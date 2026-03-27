import React, { useState, useRef, useEffect } from 'react';
import { Activity, Save, FilePlus, Wand2, Play, Search, Zap, ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './navbar.css';

const Navbar = ({ onSave, onRun, onCheck, onFormat, onNewFile, onThemeChange, isLoading, backendStatus, onNavigateProfile }) => {
  const [activeMenu, setActiveMenu] = useState(null);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setActiveMenu(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleMenu = (menu) => {
    setActiveMenu(activeMenu === menu ? null : menu);
  };

  const handleAction = (action) => {
    setActiveMenu(null);
    if (!isLoading) action();
  };

  return (
    <nav className="top-navbar" ref={menuRef}>
      <div className="nav-brand">
        <Activity size={20} color="#58a6ff" />
        <span className="brand-name">CleanCodeX</span>
        <div className={`conn-dot ${backendStatus === 'connected' ? 'online' : 'offline'}`} title={`Backend: ${backendStatus}`} />
      </div>

      <div className="nav-menus">
        {/* File Menu */}
        <div className="nav-menu-wrapper">
          <span className={`nav-menu-item ${activeMenu === 'file' ? 'active' : ''}`} onClick={() => toggleMenu('file')}>
            File
          </span>
          {activeMenu === 'file' && (
            <div className="nav-dropdown">
              <div className="nav-drop-item" onClick={() => handleAction(onNewFile)}>New File</div>
              <div className="nav-drop-item" onClick={() => handleAction(onSave)}>Save</div>
              <div className="nav-drop-divider"></div>
              <div className="nav-drop-item" onClick={() => handleAction(onNavigateProfile)}>Profile</div>
              <div className="nav-drop-item text-danger" onClick={() => handleAction(() => { localStorage.removeItem('token'); navigate('/login'); })}>Logout</div>
            </div>
          )}
        </div>

        {/* Edit Menu */}
        <div className="nav-menu-wrapper">
          <span className={`nav-menu-item ${activeMenu === 'edit' ? 'active' : ''}`} onClick={() => toggleMenu('edit')}>
            Edit
          </span>
          {activeMenu === 'edit' && (
            <div className="nav-dropdown">
              <div className="nav-drop-item" onClick={() => handleAction(onFormat)}>Format Code</div>
              <div className="nav-drop-item" onClick={() => handleAction(() => window.dispatchEvent(new CustomEvent('editor-fix-all')))}>Fix All Issues</div>
            </div>
          )}
        </div>

        {/* View Menu (Theme) */}
        <div className="nav-menu-wrapper">
          <span className={`nav-menu-item ${activeMenu === 'view' ? 'active' : ''}`} onClick={() => toggleMenu('view')}>
            View
          </span>
          {activeMenu === 'view' && (
            <div className="nav-dropdown">
              <div className="nav-drop-item" onClick={() => handleAction(() => onThemeChange('vs-dark'))}>Theme: Default Dark</div>
              <div className="nav-drop-item" onClick={() => handleAction(() => onThemeChange('vs-light'))}>Theme: Clean Light</div>
              <div className="nav-drop-item" onClick={() => handleAction(() => onThemeChange('hc-black'))}>Theme: High Contrast</div>
              <div className="nav-drop-divider"></div>
              <div className="nav-drop-item" onClick={() => handleAction(() => onThemeChange('dracula'))}>Theme: Dracula</div>
              <div className="nav-drop-item" onClick={() => handleAction(() => onThemeChange('monokai'))}>Theme: Monokai</div>
              <div className="nav-drop-item" onClick={() => handleAction(() => onThemeChange('cyberpunk'))}>Theme: Cyberpunk</div>
              <div className="nav-drop-item" onClick={() => handleAction(() => onThemeChange('oceanic'))}>Theme: Oceanic</div>
            </div>
          )}
        </div>

        {/* Run Menu */}
        <div className="nav-menu-wrapper">
          <span className={`nav-menu-item ${activeMenu === 'run' ? 'active' : ''}`} onClick={() => toggleMenu('run')}>
            Run
          </span>
          {activeMenu === 'run' && (
            <div className="nav-dropdown">
              <div className="nav-drop-item" onClick={() => handleAction(onRun)}>Execute Code</div>
              <div className="nav-drop-item" onClick={() => handleAction(onCheck)}>Analyze Code</div>
            </div>
          )}
        </div>
      </div>

      <div className="nav-search">
        <Search size={13} />
        <input type="text" placeholder="Search files..." />
      </div>

      <div className="nav-actions">
        <button className="nav-btn" onClick={onNewFile} title="New File" disabled={isLoading}>
          <FilePlus size={17} />
          <span>New</span>
        </button>
        <button className="nav-btn" onClick={onSave} title="Save" disabled={isLoading}>
          <Save size={17} />
          <span>Save</span>
        </button>
        <button className="nav-btn accent" onClick={onFormat} title="Auto Format" disabled={isLoading}>
          <Wand2 size={17} />
          <span>Format</span>
        </button>
        <div className="nav-divider" />
        <button className="nav-btn lint" onClick={onCheck} title="Analyze Code" disabled={isLoading}>
          <Zap size={17} />
          <span>Analyze</span>
        </button>
        <button className="nav-btn run" onClick={onRun} title="Run Code" disabled={isLoading}>
          <Play size={17} fill="currentColor" />
          <span>Run</span>
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
