# 🚀 CleanCodeX: Intelligent Agentic IDE

**Next-Gen Web-Based IDE with Real-Time AST Analysis, AI-Powered Fixes, and Integrated Python Execution.**

![CleanCodeX Dashboard](file:///C:/Users/harip/.gemini/antigravity/brain/72c6909c-e23a-4d87-b6f0-6cfb51830a0c/login_success_1774543673195.png)

---

## ✨ Features

### 🧠 Smart Analysis Engine (Version 3.0)
- **Advanced AST Parser**: 9+ structural checks (bare excepts, naming conventions, long functions, mutable defaults, and more).
- **Real-Time Debounced Linting**: Automatic analysis as you type (800ms debounce) using Pylint & AST markers.
- **Monaco Markers (Squiggles)**: Professional IDE-grade underlines for errors, warnings, and info hints.

### 🤖 AI Code Assistant
- **AI-Powered Review**: Higher-level code quality insights via OpenRouter (Gemini 2.0 Flash).
- **One-Click "Ask AI" Fixes**: Get structural explanations and code corrections for any detected issue.
- **Auto-Fix All**: Instantly resolve all safe naming convention and formatting violations.

### 💻 Professional Developer Experience
- **Monaco Editor Integration**: 60+ Python autocomplete snippets, IntelliSense, and keyboard shortcuts (`Ctrl+Enter` to Run, `Ctrl+S` to Save).
- **Integrated Terminal**: Live Python execution with stdout, stderr, and exit code tracking.
- **Beautiful UX**: Sleek glassmorphism design, code quality scoring (0-100), and a dynamic Status Bar.

---

## 🛠️ Tech Stack

- **Frontend**: React, Monaco Editor, Lucide Icons, Axios, Tailwind-inspired Vanilla CSS.
- **Backend**: FastAPI (Python), Uvicorn, Pydantic, SQLAlchemy.
- **Database**: SQLite (SQLAlchemy ORM).
- **Analysis**: AST (Abstract Syntax Trees), Pylint, Black (Formatter).
- **AI Intelligence**: OpenRouter API (Gemini 2.0 Flash).

---

## 📸 Screenshots & Demos

### 🖋️ Real-Time Intelligence
Automatic squiggles and auto-complete snippets with tab-stop navigation.
![Auto-Linting](file:///C:/Users/harip/.gemini/antigravity/brain/72c6909c-e23a-4d87-b6f0-6cfb51830a0c/code_linting_with_squiggles_1774543775056.png)

### 🐚 Integrated Console
Run Python code instantly and see live output in the built-in terminal.
![Terminal Output](file:///C:/Users/harip/.gemini/antigravity/brain/72c6909c-e23a-4d87-b6f0-6cfb51830a0c/run_output_check_1774543962020.png)

### 📽️ Full Flow Demo
![IDE Walkthrough](file:///C:/Users/harip/.gemini/antigravity/brain/72c6909c-e23a-4d87-b6f0-6cfb51830a0c/final_ide_verification_1774543610244.webp)

---

## 🚀 Quick Start (Manual Launch)

To start the full environment manually:

1. **Unified Launch**:
   ```bash
   python main.py
   ```
   *Launches Backend (8000) and Frontend (3005) simultaneously.*

2. **Separate Launch (Debug Mode)**:
   - **Backend**: `uvicorn backend.app:app --port 8000 --reload`
   - **Frontend**: `cd frontend && npm start` (Ensure `PORT=3005`)

### 🔑 Login Credentials:
- **Username**: `tester`
- **Password**: `password123`

---

## 📈 Roadmap (Version 4.0)
- [ ] AI Pull Request Generator (Summarize fixes into commit-ready PRs).
- [ ] Research Mode (Deep-dive pattern explanations with docs).
- [ ] Advanced Git Diff Explorer for Formatting.

---
Built for **KSSEM Hackathon 2026** 🏆
