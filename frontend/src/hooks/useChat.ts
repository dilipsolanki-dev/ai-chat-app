// useChat — drives the live message list for the active conversation.
//
// It owns the optimistic message array, the composer input, and the busy flag,
// and leans on the conversation hook (passed in as `deps`) for anything that
// touches the conversation list itself (creating a row lazily, patching titles,
// dropping a conversation that turned out to be gone).

import { useCallback, useEffect, useState } from "react";
import { listMessages, streamChat, type ChatMessage } from "../api";

interface UseChatDeps {
  activeId: number | null;
  ensureActive: () => Promise<number>;
  patchTitle: (id: number, title: string) => void;
  markStale: (id: number) => void;
}

export function useChat(deps: UseChatDeps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  const { activeId, ensureActive, patchTitle, markStale } = deps;

  // Load the persisted messages whenever the active conversation changes.
  // Everything runs through one async load so we never call setState
  // synchronously in the effect body (React 19 flags that), and a `cancelled`
  // guard drops a stale response if you switch conversations mid-fetch. A throw
  // (e.g. a 404) means the conversation is gone, so mark it stale.
  useEffect(() => {
    let cancelled = false;
    const load = async (): Promise<ChatMessage[]> =>
      activeId == null ? [] : await listMessages(activeId);

    load()
      .then((loaded) => {
        if (!cancelled) setMessages(loaded);
      })
      .catch(() => {
        if (cancelled) return;
        if (activeId != null) markStale(activeId);
        setMessages([]);
      });

    return () => {
      cancelled = true;
    };
  }, [activeId, markStale]);

  const send = useCallback(async () => {
    if (!input.trim() || busy) return;

    const text = input.trim();
    setInput("");
    setBusy(true);

    // Create the conversation row lazily if this is the first message.
    const id = await ensureActive();

    // Optimistically show the user's message and an empty assistant bubble that
    // we'll fill in as deltas stream back.
    setMessages((prev) => [
      ...prev,
      { role: "user", content: text },
      { role: "assistant", content: "" },
    ]);

    try {
      await streamChat(id, text, {
        onDelta: (piece) =>
          setMessages((prev) => {
            const next = prev.slice();
            const last = next[next.length - 1];
            next[next.length - 1] = { ...last, content: last.content + piece };
            return next;
          }),
        onTitle: (title) => patchTitle(id, title),
        onDone: () => {},
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ " + message },
      ]);
    } finally {
      setBusy(false);
    }
  }, [input, busy, ensureActive, patchTitle]);

  return { messages, input, setInput, busy, send };
}
