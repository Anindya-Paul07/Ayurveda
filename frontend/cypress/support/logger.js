// ayurveda/frontend/cypress/support/logger.js

/**
 * Custom command for consistent logging across tests
 * Logs messages both to Cypress's UI log and the browser console.
 */
Cypress.Commands.add('logStep', (message) => {
  cy.log(message);
  console.log(`[Cypress] ${message}`);
});