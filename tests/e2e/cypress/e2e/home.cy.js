describe('Page d\'accueil', () => {
  it('doit se charger correctement', () => {
    // La baseUrl est déjà configurée dans cypress.config.js (http://localhost:4200)
    cy.visit('/');
    
    // Test trivial pour vérifier que la page ne renvoie pas d'erreur
    cy.url().should('include', '/');
  });
});
