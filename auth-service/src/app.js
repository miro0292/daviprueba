require('dotenv').config();
const express = require('express');
const { v4: uuidv4 } = require('uuid');
const swaggerUi = require('swagger-ui-express');
const swaggerSpec = require('../swagger/swagger');
const authRoutes = require('./routes/authRoutes');
const logger = require('./utils/logger');
const { port, serviceName } = require('./config/env');

const app = express();

app.use(express.json());

// Propaga traceId automáticamente en cada request
app.use((req, _res, next) => {
  if (!req.headers['x-trace-id']) {
    req.headers['x-trace-id'] = uuidv4();
  }
  next();
});

app.use('/auth', authRoutes);

app.use('/auth/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
app.get('/auth/openapi.json', (_req, res) => res.json(swaggerSpec));

app.get('/auth/health', (_req, res) => res.json({ status: 'UP', service: serviceName }));

// Manejo centralizado de errores
app.use((err, req, res, _next) => {
  const traceId = req.headers['x-trace-id'] || '-';
  const statusCode = err.statusCode || 500;
  const errorCode = err.errorCode || 'INTERNAL_ERROR';
  logger.error({ operation: 'ERROR_HANDLER', message: err.message, traceId,
    status: 'FAILED', httpStatus: statusCode, errorCode });
  res.status(statusCode).json({
    error_code: errorCode,
    message: err.message || 'Error interno del servidor',
    ...(err.detail && { detail: err.detail }),
  });
});

if (require.main === module) {
  app.listen(port, () => {
    logger.info({ operation: 'STARTUP', message: `${serviceName} iniciado en puerto ${port}`, status: 'UP' });
  });
}

module.exports = app;
