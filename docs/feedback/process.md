# Processus de Gestion du Feedback Utilisateur

Ce document décrit le flux de travail pour le triage et la résolution des retours utilisateurs (bugs, demandes de fonctionnalités, questions).

## 🏷️ Système de Labellisation

Nous utilisons trois catégories de labels pour organiser les tickets :

### 1. Types (`type/`)
Définit la nature du ticket.
- `type/bug` : Comportement inattendu ou erreur technique.
- `type/feature` : Demande d'amélioration ou nouvelle fonctionnalité.
- `type/question` : Demande d'information ou aide à l'utilisation.

### 2. Priorités (`priority/`)
Définit l'urgence du traitement.
- `priority/high` : À traiter immédiatement (bloquant ou critique).
- `priority/medium` : À traiter dans le sprint en cours.
- `priority/low` : Amélioration non urgente ou cosmétique.

### 3. Statuts (`status/`)
Définit l'état d'avancement dans le cycle de vie.
- `status/triage` : Nouveau ticket en attente d'analyse.
- `status/in-progress` : En cours de traitement par l'équipe.
- `status/done` : Résolu et validé.

## 🔄 Flux de Triage

1. **Réception** : Tout nouveau ticket reçoit automatiquement le label `status/triage`.
2. **Analyse** : Le responsable QA ou le Lead Dev analyse le ticket sous 24h-48h.
3. **Qualification** : 
   - Assignation du type (`type/*`).
   - Assignation de la priorité (`priority/*`).
   - Passage au statut `status/in-progress` si le ticket est retenu.
4. **Résolution** : Une fois le travail terminé et testé, le ticket passe en `status/done` et est clôturé.
