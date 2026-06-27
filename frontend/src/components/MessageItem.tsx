import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "../api";
import TypingIndicator from "./TypingIndicator";

export interface MessageItemProps {
  message: ChatMessage;
  streaming: boolean;
}

export default function MessageItem({ message, streaming }: MessageItemProps) {
  if (message.role === "user") {
    return (
      <div className="msg msg--user">
        <div className="msg__body">
          <div className="msg__text">{message.content}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="msg msg--assistant">
      <div className="msg__avatar">A</div>
      <div className="msg__body">
        <div className="msg__role">AI Chat</div>
        <div className="msg__text">
          {message.content === "" && streaming ? (
            <TypingIndicator />
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          )}
        </div>
      </div>
    </div>
  );
}
