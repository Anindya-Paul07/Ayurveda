/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  theme: {
    extend: {
      colors: {
        primary: '#3a5a40',
        secondary: '#588157',
        accent: '#a3b18a',
        light: '#dad7cd',
        dark: '#1a1a1a',
        'text-light': '#f8f9fa'
      }
    }
  },
  plugins: []
}
