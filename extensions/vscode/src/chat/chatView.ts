// src/chat/chatView.ts
import * as vscode from "vscode";

/**
 * Class to manage the chat webview UI
 */
export class DocstraChatView {
  public readonly panel: vscode.WebviewPanel;
  private readonly sessionId: string;
  private readonly messageHandler: (message: any) => void;

  /**
   * Create a new DocstraChatView
   */
  public static create(
    extensionUri: vscode.Uri,
    sessionId: string,
    messageHandler: (message: any) => void
  ): DocstraChatView {
    // Create panel
    const panel = vscode.window.createWebviewPanel(
      "docstraChat",
      `Docstra Chat ${sessionId.substring(0, 8)}`,
      vscode.ViewColumn.Beside,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [
          vscode.Uri.joinPath(extensionUri, "media"),
          vscode.Uri.joinPath(extensionUri, "dist"),
        ],
      }
    );

    // Create and return the view instance
    return new DocstraChatView(panel, sessionId, messageHandler);
  }

  private constructor(
    panel: vscode.WebviewPanel,
    sessionId: string,
    messageHandler: (message: any) => void
  ) {
    this.panel = panel;
    this.sessionId = sessionId;
    this.messageHandler = messageHandler;

    // Set HTML content
    this.panel.webview.html = this.getHtmlForWebview(this.panel.webview);

    // Handle messages from the webview
    this.panel.webview.onDidReceiveMessage(
      (message) => {
        this.messageHandler(message);
      },
      undefined,
      []
    );
  }

  /**
   * Post a message to the webview
   */
  public postMessage(message: any): void {
    this.panel.webview.postMessage(message);
  }

  /**
   * Get the HTML content for the webview
   */
  private getHtmlForWebview(webview: vscode.Webview): string {
    // This would typically load HTML content from your webview bundle
    // This is a simplified placeholder version
    return `<!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Docstra Chat</title>
        <style>
          body {
            padding: 0;
            margin: 0;
            font-family: var(--vscode-font-family);
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
          }
          .container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-width: 100%;
            box-sizing: border-box;
          }
          .messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
          }
          .message {
            margin-bottom: 16px;
            padding: 12px;
            border-radius: 6px;
          }
          .user {
            background-color: var(--vscode-activityBar-background);
            align-self: flex-end;
          }
          .assistant {
            background-color: var(--vscode-editor-inactiveSelectionBackground);
          }
          .system {
            background-color: var(--vscode-inputValidation-infoBackground);
            color: var(--vscode-inputValidation-infoForeground);
          }
          .error {
            background-color: var(--vscode-inputValidation-errorBackground);
            color: var(--vscode-inputValidation-errorForeground);
          }
          .input-area {
            display: flex;
            padding: 16px;
            background-color: var(--vscode-editor-background);
            border-top: 1px solid var(--vscode-widget-shadow);
          }
          #message-input {
            flex: 1;
            padding: 8px;
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
          }
          button {
            margin-left: 8px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
          }
          button:hover {
            background-color: var(--vscode-button-hoverBackground);
          }
          .context-area {
            margin-bottom: 16px;
            padding: 8px;
            background-color: var(--vscode-editor-lineHighlightBackground);
            border-left: 3px solid var(--vscode-activityBarBadge-background);
            font-family: var(--vscode-editor-font-family);
            font-size: var(--vscode-editor-font-size);
            white-space: pre-wrap;
            overflow-x: auto;
          }
          .context-title {
            font-weight: bold;
            margin-bottom: 8px;
          }
          .status-bar {
            padding: 4px 16px;
            font-size: 12px;
            background-color: var(--vscode-statusBar-background);
            color: var(--vscode-statusBar-foreground);
          }
          .connected {
            color: var(--vscode-testing-iconPassed);
          }
          .disconnected {
            color: var(--vscode-testing-iconFailed);
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="status-bar">
            <span id="connection-status">Connecting...</span>
          </div>
          <div id="messages" class="messages"></div>
          <div class="input-area">
            <textarea id="message-input" placeholder="Type your message..."></textarea>
            <button id="send-button">Send</button>
            <button id="context-button">Add Code</button>
          </div>
        </div>
        <script>
          (function() {
            const vscode = acquireVsCodeApi();
            const messagesContainer = document.getElementById('messages');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            const contextButton = document.getElementById('context-button');
            const connectionStatus = document.getElementById('connection-status');
            
            // Send message
            function sendMessage() {
              const text = messageInput.value.trim();
              if (text) {
                vscode.postMessage({
                  command: 'sendMessage',
                  text: text
                });
                messageInput.value = '';
              }
            }
            
            // Add message to UI
            function addMessage(role, content) {
              const messageDiv = document.createElement('div');
              messageDiv.className = \`message \${role}\`;
              messageDiv.textContent = content;
              messagesContainer.appendChild(messageDiv);
              messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            // Add code context
            function addContext(filePath, selection) {
              const contextDiv = document.createElement('div');
              contextDiv.className = 'context-area';
              
              const titleDiv = document.createElement('div');
              titleDiv.className = 'context-title';
              titleDiv.textContent = \`Context from \${filePath}\`;
              
              const codeDiv = document.createElement('pre');
              codeDiv.textContent = selection;
              
              contextDiv.appendChild(titleDiv);
              contextDiv.appendChild(codeDiv);
              messagesContainer.appendChild(contextDiv);
              messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            // Update connection status
            function updateConnectionStatus(status, message) {
              connectionStatus.className = status;
              switch (status) {
                case 'connected':
                  connectionStatus.textContent = 'Connected';
                  break;
                case 'disconnected':
                  connectionStatus.textContent = 'Disconnected';
                  break;
                case 'error':
                  connectionStatus.textContent = message || 'Connection Error';
                  break;
                default:
                  connectionStatus.textContent = 'Connecting...';
              }
            }
            
            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            
            messageInput.addEventListener('keydown', (e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            });
            
            contextButton.addEventListener('click', () => {
              vscode.postMessage({
                command: 'getContext'
              });
            });
            
            // Handle messages from the extension
            window.addEventListener('message', (event) => {
              const message = event.data;
              
              switch (message.command) {
                case 'addMessage':
                  addMessage(message.message.role, message.message.content);
                  break;
                case 'addContext':
                  addContext(message.context.filePath, message.context.selection);
                  break;
                case 'connectionStatus':
                  updateConnectionStatus(message.status, message.message);
                  break;
                case 'error':
                  addMessage('error', message.message);
                  break;
              }
            });
          }());
        </script>
      </body>
      </html>`;
  }
}
