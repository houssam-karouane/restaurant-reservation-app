# Restaurant Reservation App

[![CI Pipeline](https://github.com/houssam-karouane/restaurant-reservation-app/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/houssam-karouane/restaurant-reservation-app/actions/workflows/ci.yml)
[![CD Pipeline](https://github.com/houssam-karouane/restaurant-reservation-app/actions/workflows/cd.yml/badge.svg?branch=main)](https://github.com/houssam-karouane/restaurant-reservation-app/actions/workflows/cd.yml)

Application de réservation de restaurants avec recommandations personnalisées.
Projet DevOps — pipeline CI/CD complet, déploiement cloud, monitoring de production.

---

## Déploiement en production

| Service | URL | Hébergeur |
|---|---|---|
| **Frontend** (Angular SPA) | https://restaurant-frontend.onrender.com | Render Free |
| **Backend** (FastAPI) | https://restaurant-api-suqc.onrender.com | Render Free |
| **API docs** (Swagger) | https://restaurant-api-suqc.onrender.com/docs | Render Free |
| **Healthcheck** | https://restaurant-api-suqc.onrender.com/health | Render Free |

> ⚠️ Render Free met les services en veille après 15 min d'inactivité.
> Premier appel après inactivité = cold start ~30–50 s, ensuite normal.

---

## Équipe

| Membre | Rôle |
|---|---|
| MT | Frontend Developer (Angular) |
| ME | Backend Developer (FastAPI) |
| HK | DevOps / Lead |
| YAS | QA / Test Engineer (Cypress) |
| IM | SRE / Monitoring |

---

## Stack technique

| Couche | Techno |
|---|---|
| Frontend | Angular 21, RxJS, Jest, Prettier, servi par nginx en prod |
| Backend | FastAPI, Python 3.12, SQLAlchemy, Alembic |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Conteneurisation | Docker + Docker Compose |
| Orchestration locale | Kubernetes (manifests dans `infra/k8s/`) |
| CI | GitHub Actions — lint, unit tests, build Docker, Cypress E2E |
| CD | GitHub Actions — build & push GHCR, deploy hooks Render, smoke tests |
| Production | Render Free (backend + frontend, autoscale géré) |
| Monitoring | Render Metrics + Logs (natif) + UptimeRobot Free (alertes Slack) |
| Tests | Pytest (backend), Jest (frontend), Cypress 15 (E2E) |

---

## Structure du projet

```
restaurant-reservation-app/
├── backend/                  FastAPI + SQLAlchemy + PostgreSQL
│   ├── app/
│   │   ├── api/              Endpoints REST (auth, restaurants, reservations, reviews)
│   │   ├── models/           Modèles SQLAlchemy
│   │   ├── core/             Config, sécurité, JWT
│   │   └── main.py           Entry point + /health
│   └── tests/                Tests Pytest
├── frontend/                 Angular 21 + nginx
│   └── src/app/
│       ├── pages/            restaurant-detail, auth, my-reservations, …
│       └── services/         auth.service, api.service, …
├── infra/
│   ├── docker/               Dockerfiles
│   ├── k8s/                  Manifests Kubernetes (préparés, non déployés)
│   └── monitoring/           Stack Vector + Zabbix (documentée, voir docs/monitoring/alerts.md)
├── tests/
│   └── e2e/                  Tests Cypress
├── docs/
│   ├── agile/                Dailies, reviews, retros
│   ├── architecture/         Diagrammes, ADRs
│   ├── design/               Maquettes UI
│   ├── monitoring/           alerts.md (architecture monitoring actuelle)
│   └── testing/              Plans de tests
├── .github/workflows/
│   ├── ci.yml                Pipeline CI (push & PR sur develop/main)
│   └── cd.yml                Pipeline CD (push sur main → Render)
├── docker-compose.yml        Stack complète locale
├── README.md
└── CONTRIBUTING.md           Conventions équipe + GitFlow
```

---

## Démarrage rapide (local)

```bash
git clone https://github.com/houssam-karouane/restaurant-reservation-app.git
cd restaurant-reservation-app

# Stack complète (frontend + backend + postgres + redis)
docker compose up

# Endpoints exposés :
# - Frontend : http://localhost:4200
# - Backend  : http://localhost:8000
# - Swagger  : http://localhost:8000/docs
# - Postgres : localhost:5432
# - Redis    : localhost:6379
```

### Développement par service

```bash
# Backend seul
cd backend
uvicorn app.main:app --reload

# Frontend seul
cd frontend
npm install
npm start

# Tests E2E (nécessite la stack en route)
cd tests/e2e
npx cypress run --headless --browser chrome
```

---

## Tests

| Type | Outil | Localisation | Commande |
|---|---|---|---|
| Unit backend | Pytest + coverage | [backend/tests/](backend/tests/) | `pytest tests/ --cov=app` |
| Unit frontend | Jest | [frontend/src/](frontend/src/) | `npm test` |
| E2E | Cypress 15 | [tests/e2e/cypress/e2e/](tests/e2e/cypress/e2e/) | `npx cypress run` |
| Lint backend | Black + Flake8 | — | `black --check app/ && flake8 app/` |
| Lint frontend | Prettier | — | `npm run lint` |

Tous exécutés automatiquement sur chaque PR via la CI ([ci.yml](.github/workflows/ci.yml)).

---

## CI/CD

### Pipeline CI ([ci.yml](.github/workflows/ci.yml))

Déclenchée sur `push` et `pull_request` vers `develop` et `main`.

```
lint-backend ─┐
              ├─► test-backend ─┐
lint-frontend ┤                 ├─► build-images ─► e2e-tests ─► ci (status)
              └─► test-frontend ┘
```

Bloque le merge si l'un des jobs échoue.

### Pipeline CD ([cd.yml](.github/workflows/cd.yml))

Déclenchée uniquement sur `push` vers `main` (et via `workflow_dispatch` manuel).

```
build-and-push (GHCR) ─┐
                       ├─► deploy-backend  ──┐
                       └─► deploy-frontend ──┴─► smoke-tests ─► cd (status)
```

- **build-and-push** : images Docker taguées `<sha>` + `latest`, push sur `ghcr.io`
- **deploy-backend / deploy-frontend** : appel des Render Deploy Hooks + polling `/health` (mode simulation si hooks non configurés)
- **smoke-tests** : retry loop 5 × 30 s pour absorber le cold-start Render Free, échec → pipeline en erreur

#### Secrets / variables GitHub requis

| Nom | Type | Usage |
|---|---|---|
| `RENDER_DEPLOY_HOOK_BACKEND` | Secret | URL Deploy Hook du service backend Render |
| `RENDER_DEPLOY_HOOK_FRONTEND` | Secret | URL Deploy Hook du service frontend Render |
| `GHCR_TOKEN` | Secret (optionnel) | Sinon `GITHUB_TOKEN` (défaut) suffit |
| `RENDER_BACKEND_URL` | Variable | URL publique backend pour le polling/smoke |
| `RENDER_FRONTEND_URL` | Variable | URL publique frontend pour le polling/smoke |

---

## Monitoring de production

**Architecture retenue** : Render natif + UptimeRobot Free.

| Composant | Couvre |
|---|---|
| **Render Dashboard** (intégré) | Metrics infra (CPU, RAM, bandwidth, response time), logs 7 j, events deploy/crash |
| **Render Health Checks** (intégré) | Restart auto si `/health` KO |
| **Render Notifications** (email) | Deploy failed, service unhealthy, service suspended |
| **UptimeRobot Free** | Monitor `/health` toutes les 5 min, alerte Slack en cas de KO |
| **SSL** | Auto-renouvelé par Render (Let's Encrypt), aucune action requise |

La stack initialement envisagée Vector + Zabbix + Railway est **documentée comme évolution future** dans [docs/monitoring/alerts.md](docs/monitoring/alerts.md) — elle reste pertinente pour une mise en production avec SLA strict, mais n'est pas déployée car le ratio coût-opérationnel-bénéfice n'est pas justifié pour un MVP démo (Railway Free ne garantit pas la persistance des données Zabbix).

---

## Workflow Git

GitFlow strict :

| Branche | Rôle | Protection |
|---|---|---|
| `main` | Production stable | Protégée — PR + review obligatoire |
| `develop` | Intégration | Protégée — PR obligatoire |
| `feature/DR-<id>-<desc>` | Développement | Libre |
| `fix/DR-<id>-<desc>` | Correctifs urgents | Libre |
| `chore/...` | Maintenance, docs | Libre |

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les conventions de commit et la procédure complète de PR.

---

## Sprints livrés

| Sprint | Durée | Objectif | Status |
|---|---|---|---|
| Sprint 1 | 1 jour | Setup & Foundations (repo, CI initial, structure projet) | ✅ |
| Sprint 2 | 2 jours | Core Features & CI complète (auth, restaurants, réservations, tests, monitoring conçu) | ✅ |
| Sprint 3 | 2 jours | Deploy, Monitor & Polish (déploiement Render, CD pipeline, monitoring production, recommandations, reviews) | ✅ |

---

## Tickets clés (historique condensé)

| Ticket | Sujet |
|---|---|
| DR-25 | Pipeline CI initiale (lint, tests, build) |
| DR-26 | Coverage Pytest |
| DR-27 | Tests E2E Cypress |
| DR-29 | Liaison Jira ↔ commits |
| DR-30 | Manifests Kubernetes |
| DR-31 | Pipeline CD vers Render |
| DR-32 | Configuration Render (services, env, redirects, CORS) |
| DR-34 | Tests endpoint recommandations |
| DR-35 | Frontend reviews |
| DR-38 | Monitoring production (Render natif + UptimeRobot ; Vector/Zabbix documenté comme évolution) |
| DR-40 | UI polish final |

---

## Documentation détaillée

- [CONTRIBUTING.md](CONTRIBUTING.md) — Conventions équipe, commits, PR
- [docs/architecture/](docs/architecture/) — Diagrammes, ADRs
- [docs/monitoring/alerts.md](docs/monitoring/alerts.md) — Architecture monitoring + runbook + évolution future
- [docs/testing/](docs/testing/) — Plans de tests par couche
- [docs/agile/](docs/agile/) — Dailies, reviews, retros
- [infra/k8s/README.md](infra/k8s/README.md) — Déploiement Kubernetes (préparé, non déployé en prod)

---

## Licence

MIT
