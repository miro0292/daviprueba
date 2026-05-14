import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import api from '../api/axios';
import { MovementsResponse, MovementItem } from '../types';

const PAGE_SIZE = 10;

export default function Movements() {
  const navigate = useNavigate();
  const [data, setData]       = useState<MovementsResponse | null>(null);
  const [page, setPage]       = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');

  useEffect(() => {
    setLoading(true);
    api.get<MovementsResponse>(`/movements?page=${page}&page_size=${PAGE_SIZE}`)
      .then((res) => setData(res.data))
      .catch((err) => setError(err.friendlyMessage || 'Error al cargar movimientos'))
      .finally(() => setLoading(false));
  }, [page]);

  function fmt(n: number) {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n);
  }

  function fmtDate(iso: string) {
    return new Date(iso).toLocaleDateString('es-CO', {
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    });
  }

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1;

  return (
    <Layout>
      <div className="page-header">
        <button className="btn btn-secondary" onClick={() => navigate('/home')} style={{ padding: '0.4rem 0.9rem' }}>
          ← Volver
        </button>
        <h1>Mis movimientos</h1>
      </div>

      <div className="card">
        {error && <div className="alert alert-error">{error}</div>}

        {loading ? (
          <div className="spinner" />
        ) : !data || data.movements.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#94a3b8', padding: '2rem 0' }}>
            No tienes movimientos aún.
          </p>
        ) : (
          <>
            <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '1rem' }}>
              {data.total} movimiento{data.total !== 1 ? 's' : ''} en total
            </p>
            <ul className="movements-list">
              {data.movements.map((m: MovementItem) => (
                <li key={m.id} className="movement-item">
                  <div className="movement-type">
                    <div className={`movement-badge ${m.type === 'DEBITO' ? 'badge-debito' : 'badge-credito'}`}>
                      {m.type === 'DEBITO' ? '↓' : '↑'}
                    </div>
                    <div className="movement-info">
                      <p>{m.type === 'DEBITO' ? 'Transferencia enviada' : 'Transferencia recibida'}</p>
                      <span>{fmtDate(m.created_at)}</span>
                    </div>
                  </div>
                  <div className="movement-right">
                    <p className={`movement-amount ${m.type === 'DEBITO' ? 'amount-debito' : 'amount-credito'}`}>
                      {m.type === 'DEBITO' ? '-' : '+'}{fmt(m.amount)}
                    </p>
                    <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                      Saldo: {fmt(m.balance_after)}
                    </span>
                  </div>
                </li>
              ))}
            </ul>

            {totalPages > 1 && (
              <div className="pagination">
                <button
                  className="page-btn"
                  disabled={page === 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  ‹ Anterior
                </button>
                <span className="page-btn active">{page} / {totalPages}</span>
                <button
                  className="page-btn"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Siguiente ›
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  );
}
