import './IntelBrief.css';

function StoryCard({ story }) {
  const pct = (story.impact_score / 10) * 100;
  let hostname = '';
  try { hostname = new URL(story.source_url).hostname; } catch (_) {}

  return (
    <div className="ib-story">
      <div className="ib-story-meta">
        <span className="ib-category">{story.category}</span>
        <span className="ib-company">{story.company_name}</span>
        <div className="ib-impact">
          <div className="ib-impact-bar">
            <div className="ib-impact-fill" style={{ width: `${pct}%` }} />
          </div>
          <span className="ib-impact-num">Impact {story.impact_score}/10</span>
        </div>
      </div>

      <p className="ib-summary">{story.summary}</p>

      <div className="ib-story-footer">
        {story.funding_amount && (
          <span className="ib-funding">💰 {story.funding_amount}</span>
        )}
        {story.source_url && (
          <a
            className="ib-source"
            href={story.source_url}
            target="_blank"
            rel="noreferrer"
          >
            {hostname}
          </a>
        )}
      </div>
    </div>
  );
}

export default function IntelBrief({ brief, onReset }) {
  const score = brief.confidence_score
    ? (brief.confidence_score * 10).toFixed(1)
    : '—';

  return (
    <div className="ib-card">
      <div className="ib-card-title">Final Intelligence Brief</div>

      <div className="ib-header">
        <h2 className="ib-headline">{brief.headline}</h2>
        <div className="ib-score-ring">
          <div className="ib-score-value">{score}</div>
          <div className="ib-score-label">Confidence</div>
        </div>
      </div>

      <div className="ib-section-label">Regulatory Radar</div>
      <ul className="ib-radar">
        {(brief.regulatory_radar || []).map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>

      <div className="ib-section-label">Top Stories</div>
      <div className="ib-stories">
        {(brief.top_stories || []).map((story, i) => (
          <StoryCard key={i} story={story} />
        ))}
      </div>

      <div className="ib-section-label" style={{ marginTop: 24 }}>Verified Red Flags</div>
      <div className="ib-flags">
        {(brief.skeptic_notes || []).map((note, i) => (
          <div key={i} className="ib-flag">{note}</div>
        ))}
      </div>

      <button className="ib-reset-btn" onClick={onReset}>
        ↺ New Research Mission
      </button>
    </div>
  );
}
