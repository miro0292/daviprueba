const winston = require('winston');
const { serviceName, logLevel } = require('../config/env');

const maskValue = (value) => {
  if (!value) return '-';
  return String(value).slice(0, 4) + '***';
};

const structuredFormat = winston.format.printf((info) => {
  const entry = {
    timestamp: new Date().toISOString(),
    level: info.level.toUpperCase(),
    service: serviceName,
    traceId: info.traceId || '-',
    sessionId: maskValue(info.sessionId),
    operation: info.operation || '-',
    message: info.message,
    status: info.status || '',
    durationMs: info.durationMs ?? null,
    httpStatus: info.httpStatus ?? null,
    errorCode: info.errorCode ?? null,
  };
  return JSON.stringify(entry);
});

const logger = winston.createLogger({
  level: logLevel,
  format: winston.format.combine(
    winston.format.errors({ stack: true }),
    structuredFormat
  ),
  transports: [new winston.transports.Console()],
});

module.exports = logger;
