import './ActivityLog.css';

function ScoutEntry({ count }) {
  return (
    <div className="al-entry" style={{ animationDelay: '0ms' }}>
      <div className="al-icon al-icon--scout">🔍</div>
      <div className="al-body">
        <div className="al-label al-label--scout">Scout</div>
        <div className="al-msg">
          Found <strong>{count}</strong> new piece{count !== 1 ? 's' : ''} of intel.
        </div>
      </div>
    </div>
  );
}

function SkepticEntry({ is_satisfactory, follow_up_queries }) {
  return (
    <div className="al-entry">
      <div className={`al-icon ${is_satisfactory ? 'al-icon--pass' : 'al-icon--fail'}`}>
        {is_satisfactory ? '✅' : '⚠️'}
      </div>
      <div className="al-body">
        <div className={`al-label ${is_satisfactory ? 'al-label--pass' : 'al-label--fail'}`}>
          Skeptic · {is_satisfactory ? 'Pass' : 'Fail'}
        </div>
        <div className="al-msg">
          {is_satisfactory
            ? 'Research verified. Escalating to human review.'
            : 'Audit failed. Generating follow-up queries.'}
        </div>
        {!is_satisfactory && follow_up_queries?.length > 0 && (
          <div className="al-followups">
            {follow_up_queries.map((q, i) => (
              <div key={i} className="al-followup-item">{q}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ActivityLog({ logs }) {
  if (!logs.length) return null;

  return (
    <div className="al-card">
      <div className="al-title">Agent Activity</div>
      <div className="al-list">
        {logs.map((log, i) => {
          if (log.type === 'scout')   return <ScoutEntry   key={i} {...log} />;
          if (log.type === 'skeptic') return <SkepticEntry key={i} {...log} />;
          return null;
        })}
      </div>
    </div>
  );
}
