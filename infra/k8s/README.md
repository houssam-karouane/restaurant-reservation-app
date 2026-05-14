# Déploiement Kubernetes — restaurant-reservation-app

Manifests pour déployer la stack sur **kind**, **minikube** ou tout cluster Kubernetes ≥ 1.25.

## Architecture

```
                 ┌─────────────────┐
   Internet ───▶ │ Ingress NGINX   │
                 │  / → frontend   │
                 │  /api → backend │
                 └────┬──────────┬─┘
                      │          │
              ┌───────▼──┐  ┌───▼────────┐
              │ frontend │  │  backend   │
              │ (2 rep.) │  │  (2 rep.)  │
              │ nginx 80 │  │ fastapi 8k │
              └──────────┘  └─┬────────┬─┘
                              │        │
                       ┌──────▼─┐  ┌──▼────┐
                       │postgres│  │ redis │
                       │  STS   │  │ Deply │
                       └────────┘  └───────┘
```

## Fichiers

| Fichier | Rôle |
|---|---|
| `namespace.yaml` | Namespace `restaurant-app` |
| `configmaps.yaml` | Variables d'env non sensibles (POSTGRES_USER, POSTGRES_DB, REDIS_URL, ENVIRONMENT) |
| `secrets.yaml` | `SECRET_KEY` + `POSTGRES_PASSWORD` (base64 démo — **à remplacer en prod**) |
| `postgres-statefulset.yaml` | StatefulSet PostgreSQL + headless Service + PVC 2 Gi |
| `redis-deployment.yaml` | Deployment Redis + Service |
| `backend-deployment.yaml` | Deployment FastAPI 2 replicas, probes `/health`, rolling update |
| `backend-service.yaml` | Service ClusterIP `backend:8000` |
| `frontend-deployment.yaml` | Deployment Angular+nginx 2 replicas, probes `/` |
| `frontend-service.yaml` | Service ClusterIP `frontend:80` |
| `ingress.yaml` | Ingress NGINX, `/api` → backend, `/` → frontend |

## Prérequis

- `kubectl` connecté à un cluster (`kubectl cluster-info`)
- **Ingress NGINX Controller** installé :
  - kind : `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml`
  - minikube : `minikube addons enable ingress`

## Images locales

Les manifests référencent `restaurant-backend:latest` et `restaurant-frontend:latest`. Avec `imagePullPolicy: Always`, Kubernetes tente toujours de tirer ces images depuis un registry. Pour le dev local :

### kind

```bash
# Build
docker build -t restaurant-backend:latest ./backend
docker build -t restaurant-frontend:latest ./frontend

# Charger dans le cluster kind
kind load docker-image restaurant-backend:latest
kind load docker-image restaurant-frontend:latest
```

Note : avec `imagePullPolicy: Always`, l'image chargée sera quand même utilisée à condition qu'aucun registry distant ne réponde au pull. Si vous voulez garantir l'utilisation de l'image locale, passez en `imagePullPolicy: IfNotPresent`.

### minikube

```bash
eval $(minikube docker-env)   # bash/zsh
# Powershell : minikube docker-env --shell powershell | Invoke-Expression

docker build -t restaurant-backend:latest ./backend
docker build -t restaurant-frontend:latest ./frontend
```

## Déploiement

```bash
# Tout déployer en un coup (l'ordre des fichiers est géré par k8s)
kubectl apply -f infra/k8s/

# Suivi
kubectl get pods -n restaurant-app -w

# Logs
kubectl logs -n restaurant-app -l app=backend --tail=100 -f
```

## Accès

### Avec Ingress

```bash
# Récupérer l'IP de l'ingress
kubectl get ingress -n restaurant-app

# kind : l'ingress écoute sur localhost (80/443)
# minikube : minikube ip → http://<ip>/
```

### Sans ingress (port-forward)

```bash
kubectl port-forward -n restaurant-app svc/frontend 4200:80
kubectl port-forward -n restaurant-app svc/backend 8000:8000
```

## Vérification post-deploy

```bash
# Pods Ready
kubectl get pods -n restaurant-app

# Endpoints renseignés
kubectl get endpoints -n restaurant-app

# Probes OK
kubectl describe pod -n restaurant-app -l app=backend | grep -A2 Conditions:
```

## Nettoyage

```bash
kubectl delete -f infra/k8s/
# ou
kubectl delete namespace restaurant-app
```

## Sécurité — à NE PAS oublier en prod

- `secrets.yaml` contient des valeurs **démo** base64. Régénérer avec un vrai `SECRET_KEY` et un mot de passe Postgres fort, ou utiliser un gestionnaire de secrets (Sealed Secrets, External Secrets, Vault).
- `postgres-statefulset.yaml` utilise un PVC standard avec la storage class par défaut du cluster — vérifier qu'elle est adaptée à la prod.
- Activer `NetworkPolicy` pour restreindre les communications inter-pods.
