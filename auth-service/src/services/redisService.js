const Redis = require('ioredis');
const { redis: redisCfg, session: sessionCfg } = require('../config/env');
const { encrypt, decrypt } = require('../utils/crypto');
const logger = require('../utils/logger');

const client = new Redis({
  host: redisCfg.host,
  port: redisCfg.port,
  password: redisCfg.password || undefined,
  lazyConnect: true,
});

client.on('error', (err) => {
  logger.error({ operation: 'REDIS', message: 'Error de conexión Redis', errorCode: 'REDIS_ERROR' });
});

async function saveSession(sessionId, userData) {
  // Nunca almacenar password ni password_hash
  const safe = {
    userId: userData.user_id,
    username: userData.username,
    email: userData.email,
    phone: userData.phone,
    status: userData.status,
  };
  const encrypted = encrypt(safe);
  await client.set(`session:${sessionId}`, encrypted, 'EX', sessionCfg.ttlSeconds);
}

async function getSession(sessionId) {
  const raw = await client.get(`session:${sessionId}`);
  if (!raw) return null;
  return decrypt(raw);
}

async function deleteSession(sessionId) {
  await client.del(`session:${sessionId}`);
}

module.exports = { saveSession, getSession, deleteSession };
