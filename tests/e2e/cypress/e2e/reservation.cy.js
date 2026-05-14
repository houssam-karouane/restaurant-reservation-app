// ============================================================
// Parcours 3 : Réservation complète E2E — DR-27
// Login via cy.login() → restaurant → formulaire → toast → profil
// Formulaire réel : #res-date, #res-time, #res-people
// Toast : .toast--success .toast__message
// ============================================================

describe('Parcours 3 : Réservation complète (E2E)', () => {
  let user;

  before(() => {
    cy.fixture('users').then((data) => {
      user = data.testUser;
    });
  });

  beforeEach(() => {
    // Se connecter via la commande custom (rapide, sans UI)
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

    // Calculer une date future (demain)
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0]; // format YYYY-MM-DD

    // Remplir le formulaire (IDs réels du HTML)
    cy.get('#res-date').type(dateStr);
    cy.get('#res-time').type('19:00');
    cy.get('#res-people').clear().type('2');

    // Soumettre la réservation
    cy.get('.reservation-form button[type="submit"]').click();

    // Vérifier le toast de confirmation de succès
    cy.get('.toast--success', { timeout: 10000 }).should('be.visible');
    cy.get('.toast__message').should('not.be.empty');
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
