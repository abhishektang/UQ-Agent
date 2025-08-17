import './LoginViewstyle.css'; // Add this import at the top of your file

export default function LoginView({ onLogin }) {
  return (
    <div className="login-view">
      <img src="icons/icon128.png" alt="UQ Agent Logo" className="logo" />
      <p>Please login to your UQ Dashboard to use UQ Agent</p>
      <button onClick={onLogin} className="btn login-btn">
        Login to UQ Dashboard
        <svg className="btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" fill="currentColor"/>
        </svg>
      </button>
    </div>
  )
}