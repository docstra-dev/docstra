---
language: documenttype.typescript
source_file: /Users/jorgenosberg/development/docstra/extensions/vscode/src/chat/chatManager.ts
summary: 'Chat Manager

  ================'
title: chatManager

---

Chat Manager
================

Overview
--------

The Chat Manager is a class responsible for managing chat sessions between the user and the Docstra assistant. It handles creating new chats, sending messages, adding code context, and reconnecting to the WebSocket server.

Implementation Details
---------------------

The Chat Manager uses the following dependencies:

* `vscode`: The Visual Studio Code API for interacting with the editor.
* `axios`: A library for making HTTP requests to the Docstra API.
* `ws`: A library for working with WebSockets.
* `path`: A built-in Node.js module for working with file paths.

The Chat Manager uses a map to store chat sessions, where each session is identified by its unique ID. When a new chat is created, a new entry is added to the map with the current session's attributes.

Usage Examples
--------------

To create a new chat session:

```typescript
const chatManager = new ChatManager(context, serverManager);
const newChatPanel = await chatManager.createNewChat();
```

To send a message in an existing chat session:

```typescript
const chatPanel = this.chatPanels.get(sessionId)!;
chatPanel.view.postMessage({
  command: "addMessage",
  message: {
    role: "user",
    content: "Hello, Docstra!"
  }
});
```

Classes
-------

### ChatManager

#### Attributes

* `chatPanels`: A map of chat sessions, where each session is identified by its unique ID.
* `context`: The Visual Studio Code extension context.
* `serverManager`: An instance of the Server Manager class.

#### Methods

##### createNewChat()

Creates a new chat session and returns it as a `ChatPanel` object. If the user has not opened a workspace folder, an error message is displayed.

```typescript
public async createNewChat(): Promise<ChatPanel | undefined> {
  // ...
}
```

##### askAboutSelection()

Asks the user about their current code selection and creates a new chat session if necessary. The user can choose to use an existing chat or create a new one.

```typescript
public async askAboutSelection() {
  // ...
}
```

##### sendChatMessage(chatPanel: ChatPanel, text: string)

Sends a message in the specified chat panel. If the WebSocket connection is lost, the message is sent via HTTP instead.

```typescript
private async sendChatMessage(chatPanel: ChatPanel, text: string) {
  // ...
}
```

##### addCodeContext(chatPanel: ChatPanel)

Adds code context to the specified chat panel and notifies the user that the context has been added.

```typescript
private addCodeContext(chatPanel: ChatPanel) {
  // ...
}
```

##### connectWebSocket(chatPanel: ChatPanel)

Connects to the WebSocket server with improved error handling. If the connection is lost, the session is recreated.

```typescript
private async connectWebSocket(chatPanel: ChatPanel) {
  // ...
}
```

##### recreateSession(chatPanel: ChatPanel)

Recreates a chat session when the connection to the WebSocket server is lost.

```typescript
private async recreateSession(chatPanel: ChatPanel) {
  // ...
}
```

Functions
---------

### `createNewChat()`

Creates a new chat session and returns it as a `ChatPanel` object. If the user has not opened a workspace folder, an error message is displayed.

#### Parameters

* None

#### Return Value

A `ChatPanel` object representing the newly created chat session.

#### Purpose

Creates a new chat session and initializes its attributes.

### `askAboutSelection()`

Asks the user about their current code selection and creates a new chat session if necessary. The user can choose to use an existing chat or create a new one.

#### Parameters

None

#### Return Value

None

#### Purpose

Asks the user about their current code selection and creates a new chat session if necessary.

### `sendChatMessage(chatPanel: ChatPanel, text: string)`

Sends a message in the specified chat panel. If the WebSocket connection is lost, the message is sent via HTTP instead.

#### Parameters

* `chatPanel`: The chat panel to send the message to.
* `text`: The message to send.

#### Return Value

None

#### Purpose

Sends a message in the specified chat panel and handles any errors that may occur during transmission.

### `addCodeContext(chatPanel: ChatPanel)`

Adds code context to the specified chat panel and notifies the user that the context has been added.

#### Parameters

* `chatPanel`: The chat panel to add code context to.

#### Return Value

None

#### Purpose

Adds code context to the specified chat panel and notifies the user that the context has been added.

### `connectWebSocket(chatPanel: ChatPanel)`

Connects to the WebSocket server with improved error handling. If the connection is lost, the session is recreated.

#### Parameters

* `chatPanel`: The chat panel to connect to the WebSocket server for.

#### Return Value

None

#### Purpose

Connects to the WebSocket server and handles any errors that may occur during transmission.

### `recreateSession(chatPanel: ChatPanel)`

Recreates a chat session when the connection to the WebSocket server is lost.

#### Parameters

* `chatPanel`: The chat panel to recreate the session for.

#### Return Value

None

#### Purpose

Recreates a chat session when the connection to the WebSocket server is lost.


## Source Code

```documenttype.typescript
// src/chat/chatManager.ts
import * as vscode from "vscode";
import * as path from "path";
import WebSocket from "ws";
import axios from "axios";
import { DocstraChatView } from "./chatView";
import { ServerManager } from "../server/serverManager";
import { getWorkspaceFolder } from "../utils/workspaceUtils";

// Chat panel type definition
export interface ChatPanel {
  view: DocstraChatView;
  sessionId: string;
  disposables: vscode.Disposable[];
  socket: WebSocket | null;
  reconnectAttempts: number;
}

export class ChatManager {
  private chatPanels = new Map<string, ChatPanel>();
  private context: vscode.ExtensionContext;
  private serverManager: ServerManager;

  constructor(context: vscode.ExtensionContext, serverManager: ServerManager) {
    this.context = context;
    this.serverManager = serverManager;
  }

  /**
   * Creates a new chat session
   */
  public async createNewChat(): Promise<ChatPanel | undefined> {
    try {
      const workspaceFolder = getWorkspaceFolder();
      if (!workspaceFolder) {
        vscode.window.showErrorMessage("Docstra: No workspace folder is open");
        return undefined;
      }

      const apiUrl = this.serverManager.getApiUrl();
      const response = await axios.post(`${apiUrl}/sessions/create`, {
        working_dir: workspaceFolder,
      });

      const sessionId = response.data.session_id;

      // Create new chat view
      const chatView = DocstraChatView.create(
        this.context.extensionUri,
        sessionId,
        async (message) => {
          await this.handleViewMessage(chatPanel, message);
        }
      );

      // Initialize chat panel
      const chatPanel: ChatPanel = {
        view: chatView,
        sessionId,
        disposables: [],
        socket: null,
        reconnectAttempts: 0,
      };

      // Set up WebSocket connection
      await this.connectWebSocket(chatPanel);

      // Store chat panel
      this.chatPanels.set(sessionId, chatPanel);

      // Handle panel disposal
      chatView.panel.onDidDispose(
        () => {
          chatPanel.disposables.forEach((d) => d.dispose());
          if (chatPanel.socket) {
            chatPanel.socket.close();
          }
          this.chatPanels.delete(sessionId);

          // Clean up session on backend
          axios
            .delete(`${this.serverManager.getApiUrl()}/sessions/${sessionId}`)
            .catch(console.error);
        },
        null,
        chatPanel.disposables
      );

      // Initial greeting
      chatView.postMessage({
        command: "addMessage",
        message: {
          role: "assistant",
          content:
            "Hello! I'm Docstra assistant. How can I help you understand your code today?",
        },
      });

      return chatPanel;
    } catch (error: any) {
      console.error("Error creating chat:", error);
      vscode.window.showErrorMessage(
        `Docstra: Failed to create chat - ${error.message}`
      );
      return undefined;
    }
  }

  /**
   * Handle messages from the webview
   */
  private async handleViewMessage(chatPanel: ChatPanel, message: any) {
    switch (message.command) {
      case "sendMessage":
        await this.sendChatMessage(chatPanel, message.text);
        break;
      case "getContext":
        await this.addCodeContext(chatPanel);
        break;
      case "closeChat":
        chatPanel.view.panel.dispose();
        break;
    }
  }

  /**
   * Ask about the currently selected code
   */
  public async askAboutSelection() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage("Docstra: No active editor");
      return;
    }

    const selection = editor.selection;
    if (selection.isEmpty) {
      vscode.window.showErrorMessage("Docstra: No code selected");
      return;
    }

    const text = editor.document.getText(selection);
    const filePath = editor.document.uri.fsPath;

    // Ask for the question
    const question = await vscode.window.showInputBox({
      prompt: "What would you like to know about this code?",
      placeHolder: "E.g., What does this function do?",
    });

    if (!question) {
      return;
    }

    // Create a new chat or use existing
    let chatPanel: ChatPanel;
    if (this.chatPanels.size > 0) {
      const answer = await vscode.window.showQuickPick(
        ["New Chat", "Existing Chat"],
        {
          placeHolder: "Use existing chat or create a new one?",
        }
      );

      if (answer === "Existing Chat") {
        // If only one chat, use it; otherwise let user pick
        if (this.chatPanels.size === 1) {
          chatPanel = Array.from(this.chatPanels.values())[0];
        } else {
          const sessions = Array.from(this.chatPanels.entries()).map(
            ([id, panel]) => ({
              label: `Chat Session ${id.substring(0, 8)}...`,
              sessionId: id,
            })
          );

          const selected = await vscode.window.showQuickPick(sessions, {
            placeHolder: "Select a chat session",
          });

          if (!selected) {
            return;
          }

          chatPanel = this.chatPanels.get(selected.sessionId)!;
        }

        // Focus existing panel
        chatPanel.view.panel.reveal();
      } else {
        // Create new chat
        const newChatPanel = await this.createNewChat();
        if (!newChatPanel) {
          return;
        }
        chatPanel = newChatPanel;
      }
    } else {
      // Create new chat
      const newChatPanel = await this.createNewChat();
      if (!newChatPanel) {
        return;
      }
      chatPanel = newChatPanel;
    }

    try {
      const workspaceFolder = getWorkspaceFolder();
      if (!workspaceFolder) {
        vscode.window.showErrorMessage("Docstra: No workspace folder is open");
        return;
      }

      const relativePath = path.relative(workspaceFolder, filePath);

      // Add context to the session
      const apiUrl = this.serverManager.getApiUrl();
      await axios.post(`${apiUrl}/sessions/${chatPanel.sessionId}/context`, {
        file_path: relativePath,
        content: text,
        selection_range: {
          startLine: selection.start.line,
          endLine: selection.end.line,
        },
      });

      // Send the user's question
      this.sendChatMessage(chatPanel, question);

      // Notify the webview to add the context
      chatPanel.view.postMessage({
        command: "addContext",
        context: {
          filePath: relativePath,
          selection: text,
        },
      });
    } catch (error: any) {
      console.error("Error adding context:", error);
      vscode.window.showErrorMessage(
        `Docstra: Failed to add context - ${error.message}`
      );
    }
  }

  /**
   * Send a chat message to the server
   */
  private async sendChatMessage(chatPanel: ChatPanel, text: string) {
    try {
      if (chatPanel.socket && chatPanel.socket.readyState === WebSocket.OPEN) {
        // Send directly via WebSocket
        chatPanel.socket.send(text);

        // Update webview with user message
        chatPanel.view.postMessage({
          command: "addMessage",
          message: {
            role: "user",
            content: text,
          },
        });
      } else {
        // Fallback to HTTP
        const apiUrl = this.serverManager.getApiUrl();
        const response = await axios.post(
          `${apiUrl}/sessions/${chatPanel.sessionId}/message`,
          {
            content: text,
          }
        );

        // Update webview with user message first (for better UX)
        chatPanel.view.postMessage({
          command: "addMessage",
          message: {
            role: "user",
            content: text,
          },
        });

        // Then update with assistant response
        chatPanel.view.postMessage({
          command: "addMessage",
          message: {
            role: "assistant",
            content: response.data.response,
          },
        });
      }
    } catch (error: any) {
      console.error("Error sending message:", error);
      chatPanel.view.postMessage({
        command: "error",
        message: `Failed to send message: ${error.message}`,
      });
    }
  }

  /**
   * Add code context to the chat
   */
  private async addCodeContext(chatPanel: ChatPanel) {
    try {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showInformationMessage(
          "Docstra: No active editor to get context from"
        );
        return;
      }

      const document = editor.document;
      const selection = editor.selection;

      // Get workspace folder to calculate relative path
      const workspaceFolder = getWorkspaceFolder();
      if (!workspaceFolder) {
        vscode.window.showErrorMessage("Docstra: No workspace folder is open");
        return;
      }

      const filePath = document.uri.fsPath;
      const relativePath = path.relative(workspaceFolder, filePath);

      // Get selected text or entire file
      const text = selection.isEmpty
        ? document.getText()
        : document.getText(selection);

      // Add context to the session
      const apiUrl = this.serverManager.getApiUrl();
      await axios.post(`${apiUrl}/sessions/${chatPanel.sessionId}/context`, {
        file_path: relativePath,
        content: text,
        selection_range: selection.isEmpty
          ? null
          : {
              startLine: selection.start.line,
              endLine: selection.end.line,
            },
      });

      // Notify the webview
      chatPanel.view.postMessage({
        command: "addContext",
        context: {
          filePath: relativePath,
          selection: text,
        },
      });

      vscode.window.showInformationMessage(
        `Docstra: Added context from ${relativePath}`
      );
    } catch (error: any) {
      console.error("Error adding context:", error);
      vscode.window.showErrorMessage(
        `Docstra: Failed to add context - ${error.message}`
      );
    }
  }

  /**
   * Connect to the WebSocket server with improved error handling
   */
  private async connectWebSocket(chatPanel: ChatPanel) {
    const maxReconnectAttempts = 5;
    const baseDelay = 1000;
    const apiBaseUrl = this.serverManager.getApiUrl();

    // First verify session exists on server
    try {
      const response = await axios.get(
        `${apiBaseUrl}/sessions/${chatPanel.sessionId}`
      );
      if (!response.data || !response.data.session_id) {
        console.error("Session not found on server");

        // Try to recreate the session if this is a reconnection attempt
        if (chatPanel.reconnectAttempts > 0) {
          await this.recreateSession(chatPanel);
          return;
        }
      }
    } catch (error) {
      console.error("Error checking session:", error);

      // Try to recreate the session if this is a reconnection attempt
      if (chatPanel.reconnectAttempts > 0) {
        await this.recreateSession(chatPanel);
        return;
      }
    }

    const url =
      apiBaseUrl.replace("http", "ws") +
      `/sessions/${chatPanel.sessionId}/stream`;

    try {
      const socket = new WebSocket(url);
      let pingInterval: NodeJS.Timeout;

      socket.on("open", () => {
        console.log(`WebSocket connected for session ${chatPanel.sessionId}`);
        // Reset reconnect attempts on successful connection
        chatPanel.reconnectAttempts = 0;

        chatPanel.view.postMessage({
          command: "connectionStatus",
          status: "connected",
        });

        // Set up ping interval to keep connection alive
        pingInterval = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            socket.ping();
          }
        }, 30000);
      });

      socket.on("message", (data) => {
        try {
          const parsedData = JSON.parse(data.toString());

          if (parsedData.type === "response") {
            chatPanel.view.postMessage({
              command: "addMessage",
              message: {
                role: "assistant",
                content: parsedData.content,
              },
            });
          } else if (parsedData.type === "error") {
            chatPanel.view.postMessage({
              command: "error",
              message: parsedData.message,
            });
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      });

      socket.on("error", (error) => {
        console.error(
          `WebSocket error for session ${chatPanel.sessionId}:`,
          error
        );
        chatPanel.view.postMessage({
          command: "connectionStatus",
          status: "error",
          message: "WebSocket connection error",
        });
      });

      socket.on("close", async () => {
        console.log(`WebSocket closed for session ${chatPanel.sessionId}`);
        // Clear ping interval
        clearInterval(pingInterval);

        chatPanel.view.postMessage({
          command: "connectionStatus",
          status: "disconnected",
        });

        // Try to reconnect with exponential backoff
        if (chatPanel.reconnectAttempts < maxReconnectAttempts) {
          const delay = baseDelay * Math.pow(2, chatPanel.reconnectAttempts);
          chatPanel.reconnectAttempts++;

          console.log(
            `Attempting to reconnect in ${delay}ms (attempt ${chatPanel.reconnectAttempts}/${maxReconnectAttempts})`
          );

          setTimeout(async () => {
            if (this.chatPanels.has(chatPanel.sessionId)) {
              await this.connectWebSocket(chatPanel);
            }
          }, delay);
        } else {
          console.log("Max reconnection attempts reached");
          chatPanel.view.postMessage({
            command: "error",
            message: "Connection lost. Creating a new session...",
          });

          // Try to create a new session
          await this.recreateSession(chatPanel);
        }
      });

      chatPanel.socket = socket;
    } catch (error) {
      console.error("Error connecting WebSocket:", error);

      // Try to create a new session if this is a reconnection attempt
      if (chatPanel.reconnectAttempts > 0) {
        await this.recreateSession(chatPanel);
      }
    }
  }

  /**
   * Recreate a session when connection fails
   */
  private async recreateSession(chatPanel: ChatPanel) {
    try {
      console.log("Creating a new session after connection failures");

      // Create a new session
      const apiUrl = this.serverManager.getApiUrl();
      const workspaceFolder = getWorkspaceFolder();
      if (!workspaceFolder) {
        throw new Error("No workspace folder open");
      }

      const response = await axios.post(`${apiUrl}/sessions/create`, {
        working_dir: workspaceFolder,
      });

      const newSessionId = response.data.session_id;
      const oldSessionId = chatPanel.sessionId;

      // Update the panel with the new session ID
      this.chatPanels.delete(oldSessionId);
      chatPanel.sessionId = newSessionId;
      chatPanel.reconnectAttempts = 0;
      this.chatPanels.set(newSessionId, chatPanel);

      // Notify user
      chatPanel.view.postMessage({
        command: "addMessage",
        message: {
          role: "system",
          content:
            "Connection re-established with a new session. Previous messages are not available.",
        },
      });

      // Connect with the new session
      await this.connectWebSocket(chatPanel);
    } catch (error: any) {
      console.error("Failed to recreate session:", error);
      chatPanel.view.postMessage({
        command: "error",
        message: `Could not create a new session: ${error.message}`,
      });
    }
  }
}

```
