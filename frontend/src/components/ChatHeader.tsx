// Chat header: shows the active conversation's title + message count, and a
// trash button to delete it. Presentational only — the parent owns the data.

export interface ChatHeaderProps {
  title: string;
  messageCount: number;
  busy: boolean;
  onDelete: () => void;
}

export default function ChatHeader({ title, messageCount, busy, onDelete }: ChatHeaderProps) {
  return (
    <header className="chat__head">
      <div className="chat__title">
        {title}
        <small>{messageCount} messages</small>
      </div>
      <button
        className="icon-btn"
        title="Delete conversation"
        onClick={onDelete}
        disabled={busy}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/></svg>
      </button>
    </header>
  );
}
