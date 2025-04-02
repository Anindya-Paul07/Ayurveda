// ***********************************************************
// This is a support file for Cypress E2E testing
// You can read more here: https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
// import './commands'
import './logger.js'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// You can add global overrides or imports here
// For example, you may want to ignore uncaught exceptions:
// Cypress.on('uncaught:exception', (err, runnable) => {
//   // returning false here prevents Cypress from failing the test
//   return false
// })

// Example of adding a custom command:
// Cypress.Commands.add('login', (email, password) => {
//   cy.visit('/login')
//   cy.get('#email').type(email)
//   cy.get('#password').type(password)
//   cy.get('form').submit()
// })

// You can also create custom queries:
// Cypress.Commands.addQuery('getByTestId', (testId) => {
//   const getFn = cy.now('get', `[data-testid=${testId}]`)
//   return () => getFn()
// })
