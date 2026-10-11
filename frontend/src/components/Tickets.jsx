import { useEffect, useState } from "react";
import { api } from "../api";

const EMPTY = { subject: "", description: "", priority: "medium", order_number: "" };

export default function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/tickets").then(setTickets).catch((e) => setError(e.message));
  }, []);

  const update = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    const body = { ...form, order_number: form.order_number.trim() || null };
    try {
      const created = await api("/tickets", { method: "POST", body });
      setTickets([created, ...tickets]);
      setForm(EMPTY);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="box">
      <h2>Support tickets</h2>
      <form className="ticket-form" onSubmit={submit}>
        <input name="subject" placeholder="Subject" value={form.subject} onChange={update} required />
        <textarea name="description" placeholder="Describe the problem (at least 10 characters)" value={form.description} onChange={update} required />
        <div className="row">
          <select name="priority" value={form.priority} onChange={update}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <input name="order_number" placeholder="Order number (optional)" value={form.order_number} onChange={update} />
        </div>
        {error && <p className="error">{error}</p>}
        <button>Raise ticket</button>
      </form>

      {tickets.map((t) => (
        <div key={t.id} className="ticket">
          <strong>#{t.id} {t.subject}</strong>
          <span className="muted">{t.status} / {t.priority}</span>
          <p>{t.description}</p>
        </div>
      ))}
    </div>
  );
}