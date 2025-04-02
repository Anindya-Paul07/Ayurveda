// Import jest-dom's custom matchers
import '@testing-library/jest-dom';

// Polyfill for scrollIntoView for jsdom environment
if (typeof window !== 'undefined' && window.HTMLElement && !window.HTMLElement.prototype.scrollIntoView) {
  window.HTMLElement.prototype.scrollIntoView = function() {};
}