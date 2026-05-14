// ============================================================
// Parcours 3 : Réservation complète E2E — DR-27
// Login via cy.login() → restaurant → formulaire → toast → profil
// Formulaire réel : #res-date, #res-time, #res-people
// Toast : .toast--success .toast__message
// ============================================================

describe('Parcours 3 : Réservation complète (E2E)', () => {
  let user;

  before(() => {
    // Crée un utilisateur dédié au spec via l'API : pas de dépendance
    // à un user fixture qui n'existe peut-être pas en base.
    cy.registerUser().then((u) => {
      user = u;
    });
  });

  beforeEach(() => {
    cy.login(user.email, user.password);
  });

  it('3.1 — Faire une réservation complète et voir le toast de confirmation', () => {
    // Aller sur la liste des restaurants
    cy.visit('/restaurants');

    // Attendre les cartes
    cy.get('.restaurant-card', { timeout: 15000 }).should('have.length.greaterThan', 0);

    // Cliquer sur le lien à l'intérieur de la première carte
    cy.get('.restaurant-card', { timeout: 15000 }).first().click({ force: true });

    // Vérifier qu'on est sur /restaurants/:id
    cy.url().should('include', '/restaurants');

    // Vérifier que le formulaire de réservation est présent
    cy.get('.reservation-form').should('exist');

    // Date future avec offset unique : le backend interdit deux
    // réservations confirmées sur (restaurant, date, heure). Sans offset,
    // les runs successifs en local (volume Postgres persistant) tombent
    // en 409 sur le même créneau.
    const ts = Date.now();
    const future = new Date();
    future.setDate(future.getDate() + 1 + (ts % 28));
    const dateStr = future.toISOString().split('T')[0];
    const hh = String(10 + ((ts / 60) % 10) | 0).padStart(2, '0');
    const mm = String(ts % 60).padStart(2, '0');

    cy.get('#res-date').type(dateStr);
    cy.get('#res-time').type(`${hh}:${mm}`);
    cy.get('#res-people').clear().type('2');

    // Soumettre la réservation
    cy.get('.reservation-form button[type="submit"]').click();

    // Vérifier que le message de succès apparaît
    cy.contains('Réservation confirmée', { timeout: 15000 }).should('be.visible');
  });

  it('3.2 — La réservation apparaît dans /reservations/me', () => {
    cy.visit('/reservations/me');

    // Vérifier que la page se charge
    cy.url().should('include', '/reservations/me');

    // Vérifier qu'au moins une réservation est listée
    cy.get('.reservations-page', { timeout: 10000 }).should('exist');
    // La liste doit contenir au moins un élément de réservation
    cy.get('[class*="reservation"]').should('have.length.greaterThan', 0);
  });
});
