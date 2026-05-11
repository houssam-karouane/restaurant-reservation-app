# Scénarios Utilisateurs Critiques (Happy Paths)

## Scénario 1 : Le client réserve une table avec succès
1. **Étant donné** un visiteur sur la page d'accueil
2. **Quand** il clique sur "S'inscrire" et remplit le formulaire avec des informations valides
3. **Alors** il est redirigé vers son espace personnel et est connecté
4. **Et quand** il recherche "Italien" avec un prix abordable ($$)
5. **Alors** il voit une liste de restaurants correspondants
6. **Et quand** il sélectionne un restaurant et choisit la date de demain à 20h pour 2 personnes
7. **Et** il valide la réservation
8. **Alors** il reçoit un message de succès et voit la réservation dans son historique.

## Scénario 2 : Le client annule une réservation
1. **Étant donné** un utilisateur connecté avec une réservation à venir
2. **Quand** il accède à la page "Mes Réservations"
3. **Et** qu'il clique sur "Annuler" sur sa réservation
4. **Et** qu'il confirme l'annulation
5. **Alors** le statut de la réservation passe à "Annulée"
6. **Et** la table redevient disponible.

## Scénario 3 : Le client laisse un avis
1. **Étant donné** un utilisateur connecté ayant honoré une réservation
2. **Quand** il accède à l'historique de ses réservations passées
3. **Et** qu'il clique sur "Laisser un avis"
4. **Et** qu'il donne 5 étoiles et écrit un commentaire
5. **Alors** son avis est visible sur la page du restaurant
6. **Et** sa note est prise en compte dans la moyenne du restaurant.
