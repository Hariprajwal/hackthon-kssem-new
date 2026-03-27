import React, { useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';

const setupPythonSnippets = (monaco) => {
  monaco.languages.registerCompletionItemProvider('python', {
    provideCompletionItems: (model, position) => {
      // Find out if we are typing a word
      const word = model.getWordUntilPosition(position);
      const range = {
        startLineNumber: position.lineNumber,
        endLineNumber: position.lineNumber,
        startColumn: word.startColumn,
        endColumn: word.endColumn
      };

      // Advanced Tab-Stop Snippets
      const snippets = [
        { label: 'def', detail: 'Function definition', insertText: 'def ${1:function_name}(${2:args}):\n\t${3:pass}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'class', detail: 'Class definition', insertText: 'class ${1:ClassName}:\n\tdef __init__(self, ${2:args}):\n\t\t${3:pass}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'for', detail: 'For loop', insertText: 'for ${1:item} in ${2:iterable}:\n\t${3:pass}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'while', detail: 'While loop', insertText: 'while ${1:condition}:\n\t${2:pass}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'if', detail: 'If block', insertText: 'if ${1:condition}:\n\t${2:pass}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'elif', detail: 'Elif block', insertText: 'elif ${1:condition}:\n\t${2:pass}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'else', detail: 'Else block', insertText: 'else:\n\t${1:pass}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'try', detail: 'Try-except block', insertText: 'try:\n\t${1:pass}\nexcept ${2:Exception} as ${3:e}:\n\t${4:raise}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'with', detail: 'Context manager', insertText: 'with open(${1:"file.txt"}, ${2:"r"}) as ${3:f}:\n\t${4:pass}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'ifmain', detail: 'Main block', insertText: 'if __name__ == "__main__":\n\t${1:main()}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'listcomp', detail: 'List comprehension', insertText: '[${1:expr} for ${2:item} in ${3:iterable}]', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'dictcomp', detail: 'Dict comprehension', insertText: '{${1:k}: ${2:v} for ${3:item} in ${4:iterable}}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'lambda', detail: 'Lambda function', insertText: 'lambda ${1:args}: ${2:expr}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'property', detail: 'Property decorator', insertText: '@property\ndef ${1:name}(self):\n\treturn self._${1:name}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'staticmethod', detail: 'Static method', insertText: '@staticmethod\ndef ${1:name}(${2:args}):\n\t${3:pass}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'classmethod', detail: 'Class method', insertText: '@classmethod\ndef ${1:name}(cls, ${2:args}):\n\t${3:pass}', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'print', detail: 'Print statement', insertText: 'print(${1:value})', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'logger', detail: 'Logging boilerplate', insertText: 'import logging\nlogger = logging.getLogger(__name__)\nlogger.setLevel(logging.${1:INFO})', kind: monaco.languages.CompletionItemKind.Snippet },
        { label: 'asyncdef', detail: 'Async function', insertText: 'async def ${1:name}(${2:args}):\n\t${3:pass}', kind: monaco.languages.CompletionItemKind.Snippet }
      ];

      return {
        suggestions: snippets.map(s => ({ ...s, insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, range }))
      };
    }
  });
};

const EditorComponent = ({ code, onChange, markers = [], theme = 'vs-dark' }) => {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  const setupDone = useRef(false);

  const handleEditorWillMount = (monaco) => {
    if (!setupDone.current) {
      setupPythonSnippets(monaco);
      
      // Define Custom Themes
      monaco.editor.defineTheme('dracula', {
        base: 'vs-dark', inherit: true, rules: [],
        colors: { 'editor.background': '#282a36', 'editor.foreground': '#f8f8f2' }
      });
      monaco.editor.defineTheme('monokai', {
        base: 'vs-dark', inherit: true, rules: [],
        colors: { 'editor.background': '#272822', 'editor.foreground': '#f8f8f2' }
      });
      monaco.editor.defineTheme('cyberpunk', {
        base: 'vs-dark', inherit: true, rules: [],
        colors: { 'editor.background': '#03091e', 'editor.foreground': '#f0f6fc', 'editorLineNumber.foreground': '#f4007a' }
      });
      monaco.editor.defineTheme('oceanic', {
        base: 'vs-dark', inherit: true, rules: [],
        colors: { 'editor.background': '#0f1c23', 'editor.foreground': '#e0f2fe' }
      });

      setupDone.current = true;
    }
  };  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Add keyboard shortcut: Ctrl+Enter to trigger run
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      window.dispatchEvent(new CustomEvent('editor-run'));
    });
    // Ctrl+S to save
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      window.dispatchEvent(new CustomEvent('editor-save'));
    });
  };

  // Apply markers (squiggles)
  useEffect(() => {
    if (!monacoRef.current || !editorRef.current) return;
    const model = editorRef.current.getModel();
    if (!model) return;
    const monacoMarkers = markers.map(m => ({
      startLineNumber: m.line || 1,
      startColumn: m.column || 1,
      endLineNumber: m.line || 1,
      endColumn: (m.column || 1) + Math.max(20, (m.message || '').length),
      message: m.message,
      severity: m.type === 'error' ? 8 : m.type === 'warning' ? 4 : 1,
    }));
    monacoRef.current.editor.setModelMarkers(model, 'cleancodex', monacoMarkers);
  }, [markers]);

  return (
    <Editor
      height="100%"
      language="python"
      value={code}
      theme={theme}
      beforeMount={handleEditorWillMount}
      onMount={handleEditorDidMount}
      onChange={(value) => onChange(value ?? '')}
      options={{
        fontSize: 14,
        fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
        fontLigatures: true,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        padding: { top: 20 },
        suggestOnTriggerCharacters: true,
        quickSuggestions: { other: true, comments: false, strings: false },
        acceptSuggestionOnEnter: 'smart',
        tabCompletion: 'on',
        wordBasedSuggestions: 'currentDocument',
        parameterHints: { enabled: true },
        hover: { enabled: true },
        lineNumbersMinChars: 3,
        renderWhitespace: 'none',
        smoothScrolling: true,
        cursorBlinking: 'phase',
        cursorSmoothCaretAnimation: 'on',
        bracketPairColorization: { enabled: true },
        formatOnPaste: false,
      }}
    />
  );
};

export default EditorComponent;
