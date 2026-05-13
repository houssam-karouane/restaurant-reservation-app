// ============================================================
// Custom Commands Cypress — DR-27
// ============================================================

/**
 * cy.login(email, password)
 * Se connecte via l'API directement (sans passer par l'UI)
 * pour gagner du temps dans les tests qui nécessitent une session.
 */
Cypress.Commands.add('login', (email, password) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/login`,
    body: { email, password },
    headers: { 'Content-Type': 'application/json' },
    failOnStatusCode: false,
  }).then((response) => {
    if (response.status === 200 && response.body.access_token) {
      // Stocker le token dans localStorage (comme le fait Angular)
      window.localStorage.setItem('access_token', response.body.access_token);
      if (response.body.user) {
        window.localStorage.setItem('current_user', JSON.stringify(response.body.user));
      }
    }
  });
});

/**
 * cy.logout()
 * Se déconnecte en nettoyant le localStorage.
 */
Cypress.Commands.add('logout', () => {
  window.localStorage.removeItem('access_token');
  window.localStorage.removeItem('current_user');
});
