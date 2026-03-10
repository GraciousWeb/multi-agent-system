import { useState } from 'react';
import './HumanReview.css';

export default function HumanReview({ data, onSubmit, isSubmitting }) {
  const [feedback, setFeedback] = useState('');

  function handleSubmit() {
    if (!feedback.trim() || isSubmitting) return;
    onSubmit(feedback.trim());
    setFeedback('');
  }

  function quickVerdict(verdict) {
    onSubmit(verdict);
  }

  return (
    <div className="hr-card">
      <div className="hr-header">
        <span style={{ fontSize: 20 }}>🛑</span>
        <span className="hr-title">Human Review Required</span>
        <span className="hr-badge">Iteration {data.iteration}</span>
      </div>

      <p className="hr-message">{data.message}</p>

      <div className="hr-section-label">Skeptic Notes</div>
      <ul className="hr-notes">
        {(data.skeptic_notes || []).map((note, i) => (
          <li key={i}>{note}</li>
        ))}
      </ul>

      <div className="hr-field">
        <label className="hr-label">Your Feedback</label>
        <textarea
          className="hr-textarea"
          rows={3}
          value={feedback}
          onChange={e => setFeedback(e.target.value)}
          placeholder={
            'approve  →  proceed to final brief\n' +
            'reject   →  restart research\n' +
            'or type a specific search direction...'
          }
          disabled={isSubmitting}
        />
        <div className="hr-hint">
          Type <code>approve</code>, <code>reject</code>, or a comment like{' '}
          <code>Find 2026 CBN circulars on agent exclusivity</code>
        </div>
      </div>

      <div className="hr-actions">
        <button
          className="hr-btn hr-btn--primary"
          onClick={handleSubmit}
          disabled={!feedback.trim() || isSubmitting}
        >
          {isSubmitting
            ? <><span className="hr-spinner" /> Submitting…</>
            : 'Submit Review'}
        </button>
        <button
          className="hr-btn hr-btn--ghost"
          onClick={() => quickVerdict('approve')}
          disabled={isSubmitting}
        >
          ✓ Approve
        </button>
        <button
          className="hr-btn hr-btn--ghost"
          onClick={() => quickVerdict('reject')}
          disabled={isSubmitting}
        >
          ✕ Reject
        </button>
      </div>
    </div>
  );
}
