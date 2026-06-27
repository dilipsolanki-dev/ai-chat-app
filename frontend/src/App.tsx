import "./App.css";
import { useConversations } from "./hooks/useConversations";
import { useChat } from "./hooks/useChat";
import Sidebar from "./components/Sidebar";
import ChatHeader from "./components/ChatHeader";
import MessageList from "./components/MessageList";
import Composer from "./components/Composer";

function App() {
  const convos = useConversations();
  const chat = useChat({
    activeId: convos.activeId,
    ensureActive: convos.ensureActive,
    patchTitle: convos.patchTitle,
    markStale: convos.markStale,
  });
  const active = convos.conversations.find((c) => c.id === convos.activeId);

  return (
    <div className="app">
      <Sidebar
        conversations={convos.conversations}
        activeId={convos.activeId}
        busy={chat.busy}
        onSelect={convos.select}
        onNew={convos.startNewChat}
      />
      <main className="chat">
        <ChatHeader
          title={active ? active.title : "New chat"}
          messageCount={chat.messages.length}
          busy={chat.busy}
          onDelete={() => {
            if (convos.activeId != null) convos.remove(convos.activeId);
          }}
        />
        <MessageList
          messages={chat.messages}
          busy={chat.busy}
          onPickSuggestion={chat.setInput}
        />
        <Composer
          value={chat.input}
          busy={chat.busy}
          disabled={false}
          onChange={chat.setInput}
          onSend={chat.send}
        />
      </main>
    </div>
  );
}

export default App;
