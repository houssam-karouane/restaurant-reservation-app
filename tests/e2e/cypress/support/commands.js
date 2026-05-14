// ============================================================
// Custom Commands Cypress — DR-27
// ============================================================

const AUTH_TOKEN_KEY = 'auth_token';

// cy.login(email, password) — authenticate via API and persist the
// token across cy.visit() calls using cy.session().
// cy.login(email, password) — récupère un token via l'API et le stocke
// dans Cypress.env('authToken'). Le token est ensuite réinjecté dans
// localStorage par notre override de cy.visit ci-dessous, avant le
// chargement de l'AUT. Pas de cy.visit ici : on évite la course entre
// /users/me et le visit suivant du test.
Cypress.Commands.add('login', (email, password) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/login`,
    body: { email, password },
    headers: { 'Content-Type': 'application/json' },
  }).then(({ body }) => {
    expect(body.access_token, 'access_token returned by /auth/login').to.be.a('string').and.not
      .empty;
    Cypress.env('authToken', body.access_token);
  });
});

// Override cy.visit : si un token a été stocké via cy.login, on
// l'injecte dans localStorage AVANT le chargement de l'app pour que
// l'AuthService le voie au boot.
Cypress.Commands.overwrite('visit', (orig, url, options = {}) => {
  const token = Cypress.env('authToken');
  if (!token) {
    return orig(url, options);
  }
  const prevBeforeLoad = options.onBeforeLoad;
  return orig(url, {
    ...options,
    onBeforeLoad(win) {
      win.localStorage.setItem(AUTH_TOKEN_KEY, token);
      if (typeof prevBeforeLoad === 'function') {
        prevBeforeLoad(win);
      }
    },
  });
});

Cypress.Commands.add('logout', () => {
  window.localStorage.removeItem(AUTH_TOKEN_KEY);
});

// cy.registerUser() — creates a fresh user via the API and yields its
// credentials. Lets each test seed its own auth state instead of
// depending on prior tests.
Cypress.Commands.add('registerUser', () => {
  const ts = Date.now() + Math.floor(Math.random() * 1000);
  const user = {
    username: `cy_user_${ts}`,
    full_name: `Cypress User ${ts}`,
    email: `cy_user_${ts}@example.com`,
    password: 'TestPassword123!',
    confirmPassword: 'TestPassword123!',
  };
  return cy
    .request({
      method: 'POST',
      url: `${Cypress.env('apiUrl')}/auth/register`,
      body: {
        username: user.username,
        full_name: user.full_name,
        email: user.email,
        password: user.password,
      },
      headers: { 'Content-Type': 'application/json' },
    })
    .then(() => user);
});
