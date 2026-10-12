import { useEffect, useRef, useState } from "react";
import { api } from "../api";
const STARTERS = ["Where is my order?", "What is your refund policy?", "I want to raise a complaint"];
import { createPortal } from "react-dom";
import TypedText from "./TypedText";

export default function Chat({ onThinking, slot }) {
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);
  useEffect(() => {
    onThinking?.(sending);
    return () => onThinking?.(false);
  }, [sending, onThinking]);
  useEffect(() => {
    api("/conversations").then(setConversations).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  const scrollToEnd = () => bottomRef.current?.scrollIntoView({ block: "end" });

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

  async function newChat(starter = "") {
    try {
      const created = await api("/conversations", { method: "POST", body: {} });
      setConversations([created, ...conversations]);
      setActiveId(created.id);
      setMessages([]);
      setInput(starter);
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

    const temp = { id: `tmp-${Date.now()}`, role: "user", content: text };
    setMessages((prev) => [...prev, temp]);
    setInput("");
    setSending(true);
    setError("");

    try {
      const created = await api(`/conversations/${activeId}/messages`, {
        method: "POST",
        body: { content: text },
      });
      const [userMsg, reply] = created;
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== temp.id),
        { ...userMsg, key: temp.id },
        { ...reply, animate: true },
      ]);
      api("/conversations").then(setConversations).catch(() => {});
    } catch (err) {
      setMessages((prev) => prev.filter((m) => m.id !== temp.id));
      setInput(text);
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

      const sidebar = (
    <>
      <button onClick={() => newChat()}>+ New chat</button>
      {conversations.map((c) => (
        <div
          key={c.id}
          className={c.id === activeId ? "conv active" : "conv"}
          onClick={() => open(c.id)}
        >
          <span>{c.title}</span>
          <button
            className="ghost small"
            aria-label="Delete conversation"
            onClick={(e) => {
              e.stopPropagation();
              remove(c.id);
            }}
          >
            x
          </button>
        </div>
      ))}
    </>
  );

  return (
    <>
      {slot && createPortal(sidebar, slot)}
      <section className="panel">
        {activeId === null ? (
          <div className="empty">
            <h2>What do you need help with?</h2>
            <p className="muted">Pick a starter, or open a chat from the list.</p>
            <div className="chips">
              {STARTERS.map((text) => (
                <button key={text} className="chip" onClick={() => newChat(text)}>
                  {text}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            <div className="messages">
                          {messages.map((m) => (
                <div key={m.key ?? m.id} className={`msg-row ${m.role}`}>
                  {m.role !== "user" && (
                    <span className="avatar" aria-hidden="true">R</span>
                  )}
                  <div className={`bubble ${m.role}`}>
                    <TypedText text={m.content} animate={Boolean(m.animate)} onTick={scrollToEnd} />
                  </div>
                </div>
              ))}
              {sending && (
                <div className="msg-row assistant">
                  <span className="avatar wobble" aria-hidden="true">R</span>
                  <div className="bubble assistant muted">Roh is thinking...</div>
                </div>
              )}
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
    </>
  );
}