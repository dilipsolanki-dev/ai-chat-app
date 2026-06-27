// Owns the conversation list and which one is active.
//
// "Active" is persisted to localStorage under 'conversationId' so a reload lands
// you back on the last conversation you were viewing. The active row can be null:
// "New chat" is lazy — no DB row exists until the first message is sent.

import { useCallback, useEffect, useState } from "react";
import type { ConversationOut } from "../api";
import { createConversation, deleteConversation, listConversations } from "../api";

const STORAGE_KEY = "conversationId";

export function useConversations() {
  const [conversations, setConversations] = useState<ConversationOut[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  // On mount: fetch the list, then restore the persisted active id if it still
  // exists, else fall back to the newest conversation (the list is created_at DESC).
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const list = await listConversations();
        if (cancelled) return;
        setConversations(list);

        const stored = localStorage.getItem(STORAGE_KEY);
        const storedId = stored != null ? Number(stored) : null;
        if (storedId != null && list.some((c) => c.id === storedId)) {
          setActiveId(storedId);
        } else if (list.length > 0) {
          setActiveId(list[0].id);
        } else {
          setActiveId(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  // Keep localStorage in sync with the active id (remove it when null).
  useEffect(() => {
    if (activeId == null) localStorage.removeItem(STORAGE_KEY);
    else localStorage.setItem(STORAGE_KEY, String(activeId));
  }, [activeId]);

  const select = useCallback((id: number) => {
    setActiveId(id);
  }, []);

  const startNewChat = useCallback(() => {
    setActiveId(null);
  }, []);

  // Resolve a real conversation id to send into: reuse the active one, or create
  // a fresh row on the fly and make it active.
  const ensureActive = useCallback(async (): Promise<number> => {
    if (activeId != null) return activeId;
    const convo = await createConversation();
    setConversations((prev) => [convo, ...prev]);
    setActiveId(convo.id);
    return convo.id;
  }, [activeId]);

  const remove = useCallback(async (id: number): Promise<void> => {
    await deleteConversation(id);
    setConversations((prev) => {
      const next = prev.filter((c) => c.id !== id);
      // If we just deleted the active conversation, jump to the newest remaining.
      setActiveId((current) => (current === id ? (next[0]?.id ?? null) : current));
      return next;
    });
  }, []);

  const patchTitle = useCallback((id: number, title: string) => {
    setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, title } : c)));
  }, []);

  // The conversation vanished server-side (e.g. a 404 on load); drop it from the
  // list + storage and activate the newest remaining one.
  const markStale = useCallback((id: number) => {
    localStorage.removeItem(STORAGE_KEY);
    setConversations((prev) => {
      const next = prev.filter((c) => c.id !== id);
      setActiveId((current) => (current === id ? (next[0]?.id ?? null) : current));
      return next;
    });
  }, []);

  return {
    conversations,
    activeId,
    loading,
    select,
    startNewChat,
    ensureActive,
    remove,
    patchTitle,
    markStale,
  };
}
