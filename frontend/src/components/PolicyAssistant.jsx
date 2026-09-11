import { useState } from 'react';
import { api } from '../services/api';
import { ErrorState, LoadingState } from './Common';

export function PolicyAssistant({ onRequest }) {
  const [question, setQuestion] = useState(
    'What preparation is required before my appointment?'
  );
  const [reply, setReply] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function ask(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    setReply(null);

    try {
      const result = await api('/policy/query', { question });
      setReply(result);

      if (result.request_id) {
        onRequest(result.request_id);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="assistant">
      <h2>Ask APOLLO</h2>

      <p>
        Get appointment and preparation guidance grounded in clinic policies.
        APOLLO does not diagnose or prescribe.
      </p>

      <form onSubmit={ask}>
        <label htmlFor="question">Your question</label>

        <textarea
          id="question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          maxLength={2000}
          required
        />

        <button
          className="confirm"
          disabled={busy || !question.trim()}
        >
          Ask APOLLO
        </button>
      </form>

      <ErrorState message={error} />

      {busy && (
        <LoadingState text="Retrieving clinic policies and preparing a grounded answer..." />
      )}

      {reply && (
        <article className="answer" aria-live="polite">
          <h3>
            {reply.status === 'allow'
              ? 'Grounded policy response'
              : reply.status === 'emergency'
              ? 'Urgent human assistance needed'
              : 'Human review required'}
          </h3>

          <p>
            {reply.status === 'allow'
              ? reply.answer || reply.draft
              : reply.message ||
                'APOLLO could not validate a grounded answer. Please contact the clinic for help.'}
          </p>

          {reply.citations?.length > 0 && (
            <div className="sources">
              Sources:{' '}
              {reply.citations.map((citation) => (
                <span key={citation}>{citation}</span>
              ))}
            </div>
          )}

          {reply.generation_mode && (
            <p>
              Generation:{' '}
              {reply.generation_mode.replaceAll('_', ' ')}
            </p>
          )}

          {reply.critic && (
            <p>
              Confidence: {reply.critic.confidence} · Safety review:{' '}
              {reply.critic.decision}
            </p>
          )}
        </article>
      )}
    </section>
  );
}