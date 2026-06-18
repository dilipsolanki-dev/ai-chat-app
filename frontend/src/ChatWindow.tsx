import { useEffect, useRef, useState } from "react";
import {
  createConversation,
  listMessages,
  streamChat,
  type MessageOut,
} from "./api";

// A local message shape. We reuse MessageOut but the streaming assistant message
// won't have a DB id yet, so id is optional while it's being typed out.
type ChatMessage = Omit<MessageOut, "id" | "created_at"> & { id?: number };

export default function ChatWindow() {
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // On first load: reuse the conversation we saved in localStorage (so a reload
  // reopens the same chat), or create a new one if there isn't a saved id yet.
  useEffect(() => {
    (async () => {
      const saved = localStorage.getItem("conversationId");
      if (saved) {
        const id = Number(saved);
        setConversationId(id);
        setMessages(await listMessages(id));
        return;
      }
      const convo = await createConversation();
      localStorage.setItem("conversationId", String(convo.id));
      setConversationId(convo.id);
      setMessages(await listMessages(convo.id));
    })();
  }, []);

  // Auto-scroll to the latest message.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    if (!input.trim() || conversationId == null || busy) return;
    const text = input.trim();
    setInput("");
    setBusy(true);

    // 1. Optimistically show the user's message immediately.
    // 2. Add an empty assistant message we'll fill as tokens stream in.
    setMessages((prev) => [
      ...prev,
      { role: "user", content: text },
      { role: "assistant", content: "" },
    ]);

    try {
      await streamChat(
        conversationId,
        text,
        // onDelta: append each token to the LAST message (the assistant one).
        (piece) =>
          setMessages((prev) => {
            const next = [...prev];
            next[next.length - 1] = {
              ...next[next.length - 1],
              content: next[next.length - 1].content + piece,
            };
            return next;
          }),
        // onDone: nothing extra needed; the message is already on screen.
        () => {},
      );
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `⚠️ ${(err as Error).message}` },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="chat">
      <header>AI Chat {conversationId ? `#${conversationId}` : "(connecting…)"}</header>

      <div className="messages">
        {messages.map((m, i) => (
          <div key={m.id ?? i} className={`msg ${m.role}`}>
            <span className="role">{m.role}</span>
            <span className="content">{m.content || "…"}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="composer">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Type a message…"
          disabled={busy || conversationId == null}
        />
        <button onClick={send} disabled={busy || conversationId == null}>
          {busy ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
