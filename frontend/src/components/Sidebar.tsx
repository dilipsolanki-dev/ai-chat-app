import type { ConversationOut } from "../api";
import ThreadList from "./ThreadList";

export interface SidebarProps {
  conversations: ConversationOut[];
  activeId: number | null;
  busy: boolean;
  onSelect: (id: number) => void;
  onNew: () => void;
}

export default function Sidebar({
  conversations,
  activeId,
  busy,
  onSelect,
  onNew,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar__head">
        <div className="logo">A</div>
        <div>
          <div className="brand-name">AI Chat</div>
          <div className="brand-sub">powered by Groq</div>
        </div>
      </div>

      <button className="new-chat" onClick={onNew} disabled={busy}>
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 5v14M5 12h14" />
        </svg>
        New chat
      </button>

      <div className="thread-label">Recent</div>
      <ThreadList
        conversations={conversations}
        activeId={activeId}
        onSelect={onSelect}
      />

      <div className="sidebar__foot">
        <div className="avatar">DS</div>
        <div>
          <div className="user-name">Dilip</div>
          <div className="user-mail">dsolanki@westernalliancelogistics.com</div>
        </div>
      </div>
    </aside>
  );
}
