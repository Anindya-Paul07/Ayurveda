#!/bin/sh

# Ensure script is run from the project root directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Check if we're in the project root directory, if not, change to it
if [ "$(pwd)" != "$PROJECT_ROOT" ]; then
  echo "Changing to project root directory: $PROJECT_ROOT"
  cd "$PROJECT_ROOT" || { echo "Failed to change to project root directory"; exit 1; }
fi

# Set environment variables for user-based testing
export CHAT_RELATED_QUESTION="What Ayurvedic remedies help with digestion issues?"
export CHAT_UNRELATED_QUESTION="What is the latest iPhone model?"
export DOSHA_QUIZ_SELECTIONS="thin,dry,dry,variable,irregular,warm,light,anxious,fast,hyperactive"
export WEATHER_CITY="Mumbai"
export WEATHER_COUNTRY="India"
export FOOD_RECOMMENDATION_QUERY="Recommend Ayurvedic foods for pitta dosha"

# Run backend tests
echo "Running backend tests..."
pytest ./tests/backend

# Check if the backend tests passed
if [ $? -ne 0 ]; then
  echo "Backend tests failed. Exiting."
  exit 1
fi

# Run frontend tests
echo "Running frontend tests..."
cd frontend || exit
npm test

# Check if the frontend tests passed
if [ $? -ne 0 ]; then
  echo "Frontend tests failed. Exiting."
  exit 1
fi

# Create e2e directory if not exists
mkdir -p ./tests/e2e

# Check if Cypress is installed; install if not
if [ ! -d "node_modules/cypress" ]; then
  echo "Installing Cypress for e2e testing..."
  npm install --save-dev cypress
fi

# Create Cypress test file if not exists
if [ ! -f "cypress/e2e/user_flows.cy.js" ]; then
  echo "Creating Cypress test files..."
  mkdir -p cypress/e2e
  cat > cypress/e2e/user_flows.cy.js << 'EOL'
// Cypress tests for user flows
describe('User Flows', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000')
  })

  it('Tests chat with Ayurveda-related question', () => {
    cy.contains('Chat').click()
    const relatedQuestion = Cypress.env('CHAT_RELATED_QUESTION')
    cy.get('input[placeholder*="Type your message"]').type(relatedQuestion)
    cy.get('input[placeholder*="Type your message"]').type('{enter}')
    cy.contains('Loading...', { timeout: 10000 }).should('not.exist')
    cy.contains('I apologize, but I encountered an issue').should('not.exist')
  })

  it('Tests chat with non-Ayurveda question (Google search fallback)', () => {
    cy.contains('Chat').click()
    const unrelatedQuestion = Cypress.env('CHAT_UNRELATED_QUESTION')
    cy.get('input[placeholder*="Type your message"]').type(unrelatedQuestion)
    cy.get('input[placeholder*="Type your message"]').type('{enter}')
    cy.contains('Based on my search').should('exist')
  })

  it('Tests dosha quiz with specific selections', () => {
    cy.contains('Dosha Quiz').click()
    const selections = Cypress.env('DOSHA_QUIZ_SELECTIONS').split(',')
    const optionMap = {
      'thin': 'Thin and lean, difficulty gaining weight',
      'dry': 'Dry, rough, or thin',
      'variable': 'Variable, sometimes forget to eat',
      'irregular': 'Irregular, tendency to bloat',
      'warm': 'Warm and humid, dislike cold',
      'light': 'Light, easily disturbed',
      'anxious': 'Become anxious or worried',
      'fast': 'Fast, sometimes jumps topics',
      'hyperactive': 'Hyperactive, restless'
    }
    selections.forEach(selection => {
      if (optionMap[selection]) {
        cy.contains(optionMap[selection]).click()
      }
    })
    cy.contains('Submit Quiz').click()
    cy.contains('Your Dosha:', { timeout: 10000 }).should('exist')
  })

  it('Tests weather tab with specific city and country', () => {
    cy.contains('Weather').click()
    const city = Cypress.env('WEATHER_CITY')
    const country = Cypress.env('WEATHER_COUNTRY')
    cy.get('input[placeholder*="Enter city name"]').type(city)
    cy.get('input[placeholder*="country"]').type(country)
    cy.contains('Search').click()
    cy.contains(city, { timeout: 10000 }).should('exist')
    cy.contains('Temperature:').should('exist')
    cy.contains('Humidity:').should('exist')
    cy.contains('Get Ayurvedic Recommendations').click()
    cy.contains('Personalized Recommendations:', { timeout: 10000 }).should('exist')
  })

  it('Tests food recommendation feature', () => {
    cy.contains('Recommendations').click()
    const query = Cypress.env('FOOD_RECOMMENDATION_QUERY')
    cy.get('input[placeholder*="Enter your query"]').type(query)
    cy.get('select').select('pitta')
    cy.contains('Get Recommendations').click()
    cy.contains('Recommendations:', { timeout: 10000 }).should('exist')
    cy.get('.recommendation-item').should('have.length.at.least', 1)
  })
})
EOL

  # Also create a minimal Cypress configuration file
  cat > cypress.config.js << 'EOL'
const { defineConfig } = require('cypress')
module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      config.env = { ...config.env, ...process.env }
      return config
    },
  },
})
EOL
fi

# Run e2e tests
echo "Running e2e tests..."
npx cypress run

if [ $? -ne 0 ]; then
  echo "E2E tests failed. Exiting."
  exit 1
fi

# Return to the project root
cd ..

echo "All tests passed successfully."
