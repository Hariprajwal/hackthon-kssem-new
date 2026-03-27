import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt, QProcess, pyqtSignal, QProcessEnvironment
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor


class TerminalPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.cwd = os.path.expanduser("~")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header = QWidget()
        header.setFixedHeight(30)
        header.setStyleSheet("""
            background:#1e1e1e; 
            border-top:1px solid #333;
            border-bottom:1px solid #252526;
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 0, 8, 0)

        title = QLabel("TERMINAL")
        title.setStyleSheet("color:#bbbbbb; font-size:11px; font-weight:bold; letter-spacing:1px;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        run_hint = QLabel("Ctrl+` to toggle")
        run_hint.setStyleSheet("color:#555; font-size:11px;")
        h_layout.addWidget(run_hint)
        layout.addWidget(header)

        # Output area
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 12))
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background:#1e1e1e; color:#cccccc;
                border:none; padding:4px 8px;
            }
        """)
        self.output.setMaximumBlockCount(2000)
        layout.addWidget(self.output)

        # Input bar
        input_bar = QWidget()
        input_bar.setStyleSheet("background:#1e1e1e; border-top:1px solid #333;")
        input_layout = QHBoxLayout(input_bar)
        input_layout.setContentsMargins(8, 4, 8, 4)
        input_layout.setSpacing(6)

        self.prompt_label = QLabel(f"$ ")
        self.prompt_label.setStyleSheet("color:#569cd6; font-family:Consolas; font-size:12px;")
        input_layout.addWidget(self.prompt_label)

        self.input = QLineEdit()
        self.input.setFont(QFont("Consolas", 12))
        self.input.setStyleSheet("""
            QLineEdit {
                background:#1e1e1e; color:#d4d4d4;
                border:none; padding:2px;
            }
        """)
        self.input.returnPressed.connect(self._run_command)
        input_layout.addWidget(self.input)

        layout.addWidget(input_bar)

        # Welcome message
        self._print("Welcome to VSCode Lite Terminal\n", color="#6a9955")
        self._print(f"Working directory: {self.cwd}\n", color="#888888")
        self._print("Type commands and press Enter.\n\n", color="#888888")

    def _print(self, text: str, color: str = "#d4d4d4"):
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.insertText(text)

        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    def _run_command(self):
        cmd = self.input.text().strip()
        if not cmd:
            return
        self.input.clear()

        # If a process is already running, send the input to its standard input
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self._print(f"{cmd}\n", color="#cccccc")
            # Write exactly as input with a newline
            self.process.write((cmd + "\n").encode("utf-8"))
            return

        self._print(f"$ {cmd}\n", color="#569cd6")

        # Handle built-in commands
        if cmd.startswith("cd "):
            self._handle_cd(cmd[3:].strip())
            return
        if cmd == "clear" or cmd == "cls":
            self.output.clear()
            return

        # Run via QProcess (non-blocking)
        self.process = QProcess(self)
        self.process.setWorkingDirectory(self.cwd)

        # Optional: unbuffered python output for interactivity
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONUNBUFFERED", "1")
        self.process.setProcessEnvironment(env)

        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.finished.connect(self._process_done)

        # Update prompt to show we are running
        self.prompt_label.setText("> ")
        self.prompt_label.setStyleSheet("color:#eab308; font-family:Consolas; font-size:12px;")

        if sys.platform == "win32":
            # Just relying on cmd /c works for simple scripts but won't maintain the terminal shell. 
            self.process.start("cmd.exe", ["/c", cmd])
        else:
            self.process.start("/bin/bash", ["-c", cmd])

    def _handle_cd(self, path: str):
        target = os.path.join(self.cwd, path) if not os.path.isabs(path) else path
        target = os.path.normpath(target)
        if os.path.isdir(target):
            self.cwd = target
            self._print(f"Changed to: {self.cwd}\n", color="#6a9955")
        else:
            self._print(f"cd: no such directory: {path}\n", color="#f14c4c")

    def _read_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self._print(data, color="#d4d4d4")

    def _read_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self._print(data, color="#f14c4c")

    def _process_done(self, exit_code, exit_status):
        if exit_code != 0:
            self._print(f"\n[Exit code: {exit_code}]\n", color="#888888")
        else:
            self._print(f"\n", color="#888888")
            
        # Reset prompt
        self.prompt_label.setText("$ ")
        self.prompt_label.setStyleSheet("color:#569cd6; font-family:Consolas; font-size:12px;")
        self.process = None

    def run_file(self, file_path: str):
        """Convenience: run a Python file directly."""
        self.input.setText(f"python {file_path}")
        self._run_command()

    # ── Public helpers for programmatic output (used by Run Code) ────────────
    def append_output(self, text: str, color: str = "#d4d4d4"):
        """Append text to the output area with an optional colour."""
        self._print(text, color=color)

    def clear(self):
        """Clear all output."""
        self.output.clear()
