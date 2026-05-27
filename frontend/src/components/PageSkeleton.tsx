export function PageSkeleton() {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div className="skeleton" style={{ height: 28, width: 280, marginBottom: 10 }} />
        <div className="skeleton" style={{ height: 14, width: 380 }} />
      </div>
      <div className="ticket-grid">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="ticket-card" style={{ cursor: 'default' }}>
            <div className="skeleton" style={{ height: 14, width: '35%' }} />
            <div className="skeleton" style={{ height: 18, width: '85%' }} />
            <div className="skeleton" style={{ height: 14, width: '95%' }} />
            <div className="skeleton" style={{ height: 14, width: '60%' }} />
          </div>
        ))}
      </div>
    </div>
  );
}
