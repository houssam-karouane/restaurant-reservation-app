# Monitoring production — Render + Railway (Zabbix + Vector)

Documentation de la stack de monitoring déployée pour
`restaurant-reservation-app` en production sur Render. La collecte et
le stockage des métriques sont hébergés sur Railway (plan gratuit
500 h/mois).

> ⚠️ **Démo / pédagogique** — Railway free n'offre pas de SLA de
> persistance disque. Cette stack est conçue pour démontrer
> l'observabilité bout-en-bout, pas pour absorber un incident
> production prolongé. Voir [§ Limitations connues](#limitations-connues).

---

## 1. Architecture

```
                   ┌──────────────────────────┐
                   │       Render (prod)      │
   ┌────────────┐  │                          │  Log Streams (HTTPS POST)
   │  Backend   │──┼──► stdout/stderr ─────────┼──┐
   │  FastAPI   │  │                          │  │
   └────────────┘  │  ┌────────────┐          │  │
                   │  │ Frontend   │          │  │
                   │  │ nginx+Ang. │──► logs ─┼──┤
                   │  └────────────┘          │  │
                   └──────────────────────────┘  │
                                                 │ POST /backend
                                                 │ POST /frontend
                                                 ▼
                   ┌──────────────────────────────────────┐
                   │             Railway                  │
                   │  ┌────────────────────────────────┐  │
                   │  │  Vector (aggregator)           │  │
                   │  │   • HTTP source :9000          │  │
                   │  │   • VRL transforms (parse,     │  │
                   │  │     classify, metrify)         │  │
                   │  │   • Prometheus exporter :9598  │  │
                   │  └────────────────────────────────┘  │
                   │            │  scrape /metrics        │
                   │            ▼                          │
                   │  ┌────────────────────────────────┐  │
                   │  │  Zabbix server + Postgres + UI │  │
                   │  │   • Web Scenarios (uptime)     │  │
                   │  │   • HTTP agent items (metrics) │  │
                   │  │   • Triggers + Slack webhook   │  │
                   │  └────────────────────────────────┘  │
                   └──────────────────────────────────────┘
                              │
                              ▼
                       Slack #alerts  (or email)
```

### Composants

| Composant | Hébergement | Rôle | Fichier de référence |
|---|---|---|---|
| Vector aggregator | Railway (Docker) | Reçoit les logs Render, parse, exporte Prometheus | [infra/monitoring/vector.aggregator.yaml](../../infra/monitoring/vector.aggregator.yaml) |
| Zabbix server + Web + Postgres | Railway (compose) | Stocke métriques, déclenche alertes, héberge dashboards | [infra/monitoring/railway/zabbix/docker-compose.railway.yml](../../infra/monitoring/railway/zabbix/docker-compose.railway.yml) |
| Render Log Streams | Render (UI) | Source de tous les logs | configuré manuellement, voir § 3 |
| Slack webhook | Slack | Canal d'alerte principal | [infra/monitoring/zabbix/media_webhook.yaml](../../infra/monitoring/zabbix/media_webhook.yaml) |

---

## 2. Déploiement Railway

### 2.1. Vector aggregator

1. Sur [railway.com](https://railway.com/new), créer un nouveau projet → **Deploy from GitHub repo**.
2. Choisir `restaurant-reservation-app`, branche `main`.
3. Service settings :
   - **Root directory** : `infra/monitoring/railway/vector`
   - **Builder** : Dockerfile (auto-détecté)
   - **Port exposé public** : `9000` (pour les Log Streams Render)
   - **Port additionnel privé** : `9598` (Prom exporter, scrappé par Zabbix interne)
4. Après le 1er deploy, récupérer l'URL publique Railway, ex.
   `https://vector-aggregator-production.up.railway.app`.
5. Conserver cette URL — elle sert de **destination Log Stream** côté Render.

### 2.2. Stack Zabbix

1. Nouveau service Railway → **Deploy from compose** →
   `infra/monitoring/railway/zabbix/docker-compose.railway.yml`.
2. Variables d'environnement :
   - `ZABBIX_DB_PASSWORD` : générer un secret fort.
3. Exposer publiquement le service `zabbix-web` (port 8080).
4. À la 1re connexion : `Admin` / `zabbix` → **changer immédiatement le mot de passe**.
5. Importer les templates :
   ```bash
   ZABBIX_URL=https://zabbix.up.railway.app \
   ZABBIX_USER=Admin \
   ZABBIX_PASSWORD=<nouveau> \
   ./infra/monitoring/railway/zabbix/import_templates.sh
   ```
6. Créer 2 hôtes dans Zabbix, leur attacher les templates :
   - `render-backend`  → templates *Render Uptime* + *API Metrics*
     - macro `{$RENDER_BACKEND_URL}` = URL backend Render
   - `render-frontend` → template *Render Uptime*
     - macro `{$RENDER_FRONTEND_URL}` = URL frontend Render
7. Configurer la media Slack : *Administration → Media types → Slack
   Webhook (Restaurant Reservation) → Test*. Coller l'URL réelle du
   webhook Slack dans le paramètre `webhook_url`.

---

## 3. Render Log Streams

Render → Settings du service → **Log Streams** → *Add log stream*.

| Champ | Backend | Frontend |
|---|---|---|
| **Destination** | `https://vector-aggregator.up.railway.app/backend` | `https://vector-aggregator.up.railway.app/frontend` |
| **Method** | POST | POST |
| **Format** | JSON | JSON |

À enregistrer : Render commence à streamer ~30 s après. Vérifier la
réception côté Vector : *Railway logs Vector* → on doit voir les
events JSON correspondant aux requêtes du backend.

**Test rapide** (depuis n'importe quel poste) :
```bash
curl https://restaurant-backend.onrender.com/health
# 5 secondes plus tard, dans les logs Railway de Vector :
#   {"service":"backend","http":{"method":"GET","path":"/health","status":200},...}
```

---

## 4. Dashboards Zabbix

Tous les dashboards consomment des **données réelles** (pas de mock).

### 4.1. Dashboard "Disponibilité"

| Widget | Source | Fréquence |
|---|---|---|
| Backend uptime (%) sur 24 h | Web Scenario `Backend - GET /health` | 60 s |
| Frontend uptime (%) sur 24 h | Web Scenario `Frontend - GET /` | 60 s |
| Historique pannes (timeline) | Triggers DOWN historisés | temps réel |
| SSL certificate days remaining | `ssl.cert.expiry[backend\|frontend]` | 1 h |

### 4.2. Dashboard "API Metrics"

| Widget | Source | Calcul |
|---|---|---|
| P50 / P95 / P99 latency (ms) | `http.duration[pXX]` (DEPENDENT) | Vector → quantiles → scrape Prom |
| Throughput (rps) | `http.rps[total]` | `change_per_second` sur compteur |
| Error rate 5xx (%) | `http.error_rate[5xx]` | rps[5xx] / rps[total] × 100 |
| Error rate 4xx (%) | `http.error_rate[4xx]` | idem 4xx |

### 4.3. Dashboard "Logs aggregation"

| Widget | Provient de |
|---|---|
| Top 10 endpoints (par volume) | `http.path` parsé par Vector |
| Top 10 erreurs (par message) | `level == "error"` filtré par VRL |
| Volume logs par service (par min) | `log_events_total` |

---

## 5. Alertes activées

Toutes les définitions vivent dans les templates YAML —
[`infra/monitoring/zabbix/`](../../infra/monitoring/zabbix/).
Tableau récapitulatif :

| # | Nom | Sévérité | Condition | Fenêtre | Action |
|---|-----|---------|-----------|---------|--------|
| 1 | **P99 latency > 500 ms** | Warning | `min(http.duration[p99], 5m) > 500` | 5 min soutenu | Slack #alerts |
| 2 | **Error rate 5xx > 1 %** | High | `min(http.error_rate[5xx], 5m) > 1` | 5 min soutenu | Slack #alerts |
| 3 | **Render service DOWN > 30 s** | Disaster | Web Scenario échoue (2 polls consécutifs à 60 s) | 60 s | Slack #alerts-critical |
| 4 | **/health renvoie non-200** | High | `last(web.test.rspcode[Backend - GET /health]) <> 200` | immédiat | Slack #alerts-critical |
| 5 | **SSL expire dans < 14 j** | Warning | `last(ssl.cert.expiry) < 14` | poll horaire | Slack #alerts |

> 🔄 **Webhook critique** : les triggers de sévérité ≥ *High* déclenchent en plus
> un POST vers `https://hooks.slack.com/services/...` avec payload Slack
> coloré (rouge pour Disaster/High, jaune pour Warning) — défini dans
> [media_webhook.yaml](../../infra/monitoring/zabbix/media_webhook.yaml).
> Pour la démo, le webhook URL par défaut est un placeholder ; la
> stack fonctionne identiquement avec n'importe quelle URL Incoming
> Webhook Slack.

### 5.1. Tester une alerte

```bash
# Force /health à renvoyer 500 via env var côté Render (si supporté)
# OU plus simple : arrêter temporairement le backend depuis le dashboard Render.
# → trigger #3 doit firer en moins de 2 min, message Slack reçu.
```

Pour valider P99 latency en local sans casser la prod, on peut envoyer
un événement synthétique à Vector :
```bash
curl -X POST https://vector-aggregator.up.railway.app/backend \
  -H "Content-Type: application/x-ndjson" \
  -d '{"message":"127.0.0.1 - \"GET /slow HTTP/1.1\" 200 -","timestamp":"2026-05-15T12:00:00Z","duration_ms":1200}'
```

---

## 6. Runbook (que faire quand ça pète)

### Trigger #3 — *Render service DOWN*

1. Ouvrir le dashboard Render → service concerné → onglet **Events**.
   - Crash récent ? → onglet **Logs** pour la stack trace.
   - Deploy en cours ? → attendre, Render rebascule auto.
2. Si Render dit "service running" mais Zabbix dit DOWN :
   - Cold start free-tier en cours (15 min d'inactivité réveille à
     froid, latence ~30-50 s). Le timeout step est 15 s → l'alerte
     est techniquement un faux positif sur ce cas. Voir
     [§ Limitations connues](#limitations-connues).
3. Si /health échoue mais le service répond :
   - DB Render unreachable ? `psql $DATABASE_URL` depuis le shell Render.
   - Redis Render unreachable ? Vérifier `REDIS_URL`.

### Trigger #2 — *5xx > 1 %*

1. Dashboard "Logs aggregation" → widget *Top 10 erreurs* → identifier
   le path et le message dominant.
2. Corréler avec le dernier deploy GitHub Actions (cf. workflow
   `cd.yml`).
3. Si régression confirmée : redéclencher le deploy hook de la version
   précédente via Render → Manual Deploy → choisir le commit.

### Trigger #1 — *P99 > 500 ms*

1. Vérifier le throughput simultané — si > 50 rps, c'est probablement
   du contention sur Render free (1 worker).
2. Sinon, check des endpoints lents : widget *Top 10 endpoints by P99*
   sur le dashboard API Metrics.

---

## 7. Limitations connues

| Limitation | Impact | Mitigation |
|---|---|---|
| Railway free 500 h/mois | Stack coupée après ~21 jours d'activité continue | Couper la nuit, ou prévoir bascule Fly.io |
| Pas de persistance disque garantie | Historique Zabbix perdu au restart | `import_templates.sh` rejoue les templates ; data point loss accepté pour démo |
| Render free cold-start 30-50 s | Trigger #3 peut fausser-positiver après 15 min d'inactivité | Step timeout 15 s + retry — accepté comme bruit léger en démo. Production réelle : passer Render Starter (7 $/mois) pour no-sleep |
| Cert SSL Render géré auto | Trigger #5 alerte juste avant le renouvellement auto | Tolérance 14 j ; Render renouvelle à 30 j → théoriquement jamais déclenché |

---

## 8. Références croisées

- Setup historique Zabbix (Sprint 2, mock) : [zabbix_setup.md](zabbix_setup.md)
- Best practices Zabbix : [zabbix_best_practices.md](zabbix_best_practices.md)
- Workflow CD qui déclenche les deploys monitorés : [.github/workflows/cd.yml](../../.github/workflows/cd.yml)
- Endpoint `/health` côté backend : [backend/app/main.py:58](../../backend/app/main.py#L58)
