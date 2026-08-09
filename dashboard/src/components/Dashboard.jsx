import { useEffect, useState, useCallback } from 'react';
import { getLatestMetrics } from '../api';
import './Dashboard.css';

const POLL_INTERVAL_MS = 30_000;

function fmt(value) {
  return value == null ? '—' : value;
}
function fmtPct(value) {
  return value == null ? '—' : `${value.toFixed(1)}%`;
}
function fmtBytes(bytes) {
  return bytes == null ? '—' : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
function fmtMs(ms) {
  return ms == null ? '—' : `${Math.round(ms)} ms`;
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState([]);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchMetrics = useCallback(async () => {
    try {
      const data = await getLatestMetrics();
      setMetrics(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
    const id = setInterval(fetchMetrics, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [fetchMetrics]);

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <h1>Ops Dashboard</h1>
        {lastUpdated && <span>Updated {lastUpdated.toLocaleTimeString()}</span>}
      </header>

      {loading && <p>Loading metrics…</p>}
      {error && (
        <p className="dashboard__error">
          Can't reach the ops API. Check that `ops-api` is running.
        </p>
      )}

      {!loading && !error && (
        <table className="dashboard__table">
          <thead>
            <tr>
              <th>Container</th>
              <th>Memory</th>
              <th>CPU</th>
              <th>Queue</th>
              <th>PG conn</th>
              <th>Redis mem</th>
              <th>Latency</th>
              <th>Errors</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m) => (
              <tr key={m.container}>
                <td>{m.container}</td>
                <td>{fmtPct(m.mem_pct)}</td>
                <td>{fmtPct(m.cpu_pct)}</td>
                <td>{fmt(m.queue_depth)}</td>
                <td>{fmt(m.pg_connections)}</td>
                <td>{fmtBytes(m.redis_mem_bytes)}</td>
                <td>{fmtMs(m.gateway_latency_ms)}</td>
                <td className={m.error_count > 0 ? 'dashboard__cell--error' : ''}>
                  {fmt(m.error_count)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}