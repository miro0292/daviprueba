import { createContext, useContext, useState, ReactNode } from 'react';
import api, { setSessionId } from '../api/axios';

interface AuthState {
  sessionId: string | null;
  username: string | null;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: RegisterPayload) => Promise<void>;
}

export interface RegisterPayload {
  document_number: string;
  email: string;
  phone: string;
  username: string;
  password: string;
}

const AuthContext = createContext<AuthContextType | null>(null);

// Restaura la sesión desde sessionStorage al cargar/refrescar la página
const storedSessionId = sessionStorage.getItem('sessionId');
const storedUsername  = sessionStorage.getItem('username');
if (storedSessionId) setSessionId(storedSessionId);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => ({
    sessionId:       storedSessionId,
    username:        storedUsername,
    isAuthenticated: !!storedSessionId,
  }));

  async function register(data: RegisterPayload) {
    await api.post('/auth/register', data);
  }

  async function login(username: string, password: string) {
    const res = await api.post<{ sessionId: string; username: string }>('/auth/login', {
      username,
      password,
    });
    const { sessionId, username: user } = res.data;
    sessionStorage.setItem('sessionId', sessionId);
    sessionStorage.setItem('username', user);
    setSessionId(sessionId);
    setState({ sessionId, username: user, isAuthenticated: true });
  }

  async function logout() {
    try {
      await api.post('/auth/logout');
    } finally {
      sessionStorage.removeItem('sessionId');
      sessionStorage.removeItem('username');
      setSessionId(null);
      setState({ sessionId: null, username: null, isAuthenticated: false });
    }
  }

  return (
    <AuthContext.Provider value={{ ...state, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider');
  return ctx;
}
