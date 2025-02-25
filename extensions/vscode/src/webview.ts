import * as vscode from "vscode";
import * as path from "path";

/**
 * Manages the webview panel for Docstra chat
 */
export class DocstraChatView {
  public static readonly viewType = "docstraChat";

  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionUri: vscode.Uri;
  private _disposables: vscode.Disposable[] = [];

  private _sessionId: string;
  private _onMessage: (message: any) => void;

  /**
   * Creates a new DocstraChatView
   */
  public static create(
    extensionUri: vscode.Uri,
    sessionId: string,
    onMessage: (message: any) => void
  ): DocstraChatView {
    const panel = vscode.window.createWebviewPanel(
      DocstraChatView.viewType,
      "Docstra Chat",
      vscode.ViewColumn.Beside,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [
          vscode.Uri.file(path.join(extensionUri.fsPath, "media")),
        ],
      }
    );

    return new DocstraChatView(panel, extensionUri, sessionId, onMessage);
  }

  /**
   * Private constructor - use DocstraChatView.create instead
   */
  private constructor(
    panel: vscode.WebviewPanel,
    extensionUri: vscode.Uri,
    sessionId: string,
    onMessage: (message: any) => void
  ) {
    this._panel = panel;
    this._extensionUri = extensionUri;
    this._sessionId = sessionId;
    this._onMessage = onMessage;

    // Set initial HTML content
    this._update();

    // Listen for when the panel is disposed
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

    // Handle messages from the webview
    this._panel.webview.onDidReceiveMessage(
      (message) => this._onMessage(message),
      null,
      this._disposables
    );
  }

  /**
   * Gets the underlying webview panel
   */
  public get panel(): vscode.WebviewPanel {
    return this._panel;
  }

  /**
   * Gets the webview
   */
  public get webview(): vscode.Webview {
    return this._panel.webview;
  }

  /**
   * Gets the session ID
   */
  public get sessionId(): string {
    return this._sessionId;
  }

  /**
   * Sends a message to the webview
   */
  public postMessage(message: any): void {
    this._panel.webview.postMessage(message);
  }

  /**
   * Updates the content of the webview
   */
  private _update() {
    this._panel.webview.html = this._getHtmlForWebview();
  }

  /**
   * Generates HTML for the webview
   */
  private _getHtmlForWebview(): string {
    // Local path to media resources
    const mediaPath = path.join(this._extensionUri.fsPath, "media");

    // Create URI for media files
    const mediaUri = (fileName: string) =>
      this._panel.webview.asWebviewUri(
        vscode.Uri.file(path.join(mediaPath, fileName))
      );

    return /*html*/ `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Docstra Chat</title>
        <style>
          body {
            font-family: var(--vscode-font-family);
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
          }
          
          #chat-header {
            padding: 8px 12px;
            background-color: var(--vscode-editor-background);
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
          }
          
          #messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
          }
          
          .message {
            margin-bottom: 16px;
            display: flex;
            flex-direction: column;
          }
          
          .message-header {
            font-weight: bold;
            margin-bottom: 4px;
          }
          
          .message-content {
            padding: 8px 12px;
            border-radius: 4px;
            max-width: 85%;
          }
          
          .user-message {
            align-self: flex-end;
          }
          
          .user-message .message-content {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
          }
          
          .assistant-message {
            align-self: flex-start;
          }
          
          .assistant-message .message-content {
            background-color: var(--vscode-editor-inactiveSelectionBackground);
          }
          
          .system-message {
            align-self: center;
            font-style: italic;
            opacity: 0.7;
          }
          
          #input-container {
            display: flex;
            padding: 12px;
            border-top: 1px solid var(--vscode-panel-border);
          }
          
          #message-input {
            flex: 1;
            padding: 8px;
            border: 1px solid var(--vscode-input-border);
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border-radius: 4px;
          }
          
          #send-button {
            margin-left: 8px;
            padding: 8px 16px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
          }
          
          #send-button:hover {
            background-color: var(--vscode-button-hoverBackground);
          }
          
          #context-button {
            padding: 6px 12px;
            background-color: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
          }
          
          #context-button:hover {
            background-color: var(--vscode-button-secondaryHoverBackground);
          }
          
          .connection-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 6px;
          }
          
          .connected {
            background-color: #4CAF50;
          }
          
          .disconnected {
            background-color: #F44336;
          }
          
          .error {
            color: var(--vscode-errorForeground);
            text-align: center;
            margin: 8px 0;
          }
          
          /* Markdown styling */
          .markdown code {
            font-family: var(--vscode-editor-font-family);
            background-color: var(--vscode-textCodeBlock-background);
            padding: 2px 4px;
            border-radius: 3px;
          }
          
          .markdown pre {
            background-color: var(--vscode-textCodeBlock-background);
            padding: 8px;
            border-radius: 4px;
            overflow-x: auto;
          }
          
          .markdown h1, .markdown h2, .markdown h3, 
          .markdown h4, .markdown h5, .markdown h6 {
            margin-top: 16px;
            margin-bottom: 8px;
          }
          
          .markdown p {
            margin: 8px 0;
          }
          
          .markdown ul, .markdown ol {
            padding-left: 24px;
          }
        </style>
      </head>
      <body>
        <div id="chat-header">
          <h3>Docstra Chat</h3>
          <div>
            <span id="connection-status">
              <span class="connection-indicator disconnected"></span>
              Disconnected
            </span>
            <button id="context-button">Add Current File</button>
          </div>
        </div>
        
        <div id="messages-container"></div>
        
        <div id="input-container">
          <textarea id="message-input" placeholder="Ask a question..." rows="2"></textarea>
          <button id="send-button">Send</button>
        </div>
        
        <script>
          // Setup variables
          const vscode = acquireVsCodeApi();
          const messagesContainer = document.getElementById('messages-container');
          const messageInput = document.getElementById('message-input');
          const sendButton = document.getElementById('send-button');
          const contextButton = document.getElementById('context-button');
          const connectionStatus = document.getElementById('connection-status');
          
          // Add system message on startup
          addMessage({
            role: 'system',
            content: 'Chat session started. Type a message to begin.'
          });
          
          // Event listeners
          sendButton.addEventListener('click', () => {
            const text = messageInput.value.trim();
            if (text) {
              vscode.postMessage({
                command: 'sendMessage',
                text: text
              });
              messageInput.value = '';
            }
          });
          
          messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendButton.click();
            }
          });
          
          contextButton.addEventListener('click', () => {
            vscode.postMessage({
              command: 'getContext'
            });
          });
          
          // Handle incoming messages
          window.addEventListener('message', (event) => {
            const message = event.data;
            
            switch (message.command) {
              case 'addMessage':
                addMessage(message.message);
                break;
                
              case 'addContext':
                addSystemMessage(\`Added context from "\${message.context.filePath}"\`);
                break;
                
              case 'connectionStatus':
                updateConnectionStatus(message.status, message.message);
                break;
                
              case 'error':
                showError(message.message);
                break;
            }
          });
          
          // Helper functions
          function addMessage(message) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message');
            
            if (message.role === 'user') {
              messageElement.classList.add('user-message');
              messageElement.innerHTML = \`
                <div class="message-header">You</div>
                <div class="message-content">\${escapeHtml(message.content)}</div>
              \`;
            } else if (message.role === 'assistant') {
              messageElement.classList.add('assistant-message');
              messageElement.innerHTML = \`
                <div class="message-header">Docstra</div>
                <div class="message-content markdown">\${markdownToHtml(message.content)}</div>
              \`;
            } else if (message.role === 'system') {
              messageElement.classList.add('system-message');
              messageElement.textContent = message.content;
            }
            
            messagesContainer.appendChild(messageElement);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
          }
          
          function addSystemMessage(text) {
            addMessage({ role: 'system', content: text });
          }
          
          function updateConnectionStatus(status, message) {
            const indicator = connectionStatus.querySelector('.connection-indicator');
            
            if (status === 'connected') {
              indicator.classList.remove('disconnected');
              indicator.classList.add('connected');
              connectionStatus.textContent = '';
              connectionStatus.appendChild(indicator);
              connectionStatus.appendChild(document.createTextNode('Connected'));
            } else {
              indicator.classList.remove('connected');
              indicator.classList.add('disconnected');
              connectionStatus.textContent = '';
              connectionStatus.appendChild(indicator);
              connectionStatus.appendChild(document.createTextNode('Disconnected'));
              
              if (message) {
                showError(message);
              }
            }
          }
          
          function showError(message) {
            const errorElement = document.createElement('div');
            errorElement.classList.add('error');
            errorElement.textContent = message;
            messagesContainer.appendChild(errorElement);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
          }
          
          function escapeHtml(text) {
            return text
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;')
              .replace(/\\n/g, '<br>');
          }
          
          function markdownToHtml(markdown) {
            // Very simple markdown converter
            // Convert code blocks
            let html = markdown.replace(/\`\`\`([\\s\\S]*?)\`\`\`/g, (match, code) => {
              return \`<pre><code>\${escapeHtml(code.trim())}</code></pre>\`;
            });
            
            // Convert inline code
            html = html.replace(/\`([^\`]+)\`/g, '<code>$1</code>');
            
            // Convert headings
            html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
            html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
            html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');
            
            // Convert lists
            html = html.replace(/^\\* (.*$)/gm, '<li>$1</li>');
            html = html.replace(/^- (.*$)/gm, '<li>$1</li>');
            html = html.replace(/^(\\d+)\\. (.*$)/gm, '<li>$2</li>');
            
            // Wrap lists
            html = html.replace(/<li>.*<\\/li>/g, (match) => {
              return \`<ul>\${match}</ul>\`;
            });
            
            // Convert paragraphs
            html = html.replace(/^(?!<[a-z])(.*$)/gm, (match, text) => {
              if (text.trim() === '') return '';
              return \`<p>\${text}</p>\`;
            });
            
            // Convert line breaks
            html = html.replace(/\\n/g, '<br>');
            
            return html;
          }
        </script>
      </body>
      </html>
    `;
  }

  /**
   * Disposes of the view and its resources
   */
  public dispose() {
    // Clean up our resources
    this._panel.dispose();

    while (this._disposables.length) {
      const x = this._disposables.pop();
      if (x) {
        x.dispose();
      }
    }
  }
}
