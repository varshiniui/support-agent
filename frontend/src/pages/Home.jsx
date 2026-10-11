import { useState } from "react";
import { useAuth } from "../AuthContext";
import Chat from "../components/Chat";
import Orders from "../components/Orders";
import Tickets from "../components/Tickets";

const TABS = { chat: Chat, orders: Orders, tickets: Tickets };

export default function Home() {
  const { user, logout } = useAuth();
  const [tab, setTab] = useState("chat");
  const View = TABS[tab];

  return (
    <div className="app">
      <header className="topbar">
        <strong>Roh</strong>
        <nav>
          {Object.keys(TABS).map((name) => (
            <button
              key={name}
              className={tab === name ? "tab active" : "tab"}
              onClick={() => setTab(name)}
            >
              {name}
            </button>
          ))}
        </nav>
        <span className="muted">{user.email}</span>
        <button className="ghost" onClick={logout}>Log out</button>
      </header>
      <main className="content">
        <View />
      </main>
    </div>
  );
}