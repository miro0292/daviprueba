const swaggerJsdoc = require('swagger-jsdoc');
const { serviceName } = require('../src/config/env');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Auth Service API',
      version: '1.0.0',
      description: 'Servicio de autenticación, sesiones y cifrado Redis',
    },
    components: {
      securitySchemes: {
        sessionId: {
          type: 'apiKey',
          in: 'header',
          name: 'X-Session-Id',
          description: 'sessionId obtenido al hacer login',
        },
      },
    },
  },
  apis: ['./src/routes/*.js'],
};

module.exports = swaggerJsdoc(options);
