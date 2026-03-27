import React from 'react';
import { Link } from 'react-router-dom';
import { Code, Zap, Shield, Sparkles } from 'lucide-react';
import './landingpage.css';

const LandingPage = () => {
  return (
    <div className="landing-container">
      <nav className="navbar container">
        <div className="logo">
          <Code className="logo-icon" />
          <span>CleanCodeX</span>
        </div>
        <div className="nav-links">
          <Link to="/login">Login</Link>
          <Link to="/register" className="btn-primary">Get Started</Link>
        </div>
      </nav>

      <main className="hero container">
        <div className="hero-content">
          <h1>Write <span className="gradient-text">Beautiful</span> Code with Ease</h1>
          <p>CleanCodeX is your AI-powered companion for code quality. Get real-time suggestions, auto-formatting, and intelligent analysis to make your code shine.</p>
          <div className="hero-btns">
            <Link to="/dashboard" className="btn-primary flex items-center gap-2">
              <Sparkles size={20} />
              Try CleanCodeX Now
            </Link>
          </div>
        </div>
        <div className="hero-visual">
          <div className="visual-card glass">
            <div className="card-header">
              <div className="dot red"></div>
              <div className="dot yellow"></div>
              <div className="dot green"></div>
            </div>
            <pre className="code-snippet">
              {`def hello_world():\n    print("Hello, CleanCodeX!")\n\n# Suggestion: Use f-strings for better readability`}
            </pre>
          </div>
        </div>
      </main>

      <section className="features container">
        <div className="feature-card">
          <Zap className="feature-icon" color="var(--primary)" />
          <h3>Real-time Linting</h3>
          <p>Catch errors as you type with our intelligent static analysis engine.</p>
        </div>
        <div className="feature-card">
          <Sparkles className="feature-icon" color="var(--accent)" />
          <h3>AI Suggestions</h3>
          <p>Get smart refactoring tips powered by state-of-the-art AI models.</p>
        </div>
        <div className="feature-card">
          <Shield className="feature-icon" color="var(--success)" />
          <h3>Auto Formatting</h3>
          <p>Keep your codebase consistent with one-click formatting using industry standards.</p>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
