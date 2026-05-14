// ============================================================
// Parcours 1 : Inscription + Login — DR-27 (Final Fix)
// ============================================================

describe('Parcours 1 : Inscription & Connexion', () => {
  let userFixture;

  before(() => {
    cy.fixture('users').then((data) => {
      userFixture = data.testUser;
    });
  });

  it('1.1 — Inscription complète', () => {
    const ts = Date.now();
    const uniqueEmail = `test_${ts}@example.com`;
    const uniqueUsername = `user_${ts}`;

    cy.visit('/auth/register');

    cy.get('#username', { timeout: 20000 }).should('be.visible').type(uniqueUsername);
    cy.get('#full_name').type(userFixture.full_name);
    cy.get('#email').type(uniqueEmail);
    cy.get('#password').type(userFixture.password);
    cy.get('#confirmPassword').type(userFixture.confirmPassword);

    cy.get('button[type="submit"]').click();

    // Le composant register redirige vers '/' (HomePage) après création réussie.
    // NB : le backend /auth/register ne renvoie pas de token ; la connexion
    // doit être faite séparément via /auth/login (couvert par 1.3).
    cy.location('pathname', { timeout: 25000 }).should('eq', '/');
  });

  it('1.2 — Logout', () => {
    cy.registerUser().then((user) => {
      cy.login(user.email, user.password);
      cy.visit('/restaurants');

      cy.contains('button', 'Logout', { timeout: 15000 }).click({ force: true });
      cy.contains('Sign In', { timeout: 15000 }).should('be.visible');
    });
  });

  it('1.3 — Login', () => {
    cy.registerUser().then((user) => {
      cy.visit('/auth/login');

      cy.get('#email', { timeout: 15000 }).should('be.visible').type(user.email);
      cy.get('#password').type(user.password);

      cy.get('button[type="submit"]').click();

      cy.get('.nav-user', { timeout: 20000 }).should('contain', 'Welcome');
    });
  });
});
