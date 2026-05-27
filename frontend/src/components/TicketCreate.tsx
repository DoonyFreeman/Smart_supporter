import { useState, type FormEvent } from 'react';
import { submitTicket } from '../api/tickets';
import { useToast } from './Toast';
import { IconSpark } from './Icons';
import type { Ticket } from '../types';

interface Props {
  onCreated: (ticket: Ticket) => void;
}

export function TicketCreate({ onCreated }: Props) {
  const toast = useToast();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const ticket = await submitTicket({ title, description });
      setTitle('');
      setDescription('');
      toast.push('Ticket submitted — AI is processing it now', 'success');
      onCreated(ticket);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to create ticket';
      setError(msg);
      toast.push(msg, 'error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="title-xl">Submit a ticket</h1>
          <p className="subtitle">
            Describe the issue. Our AI agent will classify, route, and reply
            within seconds.
          </p>
        </div>
      </div>

      <form className="submit-panel" onSubmit={handleSubmit}>
        <h2>What's going on?</h2>
        <p className="lead">
          Be specific — include exact error messages, steps to reproduce, and
          what you expected to happen. Better input = better AI response.
        </p>

        <div className="row">
          <div className="field-group">
            <label>Title</label>
            <input
              className="input"
              type="text"
              placeholder="e.g. Reports export fails with 500 error"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              maxLength={255}
            />
          </div>

          <div className="field-group">
            <label>Description</label>
            <textarea
              className="textarea"
              placeholder={
                'Describe the problem in detail.\n\n' +
                '• What did you try?\n' +
                '• What error did you see (exact text)?\n' +
                '• Browser / OS / version?\n'
              }
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              rows={8}
            />
          </div>
        </div>

        {error && (
          <div className="error-banner" style={{ marginTop: 14 }}>{error}</div>
        )}

        <div className="actions">
          <span className="hint">
            <IconSpark width={14} height={14} /> Will be analysed by AI agent
          </span>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? 'Submitting…' : 'Submit ticket'}
          </button>
        </div>
      </form>
    </div>
  );
}
