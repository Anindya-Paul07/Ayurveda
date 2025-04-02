/**
 * Logger utility to conditionally log messages based on environment
 * Suppresses logs during test environment to reduce clutter in test output
 */

// Check if we're running in a test environment
const isTest = process.env.NODE_ENV === 'test';

/**
 * Logger object with methods that conditionally log based on environment
 */
const logger = {
  /**
   * Log general messages
   * @param {...any} args - Arguments to pass to console.log
   */
  log: (...args) => {
    if (!isTest) console.log(...args);
  },
  
  /**
   * Log informational messages
   * @param {...any} args - Arguments to pass to console.info
   */
  info: (...args) => {
    if (!isTest) console.info(...args);
  },
  
  /**
   * Log error messages
   * @param {...any} args - Arguments to pass to console.error
   */
  error: (...args) => {
    if (!isTest) console.error(...args);
  },
  
  /**
   * Log warning messages
   * @param {...any} args - Arguments to pass to console.warn
   */
  warn: (...args) => {
    if (!isTest) console.warn(...args);
  }
};

export default logger;