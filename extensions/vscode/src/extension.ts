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
  const serverManager = new ServerManager();
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
