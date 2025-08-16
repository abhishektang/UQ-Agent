export default function LoginView({ onLogin }) {
  return (
    <div className="login-view">
      <img src="icons/icon128.png" alt="UQ Agent Logo" className="logo" />
      <p>Please login to your UQ Dashboard to use UQ Agent</p>
      <button onClick={onLogin} className="btn">
        Login to UQ Dashboard
      </button>
    </div>
  )
}