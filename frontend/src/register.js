import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { User, Mail, Lock } from 'lucide-react';
import './register.css';

const API_BASE = process.env.NODE_ENV === 'production' ? 'https://hackthon-kssem-new.onrender.com/api' : 'http://127.0.0.1:8000/api';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    username: '',
    password: ''
  });
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [error, setError] = useState('');
  const [msg, setMsg] = useState('');

  const handleSendOTP = async (e) => {
    e.preventDefault();
    setError('');
    setMsg('');
    try {
      const response = await axios.post(`${API_BASE}/auth/send-otp`, { email: formData.email });
      setOtpSent(true);
      setMsg(response.data.message);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send OTP');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const payload = { ...formData, otp };
      const response = await axios.post(`${API_BASE}/auth/register`, payload);
      localStorage.setItem('token', response.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="auth-container">
      <div className="auth-card glass">
        <div className="auth-header">
          <h2>Create Account</h2>
          <p>Join the community of CleanCodeX</p>
        </div>
        {error && <p className="error-msg">{error}</p>}
        {msg && <p style={{color: '#22c55e', fontSize: '13px', textAlign: 'center', marginBottom:'15px'}}>{msg}</p>}
        
        <form onSubmit={otpSent ? handleRegister : handleSendOTP}>
          {!otpSent ? (
            <>
              <div className="form-group">
                <User className="input-icon" size={20} />
                <input 
                  type="text" 
                  name="name"
                  placeholder="Full Name" 
                  value={formData.name}
                  onChange={handleChange}
                  required 
                />
              </div>
              <div className="form-group">
                <Mail className="input-icon" size={20} />
                <input 
                  type="email" 
                  name="email"
                  placeholder="Email Address" 
                  value={formData.email}
                  onChange={handleChange}
                  required 
                />
              </div>
              <div className="form-group">
                <User className="input-icon" size={20} />
                <input 
                  type="text" 
                  name="username"
                  placeholder="Username" 
                  value={formData.username}
                  onChange={handleChange}
                  required 
                />
              </div>
              <div className="form-group">
                <Lock className="input-icon" size={20} />
                <input 
                  type="password" 
                  name="password"
                  placeholder="Password" 
                  value={formData.password}
                  onChange={handleChange}
                  required 
                />
              </div>
            </>
          ) : (
            <div className="form-group">
              <Lock className="input-icon" size={20} />
              <input 
                type="text" 
                placeholder="6-Digit OTP from Email" 
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                required 
                style={{ letterSpacing: '2px', textAlign: 'center', fontWeight: 'bold' }}
              />
            </div>
          )}
          
          <button type="submit" className="btn-primary w-full">
            {otpSent ? 'Verify & Register' : 'Send OTP'}
          </button>
        </form>
        <div className="auth-footer">
          <p>Already have an account? <Link to="/login">Sign In</Link></p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
