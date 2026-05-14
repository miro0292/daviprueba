import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    document_number: '',
    email: '',
    phone: '',
    username: '',
    password: '',
    confirm_password: '',
  });
  const [error, setError]     = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError('');
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (form.password !== form.confirm_password) {
      setError('Las contraseñas no coinciden');
      return;
    }
    setLoading(true);
    try {
      await register({
        document_number: form.document_number,
        email: form.email,
        phone: form.phone,
        username: form.username,
        password: form.password,
      });
      setSuccess('Usuario registrado exitosamente. Redirigiendo...');
      setTimeout(() => navigate('/login'), 1500);
    } catch (err: unknown) {
      const e = err as { friendlyMessage?: string };
      setError(e.friendlyMessage || 'Error al registrar usuario');
    } finally {
      setLoading(false);
    }
  }

  const fields = [
    { name: 'document_number', label: 'Número de documento', type: 'text', placeholder: 'Ej: 12345678' },
    { name: 'email',           label: 'Correo electrónico',   type: 'email', placeholder: 'correo@ejemplo.com' },
    { name: 'phone',           label: 'Número celular',        type: 'tel',   placeholder: 'Ej: 3001234567' },
    { name: 'username',        label: 'Usuario',               type: 'text',  placeholder: 'minimo 3 caracteres' },
    { name: 'password',        label: 'Contraseña',            type: 'password', placeholder: 'Mínimo 8 caracteres' },
    { name: 'confirm_password',label: 'Confirmar contraseña',  type: 'password', placeholder: 'Repite la contraseña' },
  ] as const;

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="card">
          <div className="auth-logo-wrap">
            <img src="/logo.png" alt="Daviprueba" className="auth-logo" />
          </div>
          <h1 className="card-title">Crear cuenta</h1>

          {error   && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}

          <form onSubmit={handleSubmit}>
            {fields.map((f) => (
              <div className="form-group" key={f.name}>
                <label>{f.label}</label>
                <input
                  type={f.type}
                  name={f.name}
                  value={form[f.name]}
                  onChange={onChange}
                  placeholder={f.placeholder}
                  required
                />
              </div>
            ))}
            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? 'Registrando...' : 'Crear cuenta'}
            </button>
          </form>

          <p className="auth-footer">
            ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
