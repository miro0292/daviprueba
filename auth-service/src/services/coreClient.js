const axios = require('axios');
const CircuitBreaker = require('opossum');
const { coreUsuariosUrl, circuitBreaker: cbCfg } = require('../config/env');
const logger = require('../utils/logger');

const httpClient = axios.create({ baseURL: coreUsuariosUrl, timeout: cbCfg.timeoutMs });

async function callWithRetry(fn, traceId, maxRetries = cbCfg.maxRetries) {
  let lastError;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
      if (err.response && err.response.status < 500) throw err; // No reintentar errores 4xx
      if (attempt < maxRetries) {
        await new Promise((r) => setTimeout(r, cbCfg.retryDelayMs * attempt));
        logger.warn({ operation: 'RETRY', message: `Reintento ${attempt}`, traceId, errorCode: 'RETRY' });
      }
    }
  }
  throw lastError;
}

function buildCircuitBreaker(fn, name) {
  const breaker = new CircuitBreaker(fn, {
    timeout: cbCfg.timeoutMs,
    errorThresholdPercentage: cbCfg.errorThresholdPercentage,
    resetTimeout: cbCfg.resetTimeoutMs,
    name,
    // 4xx errors are business errors, not infrastructure failures — don't open the breaker
    // opossum v8 uses errorFilter (return true = filter out, don't count as failure)
    errorFilter: (err) => !!(err?.response && err.response.status < 500),
  });

  breaker.on('open', () =>
    logger.warn({ operation: 'CIRCUIT_BREAKER', message: `Circuit breaker ABIERTO: ${name}`, errorCode: 'CB_OPEN' })
  );
  breaker.on('halfOpen', () =>
    logger.warn({ operation: 'CIRCUIT_BREAKER', message: `Circuit breaker SEMI-ABIERTO: ${name}` })
  );
  breaker.on('close', () =>
    logger.info({ operation: 'CIRCUIT_BREAKER', message: `Circuit breaker CERRADO: ${name}`, status: 'RECOVERED' })
  );
  breaker.fallback(() => {
    throw { isCircuitBreakerError: true, message: `Servicio ${name} no disponible temporalmente` };
  });

  return breaker;
}

const registerBreaker = buildCircuitBreaker(
  (data, traceId) =>
    callWithRetry(
      () => httpClient.post('/core1/users/register', data, { headers: { 'X-Trace-Id': traceId } }),
      traceId
    ),
  'core-usuarios-register'
);

const loginBreaker = buildCircuitBreaker(
  (data, traceId) =>
    callWithRetry(
      () => httpClient.post('/core1/users/login', data, { headers: { 'X-Trace-Id': traceId } }),
      traceId
    ),
  'core-usuarios-login'
);

async function registerUser(data, traceId) {
  const res = await registerBreaker.fire(data, traceId);
  return res.data;
}

async function loginUser(data, traceId) {
  const res = await loginBreaker.fire(data, traceId);
  return res.data;
}

module.exports = { registerUser, loginUser };
