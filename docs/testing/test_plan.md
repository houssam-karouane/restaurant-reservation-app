# Plan de Test - Application de Réservation de Restaurant

Ce document détaille la stratégie de test et la matrice des fonctionnalités à couvrir par la QA.

## 1. Objectifs
- Assurer la qualité fonctionnelle de l'application de réservation de bout en bout.
- Automatiser les tests critiques via Cypress pour le pipeline CI/CD.

## 2. Matrice des Fonctionnalités à Tester

### P1 (Critique - Sprint 2 & 3)
- **Authentification** : Inscription utilisateur, Connexion, Déconnexion.
- **Recherche** : Recherche de restaurants avec filtres (Cuisine, Prix, Note).
- **Réservation** : Création d'une réservation pour une date et heure données, avec nombre de personnes.

### P2 (Important - Sprint 2 & 3)
- **Gestion Réservation** : Modification et annulation d'une réservation existante.
- **Avis** : Dépôt d'un avis et d'une note sur un restaurant après une réservation complétée.

### P3 (Secondaire - Sprint 3)
- **Recommandations** : Vérification de l'affichage des recommandations personnalisées.
- **Profil Utilisateur** : Affichage de l'historique et des points de fidélité.

## 3. Stratégie d'Exécution
Les tests E2E seront intégrés dans les GitHub Actions. Chaque PR devra valider l'ensemble des tests P1 avant d'être mergée.
