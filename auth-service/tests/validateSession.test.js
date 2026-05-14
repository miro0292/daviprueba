jest.mock('../src/services/redisService');

const httpMocks = require('node-mocks-http');
const validateSession = require('../src/middleware/validateSession');
const redisService = require('../src/services/redisService');

describe('Middleware - validateSession', () => {
  it('rechaza petición sin sessionId', async () => {
    const req = httpMocks.createRequest({ headers: {} });
    const res = httpMocks.createResponse();
    await validateSession(req, res, jest.fn());
    expect(res.statusCode).toBe(401);
    expect(res._getJSONData().error_code).toBe('SESSION_MISSING');
  });

  it('rechaza sesión expirada o inexistente', async () => {
    redisService.getSession.mockResolvedValue(null);
    const req = httpMocks.createRequest({ headers: { 'x-session-id': 'expired-id' } });
    const res = httpMocks.createResponse();
    await validateSession(req, res, jest.fn());
    expect(res.statusCode).toBe(401);
    expect(res._getJSONData().error_code).toBe('SESSION_EXPIRED');
  });

  it('inyecta sessionData y llama next() cuando la sesión es válida', async () => {
    const sessionData = { userId: 'uuid-1', username: 'juanperez' };
    redisService.getSession.mockResolvedValue(sessionData);
    const req = httpMocks.createRequest({ headers: { 'x-session-id': 'valid-id', 'x-trace-id': 'trace-1' } });
    const res = httpMocks.createResponse();
    const next = jest.fn();
    await validateSession(req, res, next);
    expect(next).toHaveBeenCalledTimes(1);
    expect(req.sessionData).toEqual(sessionData);
  });
});
