import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/images/Logo1.png';
import './OTPPage.css';

function OTPPage() {
  const navigate = useNavigate();
  const [otp, setOtp] = useState('');

  const handleVerify = (e) => {
    e.preventDefault();
    navigate('/dashboard');
  };

  return (
    <div className="otp-wrapper">
      <header className="otp-header">
        <div className="landing-logo">
          <img src={logo} alt="Hein+Fricke Logo" className="logo-img" />
        </div>
        <p className="otp-subtitle">HR and Recruitment Platform</p>
      </header>

      <main className="otp-main">
        <div className="otp-card">
          <h2 className="otp-title">Sign in</h2>

          <form onSubmit={handleVerify} className="otp-form">
            <div className="form-group">
              <label>OTP <span className="required">*</span></label>
              <input
                type="text"
                placeholder="Enter OTP"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn-verify">Verify</button>
          </form>

          <p className="otp-note">Please check your registered E-mail ID</p>
        </div>
      </main>
    </div>
  );
}

export default OTPPage;
