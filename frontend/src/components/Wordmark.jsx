export default function Wordmark({ thinking = false }) {
  return (
    <span className={thinking ? "wordmark thinking" : "wordmark"} role="img" aria-label="Roh">
      <span className="wordmark-text" aria-hidden="true">Roh</span>
      <svg className="swoosh" aria-hidden="true" width="112" height="14" viewBox="0 0 112 14">
        <path d="M3 9 C 28 2, 66 2, 109 7" />
      </svg>
    </span>
  );
}