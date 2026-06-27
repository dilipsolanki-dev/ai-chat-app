// The message composer: an auto-growing textarea plus a send button.
// Enter sends, Shift+Enter inserts a newline. Sending is a no-op while the
// app is disabled/busy or the input is blank.

export interface ComposerProps {
  value: string;
  busy: boolean;
  disabled: boolean;
  onChange: (v: string) => void;
  onSend: () => void;
}

export default function Composer({ value, busy, disabled, onChange, onSend }: ComposerProps) {
  const canSend = !disabled && !busy && value.trim().length > 0;

  function handleChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    onChange(e.target.value);
    // Auto-grow: reset to measure the natural scroll height, then match it.
    e.target.style.height = "auto";
    e.target.style.height = `${e.target.scrollHeight}px`;
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (canSend) onSend();
    }
  }

  return (
    <div className="composer">
      <div className="composer__inner">
        <div className="input-wrap">
          <textarea
            rows={1}
            placeholder="Message AI Chat..."
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
          />
          <button
            className="send"
            title="Send"
            onClick={() => {
              if (canSend) onSend();
            }}
            disabled={!canSend}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7z" /></svg>
          </button>
        </div>
        <div className="composer__hint">AI Chat can make mistakes. Verify important information.</div>
      </div>
    </div>
  );
}
