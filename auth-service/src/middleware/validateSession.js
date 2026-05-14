const { getSession } = require('../services/redisService');
const logger = require('../utils/logger');

async function validateSession(req, res, next) {
  const sessionId = req.headers['x-session-id'];
  const traceId = req.headers['x-trace-id'] || '-';

  if (!sessionId) {
    logger.warn({ operation: 'SESSION_VALIDATE', message: 'sessionId ausente',
      traceId, status: 'FAILED', httpStatus: 401, errorCode: 'SESSION_MISSING' });
    return res.status(401).json({ error_code: 'SESSION_MISSING', message: 'Sesión requerida' });
  }

  const session = await getSession(sessionId).catch(() => null);
  if (!session) {
    logger.warn({ operation: 'SESSION_VALIDATE', message: 'Sesión no encontrada o expirada',
      traceId, sessionId, status: 'FAILED', httpStatus: 401, errorCode: 'SESSION_EXPIRED' });
    return res.status(401).json({ error_code: 'SESSION_EXPIRED', message: 'Sesión expirada o inválida' });
  }

  // Inyecta datos del usuario desde Redis — nunca del frontend
  req.sessionData = session;
  req.sessionId = sessionId;
  req.traceId = traceId;
  next();
}

module.exports = validateSession;
