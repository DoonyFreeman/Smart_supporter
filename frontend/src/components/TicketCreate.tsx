import { useState, type FormEvent } from 'react';
import { submitTicket } from '../api/tickets';

export function TicketCreate({ onCreated }: { onCreated: () => void }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await submitTicket({ title, description });
      setTitle('');
      setDescription('');
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create ticket');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="ticket-create" onSubmit={handleSubmit}>
      <h2>New Ticket</h2>
      <input
        type="text"
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <textarea
        placeholder="Describe your issue..."
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
        rows={5}
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'Submit Ticket'}
      </button>
      <p className="hint">The ticket will be processed by AI for auto-classification.</p>
    </form>
  );
}
