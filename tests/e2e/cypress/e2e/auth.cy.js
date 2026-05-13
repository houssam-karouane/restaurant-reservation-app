// ============================================================
// Parcours 1 : Inscription + Login — DR-27
// Routes réelles : /auth/register  /auth/login
// ============================================================

describe('Parcours 1 : Inscription & Connexion', () => {
  let user;

  before(() => {
    cy.fixture('users').then((data) => {
      user = data.testUser;
    });
  });

  it('1.1 — Inscription : remplir le formulaire et être redirigé vers /restaurants', () => {
    cy.visit('/auth/register');

    // Vérifier que la page s'affiche
    cy.get('h1').should('contain', 'Create Account');

    // Remplir le formulaire (IDs réels du HTML)
    cy.get('#username').type(user.username);
    cy.get('#full_name').type(user.full_name);
    cy.get('#email').type(user.email);
    cy.get('#password').type(user.password);
    cy.get('#confirmPassword').type(user.confirmPassword);

    // Soumettre
    cy.get('button[type="submit"]').click();

    // Vérifier la redirection vers /restaurants
    cy.url().should('include', '/restaurants');
  });

  it('1.2 — Logout : le bouton Logout doit être visible et fonctionner', () => {
    // On est connecté après l'inscription
    cy.visit('/restaurants');
    cy.get('header').should('contain', 'Welcome,');

    // Cliquer sur Logout
    cy.get('.btn-logout').click();

    // Vérifier que "Sign In" réapparaît (utilisateur déconnecté)
    cy.get('header').should('contain', 'Sign In');
  });

  it('1.3 — Login : se reconnecter et vérifier le nom dans le header', () => {
    cy.visit('/auth/login');

    // Vérifier que la page s'affiche
    cy.get('h1').should('contain', 'Welcome Back');

    // Remplir le formulaire de connexion
    cy.get('#email').type(user.email);
    cy.get('#password').type(user.password);

    // Soumettre
    cy.get('button[type="submit"]').click();

    // Vérifier que le nom apparaît dans le header
    cy.get('.nav-user').should('contain', 'Welcome,');
    cy.get('.nav-user').should(
      'satisfy',
      (el) =>
        el.text().includes(user.full_name) || el.text().includes(user.username)
    );
  });
});
