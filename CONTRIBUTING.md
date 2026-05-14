# Guide de Contribution

## Stratégie Git (GitFlow)

- **Aucun push direct** sur `main` ou `develop`.
- Toute modification passe par une **Pull Request**.
- Le pipeline CI doit passer (vert) avant tout merge (a partir du Sprint 2).
- Une PR vers `main` requiert 1 approval, vers `develop` aucun (pour fluidite).

## Convention de nommage des branches
feature/DR-<id-jira>-<description-courte-en-kebab-case>

Exemples :
- `feature/DR-13-init-fastapi`
- `feature/DR-15-docker-compose`
- `hotfix/DR-99-fix-auth-bug`

## Convention de commit (Conventional Commits)

Format : `<type>(<scope>): <description courte> DR-<id>`

| Type | Usage |
|------|-------|
| `feat` | Nouvelle fonctionnalite |
| `fix` | Correction de bug |
| `docs` | Documentation uniquement |
| `test` | Ajout ou modification de tests |
| `ci` | Changement de pipeline CI/CD |
| `chore` | Maintenance, dependances, config |
| `refactor` | Refactor sans changement fonctionnel |
| `perf` | Amelioration de performance |
| `style` | Formatage (sans impact code) |

Exemples :
- `feat(auth): add JWT authentication DR-12`
- `fix(api): handle empty payload on /reservations DR-14`
- `ci(github-actions): add pytest job DR-17`
- `docs(architecture): add system diagram DR-9`

## Workflow d'une Pull Request

1. Creer la branche depuis `develop` a jour :
```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/DR-X-description
```
2. Coder, commiter avec le numero Jira.
3. Pousser : `git push -u origin feature/DR-X-description`
4. Ouvrir la PR sur GitHub vers `develop`.
5. Titre de la PR : `DR-X <type>(<scope>): description`.
6. Remplir la description (template auto-propose).
7. Demander une review a un coequipier.
8. Merger via "Squash and merge" pour un historique propre.
9. Glisser le ticket Jira sur "Done".

## Pre-requis local

Pour installer les dependances de dev (Black, Flake8, pytest-cov, pre-commit) :

```bash
pip install -r backend/requirements-dev.txt
```

Puis active les pre-commit hooks (a faire une fois) :

```bash
pre-commit install
```

A chaque commit, Black/Prettier/ESLint verifieront automatiquement le code.

## Approche Docker-first

Tout tourne dans des conteneurs. Tu n'as pas besoin d'installer Python ou Node localement :

```bash
docker compose up
```

Cette commande lance :
- Backend FastAPI (http://localhost:8000)
- Frontend Angular (http://localhost:4200)
- PostgreSQL (port 5432)
- Redis (port 6379)

## Bypass admin (cas exceptionnels uniquement)

Le membre HK (DevOps) peut, en tant qu''admin, contourner les rulesets dans des cas
exceptionnels (cleanup, hotfix bloquant). Toute utilisation du bypass doit :
1. Etre annoncee en daily stand-up
2. Etre documentee dans `docs/agile/incidents.md`
3. Etre suivie d''un retrait immediat du bypass
