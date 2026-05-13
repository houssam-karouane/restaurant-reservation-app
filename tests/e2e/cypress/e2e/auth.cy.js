// ============================================================
// Parcours 1 : Inscription + Login — DR-27 (Ultra-Robust)
// ============================================================

describe('Parcours 1 : Inscription & Connexion', () => {
  let user;

  before(() => {
    cy.fixture('users').then((data) => {
      user = data.testUser;
    });
  });

  it('1.1 — Inscription : remplir le formulaire et être redirigé vers /restaurants', () => {
    const uniqueEmail = `test_${Date.now()}@example.com`;
    const uniqueUsername = `user_${Date.now()}`;
    
    cy.visit('/');
    
    // Utiliser cy.contains pour être indépendant des sélecteurs techniques instables
    cy.contains('Create Account', { timeout: 20000 }).click({ force: true });

    // Vérifier que le formulaire est là
    cy.get('#email', { timeout: 10000 }).should('be.visible');

    // Remplir le formulaire
    cy.get('#username').type(uniqueUsername);
    cy.get('#full_name').type(user.full_name);
    cy.get('#email').type(uniqueEmail);
    cy.get('#password').type(user.password);
    cy.get('#confirmPassword').type(user.confirmPassword);

    // Sauvegarder pour le test de login suivant (plus fiable que le context this)
    cy.writeFile('tests/e2e/cypress/fixtures/last_user_tmp.json', { 
      email: uniqueEmail,
      username: uniqueUsername 
    });

    // Soumettre
    cy.get('button[type="submit"]').click();

    // Vérifier la redirection
    cy.url({ timeout: 20000 }).should('include', '/restaurants');
  });

  it('1.2 — Logout : le bouton Logout doit fonctionner', () => {
    cy.visit('/restaurants');
    
    // Attendre que la session soit chargée dans le header
    cy.get('.btn-logout', { timeout: 15000 }).should('be.visible').click({ force: true });

    // Vérifier le retour à l'état déconnecté
    cy.contains('Sign In', { timeout: 10000 }).should('be.visible');
  });

  it('1.3 — Login : se reconnecter avec le compte créé', () => {
    cy.readFile('tests/e2e/cypress/fixtures/last_user_tmp.json').then((lastUser) => {
      cy.visit('/');
      cy.contains('Sign In', { timeout: 15000 }).click({ force: true });

      cy.get('#email').type(lastUser.email);
      cy.get('#password').type('TestPassword123!'); // password de users.json

      cy.get('button[type="submit"]').click();

      // Vérifier le header
      cy.get('.nav-user', { timeout: 15000 }).should('contain', 'Welcome');
    });
  });
});
