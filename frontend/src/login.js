import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Mail, Lock } from 'lucide-react';
import './login.css';

const API_BASE = process.env.NODE_ENV === 'production' ? 'https://hackthon-kssem-new.onrender.com/api' : 'http://127.0.0.1:8000/api';

const LoginPage = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [msg, setMsg] = useState('');
  const [isForgotMode, setIsForgotMode] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMsg('');

    if (isForgotMode) {
      try {
        await axios.post(`${API_BASE}/auth/forgot-password`, {
          username: username,
          new_password: password
        });
        setMsg('Password reset successfully. You can now login.');
        setIsForgotMode(false);
        setPassword('');
      } catch (err) {
        setError(err.response?.data?.detail || 'User not found or error occurred.');
      }
      return;
    }

    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    try {
      const response = await axios.post(`${API_BASE}/auth/login`, params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      localStorage.setItem('token', response.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid username or password');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card glass">
        <div className="auth-header">
          <h2>{isForgotMode ? 'Recover Password' : 'Welcome Back'}</h2>
          <p>{isForgotMode ? 'Enter username and your new password' : 'Sign in to continue your coding journey'}</p>
        </div>
        {error && <p className="error-msg">{error}</p>}
        {msg && <p style={{color: '#22c55e', fontSize: '13px', textAlign: 'center', marginBottom:'15px'}}>{msg}</p>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <Mail className="input-icon" size={20} />
            <input 
              type="text" 
              placeholder="Username" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required 
            />
          </div>
          <div className="form-group">
            <Lock className="input-icon" size={20} />
            <input 
              type="password" 
              placeholder={isForgotMode ? "New Password" : "Password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>
          
          <button type="submit" className="btn-primary w-full">
            {isForgotMode ? 'Reset Password' : 'Sign In'}
          </button>
        </form>

        <div className="auth-footer" style={{marginTop: '15px'}}>
          {!isForgotMode ? (
            <p>
              <span style={{cursor:'pointer', color:'#58a6ff', marginRight:'15px'}} onClick={() => setIsForgotMode(true)}>Forgot Password?</span>
              Don't have an account? <Link to="/register">Sign Up</Link>
            </p>
          ) : (
            <p><span style={{cursor:'pointer', color:'#58a6ff'}} onClick={() => setIsForgotMode(false)}>Back to Login</span></p>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
