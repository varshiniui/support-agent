import { useEffect, useRef, useState } from "react";
import { api } from "../api";

export default function Chat() {
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    api("/conversations").then(setConversations).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function open(id) {
    setActiveId(id);
    setError("");
    try {
      const detail = await api(`/conversations/${id}`);
      setMessages(detail.messages);
    } catch (e) {
      setError(e.message);
    }
  }

  async function newChat() {
    try {
      const created = await api("/conversations", { method: "POST", body: {} });
      setConversations([created, ...conversations]);
      setActiveId(created.id);
      setMessages([]);
    } catch (e) {
      setError(e.message);
    }
  }

  async function remove(id) {
    try {
      await api(`/conversations/${id}`, { method: "DELETE" });
      setConversations(conversations.filter((c) => c.id !== id));
      if (activeId === id) {
        setActiveId(null);
        setMessages([]);
      }
    } catch (e) {
      setError(e.message);
    }
  }

  async function send(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;
    setSending(true);
    setError("");
    try {
      const created = await api(`/conversations/${activeId}/messages`, {
        method: "POST",
        body: { content: text },
      });
      setMessages([...messages, ...created]);
      setInput("");
      api("/conversations").then(setConversations).catch(() => {});
    } catch (e) {
      setError(e.message);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="chat">
      <aside className="sidebar">
        <button onClick={newChat}>+ New chat</button>
        {conversations.map((c) => (
          <div
            key={c.id}
            className={c.id === activeId ? "conv active" : "conv"}
            onClick={() => open(c.id)}
          >
            <span>{c.title}</span>
            <button
              className="ghost small"
              onClick={(e) => {
                e.stopPropagation();
                remove(c.id);
              }}
            >
              x
            </button>
          </div>
        ))}
      </aside>

      <section className="panel">
        {activeId === null ? (
          <p className="muted center">Start a new chat or pick one from the list.</p>
        ) : (
          <>
            <div className="messages">
              {messages.map((m) => (
                <div key={m.id} className={`bubble ${m.role}`}>
                  {m.content}
                </div>
              ))}
              {sending && <div className="bubble assistant">Roh is thinking...</div>}
              <div ref={bottomRef} />
            </div>
            {error && <p className="error">{error}</p>}
            <form className="composer" onSubmit={send}>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask Roh about an order, a refund, or a problem..."
                maxLength={2000}
              />
              <button disabled={sending}>{sending ? "..." : "Send"}</button>
            </form>
          </>
        )}
      </section>
    </div>
  );
}