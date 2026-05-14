// Support file — chargé automatiquement avant chaque test
import './commands';

// En CI, le tout premier cy.visit du run peut échouer ECONNREFUSED
// alors que les visits suivants passent : Cypress lance Chrome avant
// que le binding TCP du frontend ne soit pleinement opérationnel
// (course IPv6/IPv4, container nginx qui finit son démarrage…).
//
// cy.request a retryOnNetworkFailure par défaut, contrairement à
// cy.visit. On l'utilise pour "réveiller" le baseUrl avant le premier
// test et absorber ce moment d'instabilité.
before(() => {
  cy.request({
    url: '/',
    retryOnNetworkFailure: true,
    timeout: 60000,
    failOnStatusCode: false,
  });
});
