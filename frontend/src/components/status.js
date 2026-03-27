import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SystemCheck = ({ apiBase }) => {
  const [status, setStatus] = useState('checking');

  useEffect(() => {
    const check = async () => {
      try {
        await axios.get(`${apiBase}/`);
        setStatus('connected');
      } catch (e) {
        setStatus('offline');
      }
    };
    check();
    const interval = setInterval(check, 5000);
    return () => clearInterval(interval);
  }, [apiBase]);

  return (
    <div className={`system-status-indicator ${status}`}>
      <span className="status-dot"></span>
      <span className="status-text">Backend: {status.toUpperCase()}</span>
    </div>
  );
};

export default SystemCheck;
