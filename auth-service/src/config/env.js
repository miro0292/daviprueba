require('dotenv').config();

function required(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Variable de entorno requerida no definida: ${name}`);
  return value;
}

module.exports = {
  port: parseInt(process.env.PORT || '3000', 10),
  serviceName: process.env.SERVICE_NAME || 'auth-service',
  logLevel: process.env.LOG_LEVEL || 'info',

  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD || undefined,
  },

  session: {
    encryptionKey: required('SESSION_ENCRYPTION_KEY'),
    ttlSeconds: parseInt(process.env.SESSION_TTL_SECONDS || '1800', 10),
  },

  coreUsuariosUrl: process.env.CORE_USUARIOS_URL || 'http://localhost:5001',

  circuitBreaker: {
    timeoutMs: parseInt(process.env.CB_TIMEOUT_MS || '5000', 10),
    errorThresholdPercentage: parseInt(process.env.CB_ERROR_THRESHOLD || '50', 10),
    resetTimeoutMs: parseInt(process.env.CB_RESET_TIMEOUT_MS || '30000', 10),
    maxRetries: parseInt(process.env.CB_MAX_RETRIES || '3', 10),
    retryDelayMs: parseInt(process.env.CB_RETRY_DELAY_MS || '1000', 10),
  },
};
