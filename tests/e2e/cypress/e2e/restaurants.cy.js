// ============================================================
// Parcours 2 : Recherche restaurants avec filtres — DR-27
// Route réelle : /restaurants
// Filtre cuisine via <select id="search-cuisine">
// ============================================================

describe('Parcours 2 : Recherche restaurant avec filtres', () => {
  beforeEach(() => {
    cy.visit('/restaurants');
  });

  it('2.1 — La page affiche plusieurs cartes de restaurants', () => {
    // Attendre que les cartes se chargent
    cy.get('app-restaurant-list', { timeout: 10000 }).should('exist');
    cy.get('app-restaurant-card').should('have.length.greaterThan', 1);
  });

  it('2.2 — Appliquer le filtre cuisine "Italienne" et vérifier les résultats', () => {
    cy.fixture('restaurants').then((data) => {
      // Sélectionner "Italienne" dans le dropdown cuisine
      cy.get('#search-cuisine').select(data.filterCuisineValue);

      // Cliquer sur Search
      cy.get('.search-bar__submit').click();

      // Attendre les nouveaux résultats
      cy.get('app-restaurant-card', { timeout: 10000 }).should('have.length.greaterThan', 0);

      // Vérifier que chaque carte affiche la cuisine (insensible à la casse)
      cy.get('app-restaurant-card').each(($card) => {
        cy.wrap($card).should(($el) => {
          const text = $el.text().toLowerCase();
          const cuisine = data.filterCuisineValue.toLowerCase();
          expect(text).to.include(cuisine);
        });
      });
    });
  });

  it('2.3 — Cliquer sur une carte redirige vers /restaurants/:id', () => {
    // Attendre les cartes
    cy.get('app-restaurant-card', { timeout: 10000 }).should('have.length.greaterThan', 0);

    // Cliquer sur la première carte
    cy.get('app-restaurant-card').first().click({ force: true });

    // Vérifier la redirection vers /restaurants/:id
    cy.url().should('match', /\/restaurants\/\d+$/);
  });
});
