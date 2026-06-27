import type { ConversationOut } from "../api";

export interface ThreadItemProps {
  conversation: ConversationOut;
  active: boolean;
  onSelect: (id: number) => void;
}

export default function ThreadItem({ conversation, active, onSelect }: ThreadItemProps) {
  return (
    <a
      className={active ? "thread is-active" : "thread"}
      onClick={() => onSelect(conversation.id)}
    >
      <svg
        width="15"
        height="15"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
      <span>{conversation.title}</span>
    </a>
  );
}
