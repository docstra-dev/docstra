---
language: documenttype.typescript
source_file: /Users/jorgenosberg/development/docstra/extensions/vscode/src/extension.ts
summary: 'Docstra Extension

  ====================='
title: extension

---

# Docstra Extension
=====================

## Overview
------------

The Docstra extension is a Visual Studio Code (VSCode) extension that provides integration with the Docstra platform. It allows users to start chats, ask about selections, and interact with the Docstra server.

## Implementation Details
-------------------------

### Activation Function

The `activate` function is the main entry point for the extension. It is called when the extension is activated in VSCode.

```typescript
/**
 * Main activation function for the extension
 */
export function activate(context: vscode.ExtensionContext) {
  console.log("Docstra extension is now active");

  // Initialize managers
  const serverManager = new ServerManager(context);
  const chatManager = new ChatManager(context, serverManager);

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand("docstra.startChat", async () => {
      try {
        // Ensure Docstra is installed and running
        const serverRunning = await serverManager.ensureDocstraRunning();
        if (!serverRunning) {
          return;
        }

        await chatManager.createNewChat();
      } catch (error: any) {
        console.error("Error starting chat:", error);
        vscode.window.showErrorMessage(
          `Docstra: Failed to start chat - ${error.message}`
        );
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("docstra.askAboutSelection", async () => {
      try {
        // Ensure Docstra is installed and running
        const serverRunning = await serverManager.ensureDocstraRunning();
        if (!serverRunning) {
          return;
        }

        await chatManager.askAboutSelection();
      } catch (error: any) {
        console.error("Error asking about selection:", error);
        vscode.window.showErrorMessage(
          `Docstra: Failed to ask about selection - ${error.message}`
        );
      }
    })
  );

  // Initialize Docstra during startup if configured to do so
  const config = vscode.workspace.getConfiguration("docstra");
  if (config.get("autoStartServer")) {
    serverManager.ensureDocstraRunning().catch(console.error);
  }
}
```

### Deactivation Function

The `deactivate` function is called when the extension is deactivated in VSCode.

```typescript
/**
 * Clean up resources when extension is deactivated
 */
export function deactivate() {
  // Clean up resources here if necessary
}
```

## Classes
------------

### ServerManager

#### Attributes

*   `context`: The VSCode extension context.

#### Methods

*   `ensureDocstraRunning()`: Ensures the Docstra server is running.
*   `createNewChat()`: Creates a new chat with the Docstra server.
*   `askAboutSelection()`: Asks about the current selection using the Docstra server.

### ChatManager

#### Attributes

*   `context`: The VSCode extension context.
*   `serverManager`: The ServerManager instance.

#### Methods

*   `createNewChat()`: Creates a new chat with the Docstra server.
*   `askAboutSelection()`: Asks about the current selection using the Docstra server.

## Functions
-------------

### activate(context: vscode.ExtensionContext)

Activates the extension and initializes the managers.

### deactivate()

Deactivates the extension and cleans up resources if necessary.

## Usage Examples
----------------

To use this extension, follow these steps:

1.  Install the extension in VSCode.
2.  Open a new file or open an existing one in VSCode.
3.  Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS) to open the Command Palette.
4.  Type "docstra.startChat" and press Enter to start a chat with Docstra.
5.  Type "docstra.askAboutSelection" and press Enter to ask about the current selection using Docstra.

## Important Dependencies
-------------------------

This extension depends on the following modules:

*   `vscode`: The VSCode API.
*   `ServerManager`: Manages the Docstra server.
*   `ChatManager`: Manages chats with the Docstra server.

## Notes
-------

*   This extension uses the `ensureDocstraRunning` method to ensure the Docstra server is running before starting a chat or asking about selections.
*   The `createNewChat` and `askAboutSelection` methods use the `serverManager` instance to interact with the Docstra server.
*   The `deactivate` function cleans up resources when the extension is deactivated.


## Source Code

```documenttype.typescript
// src/extension.ts
import * as vscode from "vscode";
import { ServerManager } from "./server/serverManager";
import { ChatManager } from "./chat/chatManager";

/**
 * Main activation function for the extension
 */
export function activate(context: vscode.ExtensionContext) {
  console.log("Docstra extension is now active");

  // Initialize managers
  const serverManager = new ServerManager(context);
  const chatManager = new ChatManager(context, serverManager);

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand("docstra.startChat", async () => {
      try {
        // Ensure Docstra is installed and running
        const serverRunning = await serverManager.ensureDocstraRunning();
        if (!serverRunning) {
          return;
        }

        await chatManager.createNewChat();
      } catch (error: any) {
        console.error("Error starting chat:", error);
        vscode.window.showErrorMessage(
          `Docstra: Failed to start chat - ${error.message}`
        );
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("docstra.askAboutSelection", async () => {
      try {
        // Ensure Docstra is installed and running
        const serverRunning = await serverManager.ensureDocstraRunning();
        if (!serverRunning) {
          return;
        }

        await chatManager.askAboutSelection();
      } catch (error: any) {
        console.error("Error asking about selection:", error);
        vscode.window.showErrorMessage(
          `Docstra: Failed to ask about selection - ${error.message}`
        );
      }
    })
  );

  // Initialize Docstra during startup if configured to do so
  const config = vscode.workspace.getConfiguration("docstra");
  if (config.get("autoStartServer")) {
    serverManager.ensureDocstraRunning().catch(console.error);
  }
}

export function deactivate() {
  // Clean up resources when extension is deactivated
}

```
