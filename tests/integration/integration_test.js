const axios = require('axios');

async function testBackend() {
  try {
    console.log('DEBUG: Initiating request to http://localhost:8080/api/health');
    const response = await axios.get('http://localhost:8080/api/health');
    console.log('DEBUG: Received response with status:', response.status);
    console.log('DEBUG: Response headers:', JSON.stringify(response.headers));
    console.log('DEBUG: Response body:', JSON.stringify(response.data));
    if (response.data.status === 'ok') {
      console.log('Backend health check passed.');
    } else {
      throw new Error('Unexpected response from /api/health');
    }
  } catch (error) {
    throw new Error('Backend health check failed: ' + error.message);
  }
}

async function testFrontend() {
  try {
    console.log('DEBUG: Initiating request to http://localhost:8080');
    const response = await axios.get('http://localhost:8080');
    console.log('DEBUG: Received response with status:', response.status);
    console.log('DEBUG: Response headers:', JSON.stringify(response.headers));
    console.log('DEBUG: Response body (first 500 chars):', response.data.substring(0, 500));
    if (response.data && response.data.includes('Ayurveda Health Assistant')) {
      console.log('Frontend load test passed.');
    } else {
      throw new Error('Expected content not found in frontend response.');
    }
  } catch (error) {
    throw new Error('Frontend load test failed: ' + error.message);
  }
}

(async () => {
  try {
    await testBackend();
    await testFrontend();
    console.log('Integration Test Passed: Frontend and Backend are connected properly.');
    process.exit(0);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
})();
