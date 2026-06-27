const SUGGESTIONS = [
  "Explain a concept",
  "Summarize an article",
  "Quiz me on a topic",
  "Debug my code",
];

export interface EmptyStateProps {
  onPick: (text: string) => void;
}

export default function EmptyState({ onPick }: EmptyStateProps) {
  return (
    <section className="empty">
      <div className="logo">A</div>
      <h2>How can I help you today?</h2>
      <p>Ask anything — explanations, summaries, practice problems, or code help.</p>
      <div className="suggestions">
        {SUGGESTIONS.map((text) => (
          <button key={text} className="chip" onClick={() => onPick(text)}>
            {text}
          </button>
        ))}
      </div>
    </section>
  );
}
