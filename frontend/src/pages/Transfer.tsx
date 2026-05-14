import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import api from '../api/axios';
import { TransferResponse } from '../types';

export default function Transfer() {
  const navigate = useNavigate();

  const [phone, setPhone]       = useState('');
  const [amount, setAmount]     = useState('');
  const [error, setError]       = useState('');
  const [success, setSuccess]   = useState<TransferResponse | null>(null);
  const [loading, setLoading]   = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setSuccess(null);

    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      setError('El monto debe ser mayor a cero');
      return;
    }

    setLoading(true);
    try {
      const res = await api.post<TransferResponse>('/transfers', {
        destination_phone: phone,
        amount: parsedAmount,
      });
      setSuccess(res.data);
      setPhone('');
      setAmount('');
      setTimeout(() => navigate('/home'), 2500);
    } catch (err: unknown) {
      const e = err as { friendlyMessage?: string };
      setError(e.friendlyMessage || 'Error al realizar la transferencia');
    } finally {
      setLoading(false);
    }
  }

  function fmt(n: number) {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n);
  }

  return (
    <Layout>
      <div className="page-header">
        <button className="btn btn-secondary" onClick={() => navigate('/home')} style={{ padding: '0.4rem 0.9rem' }}>
          ← Volver
        </button>
        <h1>Transferir dinero</h1>
      </div>

      <div className="card">
        {error   && <div className="alert alert-error">{error}</div>}

        {success && (
          <div className="alert alert-success">
            <strong>¡Transferencia exitosa!</strong>
            <p style={{ marginTop: '0.4rem', fontSize: '0.9rem' }}>
              Monto transferido: <strong>{fmt(success.amount)}</strong><br />
              ID de transferencia: <code style={{ fontSize: '0.8rem' }}>{success.transfer_id}</code>
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Número de teléfono destino</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Ej: 3009876543"
              pattern="\d{7,15}"
              title="Entre 7 y 15 dígitos"
              required
            />
          </div>
          <div className="form-group">
            <label>Monto a transferir (COP)</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="Ej: 50000"
              min="1"
              step="any"
              required
            />
          </div>
          <div className="transfer-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Procesando...' : 'Transferir'}
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/home')}>
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}
