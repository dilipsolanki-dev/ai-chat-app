// Animated "AI is typing…" dots shown in an assistant bubble while the first
// token of a streamed reply is still pending. Markup mirrors chat-template.html:
// a .typing wrapper with three <span> dots whose CSS staggers their animation.

// No props today, but the contract names the interface so callers stay typed.
export type TypingIndicatorProps = Record<string, never>;

export default function TypingIndicator() {
  return (
    <div className="typing">
      <span></span>
      <span></span>
      <span></span>
    </div>
  );
}
