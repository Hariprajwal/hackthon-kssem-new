import React, { useState } from 'react';
import { AlertCircle, Info, Sparkles, CheckCircle, Zap, ChevronDown, ChevronRight } from 'lucide-react';

/* eslint-disable jsx-a11y/no-static-element-interactions */

const SuggestionsPanel = ({ suggestions = [], qualityScore = 100, stats = {}, isAnalyzing, onQuickFix, onFixAll, diffPreview, onAIFix, onApplyAIFix }) => {
  const [expanded, setExpanded] = useState({ error: true, warning: true, info: false });
  const [aiFixData, setAiFixData] = useState(null); // { issueId, loading, explanation, fixedCode }
  
  const scoreColor = qualityScore > 80 ? '#22c55e' : qualityScore > 50 ? '#eab308' : '#ef4444';
  const scoreLabel = qualityScore > 80 ? 'Great' : qualityScore > 50 ? 'Fair' : 'Poor';

  const errors   = suggestions.filter(s => s.type === 'error');
  const warnings = suggestions.filter(s => s.type === 'warning');
  const infos    = suggestions.filter(s => s.type === 'info');

  const toggle = (type) => setExpanded(prev => ({ ...prev, [type]: !prev[type] }));

  const handleRequestAIFix = async (s) => {
    setAiFixData({ issueId: s.id, loading: true });
    const result = await onAIFix(s);
    setAiFixData({ issueId: s.id, loading: false, ...result });
  };


  const renderGroup = (items, type, label, icon) => {
    if (items.length === 0) return null;
    const isOpen = expanded[type];
    return (
      <div className="sg-group" key={type}>
        <button className={`sg-group-header ${type}`} onClick={() => toggle(type)}>
          <span>{icon} {label}</span>
          <span className="sg-count-badge">{items.length}</span>
          {isOpen ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
        </button>
        {isOpen && items.map((s, i) => (
          <div key={i} className={`sg-card ${type}`}>
            <div className="sg-icon">
              {type === 'error'   ? <AlertCircle size={13} color="#ef4444" /> :
               type === 'warning' ? <AlertCircle size={13} color="#eab308" /> :
               <Info size={13} color="#58a6ff" />}
            </div>
            <div className="sg-body">
              <p className="sg-msg">{s.message}</p>
              <div className="sg-meta">
                <span className="sg-line">L{s.line}</span>
                {s.symbol && <span className="sg-sym">{s.symbol}</span>}
                {s.fix && onQuickFix && (
                  <button className="sg-fix-btn" onClick={() => onQuickFix(s)}>⚡ Quick Fix</button>
                )}
                {onAIFix && (
                  <button className="sg-ai-fix-btn" onClick={() => handleRequestAIFix(s)}>
                    ✨ Ask AI
                  </button>
                )}
              </div>
              
              {/* AI Fix Inline Detail */}
              {aiFixData?.issueId === s.id && (
                <div className="sg-ai-box">
                  {aiFixData.loading ? (
                    <div className="sg-ai-loading">✨ AI is thinking...</div>
                  ) : (
                    <>
                      <div className="sg-ai-expl">{aiFixData.explanation}</div>
                      <div className="sg-ai-code">{aiFixData.fixed_code}</div>
                      <button className="sg-ai-apply" onClick={() => {
                        onApplyAIFix(aiFixData.fixed_code);
                        setAiFixData(null);
                      }}>Apply Fix</button>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <aside className="suggestions-panel">
      {/* Score */}
      <div className="sg-score-box">
        <div className="sg-score-circle" style={{ borderColor: scoreColor }}>
          {isAnalyzing ? (
            <span className="sg-analyzing">…</span>
          ) : (
            <>
              <span className="sg-score-num" style={{ color: scoreColor }}>{qualityScore}</span>
              <span className="sg-score-lbl">{scoreLabel}</span>
            </>
          )}
        </div>
        <div className="sg-score-info">
          <div className="sg-score-title">Code Quality</div>
          <div className="sg-stats-row">
            {stats.errors > 0   && <span className="sg-stat err">{stats.errors}E</span>}
            {stats.warnings > 0 && <span className="sg-stat warn">{stats.warnings}W</span>}
            {stats.info > 0     && <span className="sg-stat info">{stats.info}I</span>}
            {suggestions.length === 0 && !isAnalyzing && <span className="sg-stat ok">✓ Clean</span>}
          </div>
        </div>
      </div>

      {/* Fix All button */}
      {stats.fixable > 0 && (
        <button className="sg-fix-all-btn" onClick={onFixAll}>
          <Zap size={14} /> Fix {stats.fixable} issue{stats.fixable !== 1 ? 's' : ''} automatically
        </button>
      )}

      {/* Diff preview */}
      {diffPreview && (
        <div className="sg-diff-box">
          <div className="sg-diff-title">📋 Last Format Changes</div>
          <pre className="sg-diff-content">{diffPreview.slice(0, 600)}</pre>
        </div>
      )}

      <div className="sg-header">
        <Sparkles size={14} color="#a78bfa" />
        <span>Analysis Results</span>
        {isAnalyzing && <span className="sg-analyzing-pill">analyzing…</span>}
      </div>

      <div className="sg-list">
        {suggestions.length === 0 && !isAnalyzing ? (
          <div className="sg-empty">
            <CheckCircle size={28} color="#22c55e" />
            <p>All clear! No issues detected.</p>
          </div>
        ) : (
          <>
            {renderGroup(errors,   'error',   '🔴 Errors',   '')}
            {renderGroup(warnings, 'warning', '🟡 Warnings', '')}
            {renderGroup(infos,    'info',    '🔵 Info',     '')}
          </>
        )}
      </div>
    </aside>
  );
};

export default SuggestionsPanel;
