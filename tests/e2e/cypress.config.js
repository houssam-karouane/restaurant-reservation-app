const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    baseUrl: 'http://localhost:4200',       // Port Angular (Frontend)
    supportFile: 'cypress/support/e2e.js', // Charge les custom commands
    specPattern: 'cypress/e2e/**/*.cy.js',

    // Screenshots automatiques en cas d'échec
    screenshotOnRunFailure: true,
    screenshotsFolder: 'cypress/screenshots',

    // Vidéos enregistrées pour chaque run
    video: true,
    videosFolder: 'cypress/videos',

    // Timeouts augmentés pour la CI
    defaultCommandTimeout: 15000,
    pageLoadTimeout: 60000,
    requestTimeout: 15000,
    responseTimeout: 30000,

    // Retente automatiquement en cas de flake CI (ECONNREFUSED transitoire,
    // attente d'hydratation Angular, etc.). N'affecte pas le mode interactif.
    retries: {
      runMode: 2,
      openMode: 0,
    },
  },

  env: {
    apiUrl: 'http://localhost:8000/api/v1', // URL Backend FastAPI
  },
});
