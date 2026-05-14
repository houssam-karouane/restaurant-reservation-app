// ============================================================
// Parcours 1 : Inscription + Login — DR-27 (Final Fix)
// ============================================================

describe('Parcours 1 : Inscription & Connexion', () => {
  let user;

  before(() => {
    cy.fixture('users').then((data) => {
      user = data.testUser;
    });
  });

  it('1.1 — Inscription complète', () => {
    const uniqueEmail = `test_${Date.now()}@example.com`;
    const uniqueUsername = `user_${Date.now()}`;
    
    // Aller directement sur la page (maintenant que le 404 est fixé)
    cy.visit('/auth/register');
    
    cy.get('#username', { timeout: 20000 }).should('be.visible').type(uniqueUsername);
    cy.get('#full_name').type(user.full_name);
    cy.get('#email').type(uniqueEmail);
    cy.get('#password').type(user.password);
    cy.get('#confirmPassword').type(user.confirmPassword);

    cy.writeFile('tests/e2e/cypress/fixtures/last_user_tmp.json', { 
      email: uniqueEmail,
      username: uniqueUsername 
    });

    cy.get('button[type="submit"]').click();

    // VERIFICATION SANS SLASH FINAL
    cy.url({ timeout: 25000 }).should('include', '/restaurants');
  });

  it('1.2 — Logout', () => {
    // S'assurer qu'on est connecté (peut-être via un visit direct si besoin)
    cy.visit('/restaurants');
    
    // Utiliser un sélecteur plus générique si .btn-logout est capricieux
    cy.get('button', { timeout: 15000 }).contains('Logout').click({ force: true });

    cy.contains('Sign In', { timeout: 15000 }).should('be.visible');
  });

  it('1.3 — Login', () => {
    cy.readFile('tests/e2e/cypress/fixtures/last_user_tmp.json').then((lastUser) => {
      cy.visit('/auth/login');

      cy.get('#email', { timeout: 15000 }).should('be.visible').type(lastUser.email);
      cy.get('#password').type('TestPassword123!');

      cy.get('button[type="submit"]').click();

      cy.get('.nav-user', { timeout: 20000 }).should('contain', 'Welcome');
    });
  });
});
