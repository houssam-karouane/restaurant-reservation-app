# Bonnes Pratiques Zabbix pour le Projet Restaurant Reservation

Ce document décrit les bonnes pratiques pour la mise en place de Zabbix (Sprint 2 & 3) dans notre environnement conteneurisé.

## 1. Architecture de Déploiement
- **Zabbix Server en Conteneur** : Déployer le serveur Zabbix, l'interface web (Zabbix Web) et sa base de données (PostgreSQL/MySQL) via Docker Compose ou Kubernetes.
- **Zabbix Agent 2** : Préférer le `Zabbix Agent 2` car il est plus moderne, écrit en Go, et supporte nativement la supervision de Docker et PostgreSQL sans nécessiter de scripts externes complexes complexes.

## 2. Collecte de Métriques
### Métriques Conteneurs (Docker/Kubernetes)
- Superviser l'état des conteneurs (Up/Down).
- Collecter les métriques d'utilisation : CPU, RAM, IO Réseau.
- Utiliser le template officiel "Docker by Zabbix agent 2".

### Métriques Applicatives (Backend FastAPI & Frontend Angular)
- Configurer des "Web scenarios" dans Zabbix pour vérifier que les endpoints de santé (`/health`) renvoient bien un code HTTP 200.
- Surveiller le temps de réponse (latence).

### Métriques Base de Données (PostgreSQL / Redis)
- Utiliser le template "PostgreSQL by Zabbix agent 2" pour remonter le nombre de connexions, les verrous, et les performances des requêtes.
- Utiliser le template "Redis by Zabbix agent 2" pour le cache.

## 3. Gestion des Alertes (Triggers)
- **Latence** : Déclencher une alerte de type *Warning* si la latence du backend dépasse 500ms sur 3 minutes.
- **Disponibilité** : Déclencher une alerte *High* ou *Disaster* si un conteneur (ex: `postgres` ou `backend`) est down pendant plus de 2 minutes.
- **Ressources** : Alerte si l'utilisation CPU/RAM dépasse 85%.

## 4. Dashboards (Mock puis Prod)
- **Vue Opérationnelle** : Un dashboard global affichant le statut de tous les conteneurs (vert/rouge) et les ressources hôtes.
- **Vue Applicative** : Un dashboard spécifique montrant le nombre de requêtes par seconde, le taux d'erreur HTTP (5xx) et le temps de réponse.
- Garder les dashboards simples et lisibles pour que toute l'équipe (pas seulement le SRE) puisse les comprendre.

## 5. Intégration Incident
- Lier les alertes Zabbix à un canal de communication (ex: webhook vers un channel Discord ou Slack de l'équipe, simulé pour le projet).
