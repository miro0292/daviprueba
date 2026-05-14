import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

// sessionId vive en memoria — nunca en localStorage ni cookies
let _sessionId: string | null = null;

export function setSessionId(id: string | null) {
  _sessionId = id;
}

export function getSessionId(): string | null {
  return _sessionId;
}

const api = axios.create({ baseURL: '/' });

// Inyecta sessionId y traceId en cada request
api.interceptors.request.use((config) => {
  config.headers['X-Trace-Id'] = uuidv4();
  if (_sessionId) {
    config.headers['X-Session-Id'] = _sessionId;
  }
  return config;
});

// Extrae siempre un string del cuerpo de error, sin importar la estructura
function extractMessage(data: unknown): string {
  if (!data || typeof data !== 'object') return '';
  const d = data as Record<string, unknown>;

  // { message: "..." }
  if (typeof d.message === 'string' && d.message) return d.message;

  // { detail: "..." }
  if (typeof d.detail === 'string' && d.detail) return d.detail;

  // { detail: { message: "..." } }  ← caso FastAPI con dict
  if (d.detail && typeof d.detail === 'object') {
    const detail = d.detail as Record<string, unknown>;
    if (typeof detail.message === 'string' && detail.message) return detail.message;
  }

  // { detail: [{ msg: "..." }] }  ← errores de validación FastAPI
  if (Array.isArray(d.detail)) {
    return d.detail
      .map((e: unknown) => {
        if (e && typeof e === 'object') {
          const err = e as Record<string, unknown>;
          return typeof err.msg === 'string' ? err.msg : typeof err.message === 'string' ? err.message : '';
        }
        return String(e);
      })
      .filter(Boolean)
      .join('; ');
  }

  return '';
}

// Normaliza errores de respuesta — siempre devuelve friendlyMessage como string
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const extracted = extractMessage(error.response?.data);
    const friendlyMessage = extracted || 'Error de conexión con el servidor';
    return Promise.reject({ ...error, friendlyMessage });
  }
);

export default api;
