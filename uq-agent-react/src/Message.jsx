export default function Message({ text, role = 'Model' }) { // Default to 'Model' if undefined
  return (
    <div className={`message ${(role || 'Model').toLowerCase()}`}>
      <div className="message-content">
        {String(text || '').split('\n').map((line, i) => (
          <p key={i}>{line}</p>
        ))}
      </div>
    </div>
  );
}