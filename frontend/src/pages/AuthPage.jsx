import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import Wordmark from "../components/Wordmark";
export default function AuthPage() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const update = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") await login(form.email, form.password);
      else await register(form);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-wrap">
      <form className="card" onSubmit={submit}>
        <h1>Roh</h1>
        <p className="muted">Your AI support assistant</p>

        {mode === "register" && (
          <input name="full_name" placeholder="Full name" value={form.full_name} onChange={update} required />
        )}
        <input name="email" type="email" placeholder="Email" value={form.email} onChange={update} required />
        <input name="password" type="password" placeholder="Password (min 8 characters)" value={form.password} onChange={update} required />

        {error && <p className="error">{error}</p>}

        <button disabled={busy}>
          {busy ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
        </button>
        <button type="button" className="link" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "New here? Create an account" : "Already registered? Log in"}
        </button>
      </form>
    </div>
  );
}
