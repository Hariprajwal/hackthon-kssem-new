import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { User, Lock, Key, ArrowLeft } from 'lucide-react';
import './profile.css';

const API_BASE = process.env.NODE_ENV === 'production' ? 'https://hackthon-kssem-new.onrender.com/api' : 'http://127.0.0.1:8000/api';
const getToken = () => localStorage.getItem('token');
const logout = () => { localStorage.removeItem('token'); window.location.href = '/login'; };

const ProfilePage = ({ onClose, theme, onThemeChange }) => {
  const [userData, setUserData] = useState({ username: '', name: '', email: '' });
  
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [msg, setMsg] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!getToken()) {
      logout();
      return;
    }
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      // We don't have a direct /auth/me endpoint defined yet, 
      // but we can decode the JWT to get the username, or just rely on a new endpoint.
      // Since it's a hackathon and we only have access_token, let's parse JWT manually.
      const token = getToken();
      if (!token) return;
      const payload = JSON.parse(atob(token.split('.')[1]));
      setUserData({ username: payload.sub, name: payload.sub, email: payload.sub + '@cleancodex.ai' });
    } catch (err) {
      console.error(err);
    }
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    setError('');
    setMsg('');

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    try {
      await axios.post(`${API_BASE}/auth/reset-password`, {
        current_password: currentPassword,
        new_password: newPassword
      }, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setMsg('Password updated successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update password');
    }
  };

  return (
    <div className="profile-container">
      <div className="profile-wrapper glass">
        <button className="back-btn" onClick={onClose}>
          <ArrowLeft size={18} /> Back to Editor
        </button>
        
        <div className="profile-header">
          <div className="avatar-circle">
            <User size={40} color="#a78bfa" />
          </div>
          <h2>{userData.username}'s Profile</h2>
          <p className="profile-email">{userData.email}</p>
        </div>

        <div className="profile-theme-controls">
          <h3>Interface Theme</h3>
          <div className="theme-btn-group">
            <button 
              className={`theme-pick-btn ${theme === 'vs-light' ? 'active' : ''}`}
              onClick={() => onThemeChange('vs-light')}
            >
              ☀️ Light Theme
            </button>
            <button 
              className={`theme-pick-btn ${theme === 'vs-dark' ? 'active' : ''}`}
              onClick={() => onThemeChange('vs-dark')}
            >
              🌙 Dark Theme
            </button>
          </div>
        </div>

        <div className="profile-content">
          <h3>Reset Password</h3>
          
          {error && <div className="feedback-msg err">{error}</div>}
          {msg && <div className="feedback-msg ok">{msg}</div>}

          <form onSubmit={handlePasswordReset}>
            <div className="form-group">
              <Lock className="input-icon" size={18} />
              <input 
                type="password" 
                placeholder="Current Password" 
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required 
              />
            </div>
            
            <div className="form-group">
              <Key className="input-icon" size={18} />
              <input 
                type="password" 
                placeholder="New Password" 
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required 
              />
            </div>

            <div className="form-group">
              <Key className="input-icon" size={18} />
              <input 
                type="password" 
                placeholder="Confirm New Password" 
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required 
              />
            </div>

            <button type="submit" className="btn-primary w-full">Update Password</button>
          </form>
          
          <button className="btn-logout" onClick={logout}>Sign Out Component</button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
