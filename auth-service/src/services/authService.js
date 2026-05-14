const { v4: uuidv4 } = require('uuid');
const { saveSession, deleteSession } = require('./redisService');
const { registerUser, loginUser } = require('./coreClient');
const logger = require('../utils/logger');

async function register(body, traceId) {
  const start = Date.now();
  try {
    const result = await registerUser(body, traceId);
    logger.info({ operation: 'REGISTER', message: 'Usuario registrado', traceId,
      status: 'SUCCESS', httpStatus: 201, durationMs: Date.now() - start });
    return result;
  } catch (err) {
    _rethrow(err, 'REGISTER', traceId, start);
  }
}

async function login(body, traceId) {
  const start = Date.now();
  try {
    const userData = await loginUser({ username: body.username, password: body.password }, traceId);
    const sessionId = uuidv4();
    await saveSession(sessionId, userData);
    logger.info({ operation: 'LOGIN', message: 'Sesión creada', traceId, sessionId,
      status: 'SUCCESS', httpStatus: 200, durationMs: Date.now() - start });
    return { sessionId, username: userData.username, message: 'Login exitoso' };
  } catch (err) {
    _rethrow(err, 'LOGIN', traceId, start);
  }
}

async function logout(sessionId, traceId) {
  const start = Date.now();
  await deleteSession(sessionId);
  logger.info({ operation: 'LOGOUT', message: 'Sesión invalidada', traceId, sessionId,
    status: 'SUCCESS', httpStatus: 200, durationMs: Date.now() - start });
  return { message: 'Sesión cerrada exitosamente' };
}

function _rethrow(err, operation, traceId, start) {
  if (err.isCircuitBreakerError) {
    logger.error({ operation, message: err.message, traceId,
      status: 'FAILED', httpStatus: 503, errorCode: 'SERVICE_UNAVAILABLE', durationMs: Date.now() - start });
    const error = new Error(err.message);
    error.statusCode = 503;
    error.errorCode = 'SERVICE_UNAVAILABLE';
    throw error;
  }
  if (err.response) {
    logger.warn({ operation, message: 'Error desde core-usuarios', traceId,
      status: 'FAILED', httpStatus: err.response.status, durationMs: Date.now() - start });
    const error = new Error(err.response.data?.message || 'Error en el servicio');
    error.statusCode = err.response.status;
    error.errorCode = err.response.data?.error_code || 'UPSTREAM_ERROR';
    error.detail = err.response.data?.detail;
    throw error;
  }
  throw err;
}

module.exports = { register, login, logout };
