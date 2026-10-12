import { useEffect, useState } from "react";

const CHARS_PER_TICK = 2;
const TICK_MS = 20;

export default function TypedText({ text, animate, onTick }) {
  const [shown, setShown] = useState(animate ? 0 : text.length);

  useEffect(() => {
    if (!animate) return;
    let count = 0;
    const id = setInterval(() => {
      count += CHARS_PER_TICK;
      setShown(Math.min(count, text.length));
      onTick?.();
      if (count >= text.length) clearInterval(id);
    }, TICK_MS);
    return () => clearInterval(id);
  }, [text, animate]);

  if (!animate) return <>{text}</>;

  return (
    <span style={{ position: "relative", display: "block" }}>
      <span style={{ visibility: "hidden" }}>{text}</span>
      <span style={{ position: "absolute", left: 0, right: 0, top: 0 }}>
        {text.slice(0, shown)}
      </span>
    </span>
  );
}