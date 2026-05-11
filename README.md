# Restaurant Reservation App

Application de reservation de restaurants avec recommandations personnalisees.
Projet DevOps - Pipeline CI/CD/Monitoring complet.

## Equipe

| Membre | Role |
|--------|------|
| MT | Frontend Developer (Angular) |
| ME | Backend Developer (FastAPI) |
| HK | DevOps / Lead |
| YAS | QA / Test Engineer (Cypress) |
| IM | SRE / Monitoring (Vector + Zabbix) |

## Structure du projet
restaurant-reservation-app/
├── backend/              FastAPI + SQLAlchemy + PostgreSQL
│   ├── app/
│   │   ├── api/          Endpoints REST
│   │   ├── models/       Modeles SQLAlchemy
│   │   └── core/         Config, security, utils
│   └── tests/            Tests Pytest
├── frontend/             Angular 18 + nginx
├── infra/
│   ├── docker/           Dockerfiles
│   ├── k8s/              Manifests Kubernetes
│   └── monitoring/       Config Vector + Zabbix
├── tests/
│   └── e2e/              Tests Cypress
├── docs/
│   ├── agile/            Dailies, reviews, retros
│   ├── architecture/     Diagrammes, ADRs
│   ├── design/           Maquettes UI
│   ├── monitoring/       Plans de monitoring
│   └── testing/          Plans de tests
├── .github/workflows/    Pipelines CI/CD
├── docker-compose.yml    Stack complete locale
├── README.md
└── CONTRIBUTING.md       Conventions equipe

## Stack technique

- **Frontend** : Angular 18
- **Backend** : FastAPI (Python 3.12)
- **Database** : PostgreSQL 16
- **Cache** : Redis 7
- **Conteneurisation** : Docker + Docker Compose
- **Orchestration** : Kubernetes (kind ou minikube)
- **CI/CD** : GitHub Actions
- **Deploy** : Vercel (frontend) + Kubernetes (backend)
- **Monitoring** : Vector + Zabbix
- **Tests** : Pytest, Jest, Cypress

## Demarrage rapide

```bash
# Cloner le repo
git clone https://github.com/houssam-karouane/restaurant-reservation-app.git
cd restaurant-reservation-app

# Lancer toute la stack (frontend + backend + db + redis)
docker compose up

# Acceder aux services :
# - Frontend : http://localhost:4200
# - Backend API : http://localhost:8000
# - API Docs (Swagger) : http://localhost:8000/docs
# - PostgreSQL : localhost:5432
# - Redis : localhost:6379
```

## Sprints

| Sprint | Duree | Objectif |
|--------|-------|----------|
| Sprint 1 | 1 jour | Setup & Foundations |
| Sprint 2 | 2 jours | Core Features & CI |
| Sprint 3 | 2 jours | Deploy, Monitor & Polish |

## Workflow Git

Stratégie GitFlow stricte :
- `main` : production stable (protegee, PR + 1 review obligatoire)
- `develop` : integration (protegee, PR obligatoire)
- `feature/DR-<id>-<desc>` : developpement

Voir [`CONTRIBUTING.md`](./CONTRIBUTING.md) pour les regles completes.

## Licence

MIT
