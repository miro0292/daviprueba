import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Navbar() {
  const { username, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <img src="/logo.png" alt="Daviprueba" className="navbar-logo" />
      </div>
      <div className="navbar-right">
        <span className="navbar-user">Hola, {username}</span>
        <button className="navbar-logout" onClick={handleLogout}>Cerrar sesión</button>
      </div>
    </nav>
  );
}
