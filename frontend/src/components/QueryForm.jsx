import { useState } from 'react';
import './QueryForm.css';

const MARKETS = [
  { value: 'GLOBAL', label: 'GLOBAL' },
  { value: 'NG',     label: 'Nigeria (NG)' },
  { value: 'US',     label: 'United States (US)' },
  { value: 'UK',     label: 'United Kingdom (UK)' },
  { value: 'EU',     label: 'European Union (EU)' },
];

export default function QueryForm({ onSubmit, isRunning }) {
  const [query,  setQuery]  = useState('');
  const [market, setMarket] = useState('GLOBAL');
  const [submitted, setSubmitted] = useState(null);

  function handleSubmit(e) {
    e.preventDefault();
    if (!query.trim() || isRunning) return;
    setSubmitted({ query: query.trim(), market });
    onSubmit(query.trim(), market);
  }

  return (
    <div className="qf-card">
      <div className="qf-title">New Research Mission</div>

      {submitted && isRunning && (
        <div className="qf-submitted">
          <span className="qf-submitted-label">Active Query</span>
          <span className="qf-submitted-market">{submitted.market}</span>
          <div className="qf-submitted-query">"{submitted.query}"</div>
        </div>
      )}

      {/* Hide form fields while running, show when idle */}
      {!isRunning && (
        <>
          <div className="qf-field">
            <label className="qf-label">Research Query</label>
            <input
              className="qf-input"
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="e.g. Latest CBN agent banking rules and Moniepoint's 2026 expansion"
            />
          </div>

          <div className="qf-field">
            <label className="qf-label">Target Market</label>
            <select
              className="qf-input"
              value={market}
              onChange={e => setMarket(e.target.value)}
            >
              {MARKETS.map(m => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </div>

          <button
            className="qf-btn"
            type="button"
            onClick={handleSubmit}
            disabled={!query.trim()}
          >
            Deploy Squad
          </button>
        </>
      )}

      {/* Show spinner while running */}
      {isRunning && (
        <div className="qf-running">
          <span className="qf-spinner" />
          <span style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'var(--subtext)' }}>
            Squad is running…
          </span>
        </div>
      )}
    </div>
  );
}