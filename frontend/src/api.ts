// API client for the chat backend.
//
// During dev, Vite proxies "/api/*" to http://localhost:8000 (see vite.config.ts),
// so we use same-origin relative URLs here and avoid CORS entirely.

export type Role = "user" | "assistant" | "system";

export interface MessageOut {
  id: number;
  role: Role;
  content: string;
  created_at: string;
}

export interface ConversationOut {
  id: number;
  title: string;
  created_at: string;
}

export async function createConversation(): Promise<ConversationOut> {
  const res = await fetch("/api/conversations", { method: "POST" });
  if (!res.ok) throw new Error(`createConversation failed: ${res.status}`);
  return res.json();
}

export async function listMessages(conversationId: number): Promise<MessageOut[]> {
  const res = await fetch(`/api/conversations/${conversationId}/messages`);
  if (!res.ok) throw new Error(`listMessages failed: ${res.status}`);
  return res.json();
}

// -----------------------------------------------------------------------------
// streamChat — the heart of the live UI.
//
// The backend responds with Server-Sent Events: a long-lived response whose body
// is a stream of `data: {json}\n\n` blocks. The browser's EventSource API only
// supports GET, and we need POST, so we read the stream manually with fetch +
// response.body.getReader(). For each parsed event we invoke onDelta / onDone.
// -----------------------------------------------------------------------------
export async function streamChat(
  conversationId: number,
  message: string,
  onDelta: (text: string) => void,
  onDone: () => void,
): Promise<void> {
  const res = await fetch(`/api/conversations/${conversationId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok || !res.body) throw new Error(`chat failed: ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = ""; // bytes can split mid-event, so we accumulate then split

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE events are separated by a blank line ("\n\n").
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? ""; // keep the last (possibly incomplete) piece

    for (const event of events) {
      const line = event.trim();
      if (!line.startsWith("data:")) continue;
      const payload = JSON.parse(line.slice(5).trim()); // strip "data:"

      if (payload.delta) onDelta(payload.delta);
      else if (payload.error) throw new Error(payload.error);
      else if (payload.done) onDone();
    }
  }
}
