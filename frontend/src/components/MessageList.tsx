import { useEffect, useRef } from "react";
import type { ChatMessage } from "../api";
import EmptyState from "./EmptyState";
import MessageItem from "./MessageItem";

export interface MessageListProps {
  messages: ChatMessage[];
  busy: boolean;
  onPickSuggestion: (text: string) => void;
}

export default function MessageList({ messages, busy, onPickSuggestion }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return <EmptyState onPick={onPickSuggestion} />;
  }

  return (
    <section className="messages">
      <div className="messages__inner">
        {messages.map((m, i) => (
          <MessageItem
            key={m.id ?? i}
            message={m}
            streaming={busy && i === messages.length - 1}
          />
        ))}
        <div ref={bottomRef} />
      </div>
    </section>
  );
}
