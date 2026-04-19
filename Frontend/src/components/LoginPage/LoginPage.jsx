import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import logo from '../../assets/images/Logo1.png';
import './LoginPage.css';

function LoginPage() {
  // const { role } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', password: '', captcha: '' });
  const [captchaValue] = useState(Math.random().toString(36).substring(2, 8).toUpperCase());

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleLogin = (e) => {
    e.preventDefault();
    navigate('/otp');
  };

  // const roleLabel = role ? role.charAt(0).toUpperCase() + role.slice(1) : 'User';

  return (
    <div className="login-wrapper">
      <header className="login-header">
        <div className="landing-logo">
          <img src={logo} alt="Hein+Fricke Logo" className="logo-img" />
        </div>
        <p className="login-subtitle">HR and Recruitment Platform</p>
      </header>

      <main className="login-main">
        <div className="login-card">
          <h2 className="login-title">Sign in</h2>
          {/* <p className="login-role-label">{roleLabel} Portal</p> */}

          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <label>Username <span className="required">*</span></label>
              <input
                type="text"
                name="username"
                placeholder="Enter Username"
                value={form.username}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Password <span className="required">*</span></label>
              <input
                type="password"
                name="password"
                placeholder="Enter Password"
                value={form.password}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Verify Captcha <span className="required">*</span></label>
              <div className="captcha-box">{captchaValue}</div>
              <input
                type="text"
                name="captcha"
                placeholder="Enter Captch"
                value={form.captcha}
                onChange={handleChange}
                required
              />
            </div>

            <button type="submit" className="btn-login">Login</button>
          </form>

          <a href="https://www.google.com" className="forgot-password">Forgot Password</a>
        </div>
      </main>
    </div>
  );
}

export default LoginPage;
