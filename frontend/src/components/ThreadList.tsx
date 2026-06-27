import type { ConversationOut } from "../api";
import ThreadItem from "./ThreadItem";

export interface ThreadListProps {
  conversations: ConversationOut[];
  activeId: number | null;
  onSelect: (id: number) => void;
}

export default function ThreadList({ conversations, activeId, onSelect }: ThreadListProps) {
  return (
    <nav className="threads">
      {conversations.map((conversation) => (
        <ThreadItem
          key={conversation.id}
          conversation={conversation}
          active={conversation.id === activeId}
          onSelect={onSelect}
        />
      ))}
    </nav>
  );
}
