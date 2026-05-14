import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import api from '../api/axios';
import { BalanceResponse } from '../types';

export default function Home() {
  const navigate = useNavigate();
  const [balance, setBalance]   = useState<BalanceResponse | null>(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState('');

  useEffect(() => {
    api.get<BalanceResponse>('/accounts/balance')
      .then((res) => setBalance(res.data))
      .catch((err) => setError(err.friendlyMessage || 'Error al cargar el saldo'))
      .finally(() => setLoading(false));
  }, []);

  function fmt(n: number) {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n);
  }

  return (
    <Layout>
      <div className="balance-card" style={{ marginBottom: '1.5rem' }}>
        <p className="balance-label">Saldo disponible</p>
        {loading ? (
          <div className="spinner" style={{ borderTopColor: 'white' }} />
        ) : error ? (
          <p style={{ color: '#fca5a5', marginTop: '0.5rem' }}>{error}</p>
        ) : (
          <>
            <p className="balance-amount">{fmt(balance?.balance ?? 0)}</p>
            <p className="balance-currency">{balance?.currency ?? 'COP'} · Cuenta {balance?.account_status}</p>
          </>
        )}
      </div>

      <div className="card">
        <h2 className="card-title">Acciones rápidas</h2>
        <div className="quick-actions">
          <button className="action-btn" onClick={() => navigate('/transfer')}>
            <div className="action-icon">↗</div>
            Transferir
          </button>
          <button className="action-btn" onClick={() => navigate('/movements')}>
            <div className="action-icon">≡</div>
            Movimientos
          </button>
        </div>
      </div>
    </Layout>
  );
}
