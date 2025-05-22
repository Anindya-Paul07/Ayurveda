const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000', // Your backend server address
      changeOrigin: true,
      ws: true, // Enable WebSocket support
      pathRewrite: {
        '^/api': '', // Remove '/api' prefix when forwarding
      },
    })
  );
};
