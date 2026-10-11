import { useState } from "react";
import { useAuth } from "../AuthContext";
import Chat from "../components/Chat";
import Orders from "../components/Orders";
import Tickets from "../components/Tickets";
import Wordmark from "../components/Wordmark";

const TABS = { chat: Chat, orders: Orders, tickets: Tickets };

export default function Home() {
  const { user, logout } = useAuth();
  const [tab, setTab] = useState("chat");
  const [thinking, setThinking] = useState(false);
  const View = TABS[tab];
  const [slot, setSlot] = useState(null);
    return (
    <div className="app">
      <aside className="rail">
        <div className="brand">
          <Wordmark thinking={thinking} />
        </div>
        <div className="rail-slot" ref={setSlot} />
        <div className="rail-foot">
          <span>{user.email}</span>
          <button className="rail-out" onClick={logout}>Log out</button>
        </div>
      </aside>
      <main className="main">
        <nav className="tabs">
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
        <div className="content">
          <View onThinking={setThinking} slot={slot} />
        </div>
      </main>
    </div>
  );
}