# Configuration et Déploiement de Zabbix (Sprint 2)

Ce document décrit la mise en place de la stack de monitoring Zabbix pour l'application Restaurant Reservation.

## Architecture Zabbix

L'infrastructure de monitoring s'appuie sur quatre services Docker:
- **zabbix-db** : Base de données PostgreSQL dédiée à Zabbix.
- **zabbix-server-pgsql** : Serveur Zabbix principal qui collecte les données (Port 10051).
- **zabbix-web-nginx-pgsql** : Interface web de Zabbix (Port 8080).
- **zabbix-agent** : Agent Zabbix pour monitorer les hôtes et conteneurs.

---

## 1. Mocks des Dashboards

Pour le Sprint 2, nous préparons 3 tableaux de bord principaux pour assurer une observabilité complète :

### Dashboard 1 : Infrastructure
*Aperçu des ressources de l'hôte Docker et des conteneurs.*

| Métrique | Description |
|---|---|
| **CPU Usage** | Charge processeur globale de l'hôte et par conteneur (%) |
| **RAM Usage** | Mémoire allouée et disponible (Mo / %) |
| **Disk Usage** | Espace disque utilisé sur les volumes persistants |

### Dashboard 2 : API Metrics (Mock)
*Surveillance des performances de l'API Backend.*

| Métrique | Description |
|---|---|
| **Latence Requêtes** | Temps de réponse moyen et P99 des appels API |
| **Taux d'erreur** | Pourcentage de requêtes en statut 4xx et 5xx |
| **Throughput** | Nombre de requêtes HTTP par seconde (RPS) |

### Dashboard 3 : Database
*Performances et santé de la base de données PostgreSQL principale.*

| Métrique | Description |
|---|---|
| **Connexions** | Nombre de connexions actives au pool PostgreSQL |
| **Queries/sec** | Taux de requêtes lues/écrites par seconde |
| **Locks** | Nombre de verrous (locks) actifs pouvant causer des deadlocks |

---

## 2. Capture des Dashboards (Mock)

*Note: En attendant la collecte des données réelles, voici une représentation visuelle des dashboards cibles.*

**[ Infrastructure Overview ]**
```text
+-----------------------+ +-----------------------+ +-----------------------+
| CPU Usage (Host)      | | RAM Usage (Host)      | | Disk Usage (Host)     |
| [||||||||  ] 45%      | | [||||||||||| ] 65%    | | [|||||      ] 30%     |
+-----------------------+ +-----------------------+ +-----------------------+
| Active Containers: 8                                                    |
+-------------------------------------------------------------------------+
```

**[ API Performance ]**
```text
+-----------------------+ +-----------------------+ +-----------------------+
| Error Rate (5xx)      | | Avg Latency           | | P99 Latency           |
|  1.2%                 | |  120 ms               | |  450 ms               |
+-----------------------+ +-----------------------+ +-----------------------+
```

---

## 3. Liste des Métriques Cibles

L'agent Zabbix (et via des requêtes HTTP/JMX) devra remonter les métriques suivantes en priorité :
1. `system.cpu.util` - Utilisation CPU
2. `vm.memory.size[available]` - Mémoire disponible
3. `vfs.fs.size[/,pused]` - Utilisation Disque racine
4. `net.tcp.service[http,localhost,8000]` - Statut de l'API Backend
5. `pgsql.connections` - Connexions PostgreSQL
6. `pgsql.queries` - Requêtes/sec PostgreSQL

---

## 4. Templates d'Alertes (Définies)

Les déclencheurs (triggers) suivants ont été définis (ils seront activés dans une phase ultérieure) :

1. 🔴 **High CPU usage** : `system.cpu.util > 80%` pendant 5 minutes.
2. 🔴 **Container down** : Un des conteneurs critiques (backend, frontend, postgres) ne répond plus.
3. 🟠 **DB connection pool > 80%** : Les connexions actives à la base de données dépassent 80% de la limite configurée.
4. 🟠 **API latency P99 > 500ms** : La latence au 99ème centile dépasse 500ms, indiquant un ralentissement de l'application.
