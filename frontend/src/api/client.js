const BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function startRun(query, market) {
  const res = await fetch(`${BASE}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, market }),
  });
  if (!res.ok) throw new Error('Failed to start run');
  return res.json();
}

export function openStream(threadId, query, market) {
  const params = new URLSearchParams({ query, market });
  return new EventSource(`${BASE}/stream/${threadId}?${params}`);
}

export async function submitReview(threadId, feedback) {
  const res = await fetch(`${BASE}/review/${threadId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feedback }),
  });
  if (!res.ok) throw new Error('Failed to submit review');
  return res.json();
}

export function openResumeStream(threadId) {
  return new EventSource(`${BASE}/resume/${threadId}`);
}
