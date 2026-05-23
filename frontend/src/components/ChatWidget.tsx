import { useRef, useState } from "react";
import { api } from "../api/client";
import { ChatMessage } from "../types";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    const history = [...messages, userMessage];
    setMessages(history);
    setInput("");
    setLoading(true);

    try {
      const { reply } = await api.chat(text, messages);
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: reply,
        timestamp: new Date().toISOString(),
      };
      setMessages([...history, assistantMessage]);
    } catch (e) {
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: `Error: ${(e as Error).message}`,
        timestamp: new Date().toISOString(),
      };
      setMessages([...history, errorMessage]);
    } finally {
      setLoading(false);
      setTimeout(
        () => endRef.current?.scrollIntoView({ behavior: "smooth" }),
        50
      );
    }
  }

  return (
    <>
      <button
        onClick={() => setOpen((value) => !value)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-brand text-2xl text-white shadow-lg hover:bg-bright"
        aria-label="Toggle chat"
      >
        {open ? "×" : "💬"}
      </button>

      {open && (
        <div className="fixed bottom-24 right-6 z-50 flex h-[480px] w-80 flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl">
          <div className="bg-gradient-to-r from-navy to-brand px-4 py-3 text-white">
            <div className="font-semibold">Sainapsis Assistant</div>
            <div className="text-xs text-white/60">
              Ask about Bridge or this order system
            </div>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {messages.length === 0 && (
              <p className="text-center text-sm text-gray-400">
                Hi! Ask me about Sainapsis, Bridge, or how the order state
                machine works.
              </p>
            )}
            {messages.map((message) => (
              <div
                key={message.id || `${message.role}-${message.timestamp}`}
                className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm ${
                  message.role === "user"
                    ? "ml-auto bg-brand text-white"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {message.content}
              </div>
            ))}
            {loading && <div className="text-sm text-gray-400">Thinking…</div>}
            <div ref={endRef} />
          </div>

          <div className="flex gap-2 border-t border-gray-100 p-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="Type a message…"
              className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand focus:outline-none"
            />
            <button
              onClick={send}
              disabled={loading}
              className="rounded-lg bg-brand px-4 text-sm font-semibold text-white hover:bg-bright disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}