jest.mock('../src/services/redisService');
jest.mock('../src/services/coreClient');

const authService = require('../src/services/authService');
const redisService = require('../src/services/redisService');
const coreClient = require('../src/services/coreClient');

const TRACE_ID = 'test-trace-001';

const mockUser = {
  user_id: 'uuid-1',
  username: 'juanperez',
  email: 'juan@test.com',
  phone: '3001234567',
  status: 'ACTIVA',
};

describe('AuthService - register', () => {
  it('delega correctamente al core-usuarios', async () => {
    coreClient.registerUser.mockResolvedValue({ id: 'uuid-1', username: 'juanperez', status: 'ACTIVA' });
    const result = await authService.register({ username: 'juanperez', password: 'pass' }, TRACE_ID);
    expect(result.username).toBe('juanperez');
    expect(coreClient.registerUser).toHaveBeenCalledTimes(1);
  });

  it('propaga error 409 de core-usuarios', async () => {
    const axiosError = { response: { status: 409, data: { error_code: 'EMAIL_EXISTS', message: 'Email duplicado' } } };
    coreClient.registerUser.mockRejectedValue(axiosError);
    await expect(authService.register({}, TRACE_ID)).rejects.toMatchObject({ statusCode: 409 });
  });

  it('retorna error 503 cuando el circuit breaker está abierto', async () => {
    coreClient.registerUser.mockRejectedValue({ isCircuitBreakerError: true, message: 'Servicio no disponible' });
    await expect(authService.register({}, TRACE_ID)).rejects.toMatchObject({ statusCode: 503 });
  });
});

describe('AuthService - login', () => {
  beforeEach(() => jest.clearAllMocks());

  it('genera sessionId y guarda sesión cifrada en Redis', async () => {
    coreClient.loginUser.mockResolvedValue(mockUser);
    redisService.saveSession.mockResolvedValue();
    const result = await authService.login({ username: 'juanperez', password: 'Secure1234' }, TRACE_ID);
    expect(result.sessionId).toBeDefined();
    expect(result.username).toBe('juanperez');
    expect(redisService.saveSession).toHaveBeenCalledWith(
      expect.any(String),
      mockUser
    );
  });

  it('propaga error 401 de credenciales inválidas', async () => {
    const axiosError = { response: { status: 401, data: { error_code: 'INVALID_CREDENTIALS', message: 'Credenciales inválidas' } } };
    coreClient.loginUser.mockRejectedValue(axiosError);
    await expect(authService.login({ username: 'x', password: 'y' }, TRACE_ID)).rejects.toMatchObject({ statusCode: 401 });
  });
});

describe('AuthService - logout', () => {
  it('invalida la sesión en Redis', async () => {
    redisService.deleteSession.mockResolvedValue();
    const result = await authService.logout('session-id-123', TRACE_ID);
    expect(result.message).toContain('exitosamente');
    expect(redisService.deleteSession).toHaveBeenCalledWith('session-id-123');
  });
});
