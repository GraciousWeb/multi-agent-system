import { useState, useRef } from 'react';
import { startRun, openStream, submitReview, openResumeStream } from './api/client';
import QueryForm   from './components/QueryForm';
import ActivityLog from './components/ActivityLog';
import HumanReview from './components/HumanReview';
import IntelBrief  from './components/IntelBrief';
import './styles/global.css';
import './App.css';

export default function App() {
  const [isRunning,    setIsRunning]    = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [logs,         setLogs]         = useState([]);
  const [interrupt,    setInterrupt]    = useState(null);
  const [brief,        setBrief]        = useState(null);
  const [reviewLogs,   setReviewLogs]   = useState([]);
  const [activeQuery,  setActiveQuery]  = useState(null);

  const threadIdRef = useRef(null);
  const esRef       = useRef(null);

  function handleStream(es) {
    esRef.current = es;

    es.onmessage = (e) => {
      const msg = JSON.parse(e.data);

      if (msg.type === 'scout' || msg.type === 'skeptic') {
        setLogs(prev => [...prev, msg]);
      }
      else if (msg.type === 'interrupt') {
        setInterrupt(msg);
        setIsRunning(false);
        es.close();
      }
      else if (msg.type === 'brief') {
        setBrief(msg.data);
        setIsRunning(false);
        es.close();
      }
      else if (msg.type === 'done') {
        setIsRunning(false);
        es.close();
      }
      else if (msg.type === 'error') {
        console.error('Graph error:', msg.message);
        setIsRunning(false);
        es.close();
      }
    };

    es.onerror = () => {
      setIsRunning(false);
      es.close();
    };
  }

  async function handleSubmit(query, market) {
    setActiveQuery({ query, market });
    setLogs([]);
    setInterrupt(null);
    setBrief(null);
    setReviewLogs([]);
    setIsRunning(true);

    try {
      const { thread_id } = await startRun(query, market);
      threadIdRef.current = thread_id;
      handleStream(openStream(thread_id, query, market));
    } catch (err) {
      console.error('Failed to start run:', err);
      setIsRunning(false);
    }
  }

  async function handleReview(feedback) {
    setIsSubmitting(true);

    setReviewLogs(prev => [...prev, {
      iteration:    interrupt?.iteration,
      skepticNotes: interrupt?.skeptic_notes || [],
      feedback:     feedback,
      verdict:      feedback.split()[0]?.toLowerCase(),
    }]);

    setInterrupt(null);

    try {
      await submitReview(threadIdRef.current, feedback);
      setIsRunning(true);
      handleStream(openResumeStream(threadIdRef.current));
    } catch (err) {
      console.error('Failed to submit review:', err);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleReset() {
    esRef.current?.close();
    threadIdRef.current = null;
    setLogs([]);
    setReviewLogs([]);
    setInterrupt(null);
    setBrief(null);
    setIsRunning(false);
    setActiveQuery(null); 
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  return (
    <div className="app-wrap">

      <header className="app-header">
        <div className="app-badge">
          <span className="app-badge-dot" />
          Multi-Agent · Human-in-the-Loop
        </div>
        <h1 className="app-title">
          Fintech<br /><span className="app-title-accent">Intel Squad</span>
        </h1>
        <p className="app-sub">Autonomous research · Compliance audit · Verified briefs</p>
      </header>

      {/* Query form — only when idle and no active session */}
      {!activeQuery && !brief && (
        <QueryForm onSubmit={handleSubmit} isRunning={isRunning} />
      )}

      {/* Active query banner — always visible once a run starts */}
      {activeQuery && (
        <div className="active-query-banner">
          <div className="aq-top">
            <span className="aq-label">Active Mission</span>
            <span className="aq-market">{activeQuery.market}</span>
            {isRunning && <span className="aq-spinner" />}
          </div>
          <div className="aq-query">"{activeQuery.query}"</div>
        </div>
      )}

      <ActivityLog logs={logs} />

      {/* Persistent review history */}
      {reviewLogs.map((r, i) => (
        <div key={i} className="review-history-entry">
          <div className="rh-header">
            <span className="rh-iteration">Iteration {r.iteration}</span>
            <span className={`rh-verdict rh-verdict--${r.verdict}`}>
              {r.verdict === 'approve' ? '✓ Approved' :
               r.verdict === 'reject'  ? '✕ Rejected' :
               '💬 Comment'}
            </span>
          </div>
          <div className="rh-feedback">"{r.feedback}"</div>
        </div>
      ))}

      {/* Current interrupt */}
      {interrupt && (
        <HumanReview
          data={interrupt}
          onSubmit={handleReview}
          isSubmitting={isSubmitting}
        />
      )}

      {/* Final brief */}
      {brief && (
        <IntelBrief brief={brief} onReset={handleReset} />
      )}

    </div>
  );
}