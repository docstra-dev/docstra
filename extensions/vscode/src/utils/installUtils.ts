// src/utils/installUtils.ts
import * as vscode from "vscode";
import * as cp from "child_process";

/**
 * Check if Docstra is installed
 */
export async function checkDocstraInstalled(): Promise<boolean> {
  return new Promise<boolean>((resolve) => {
    cp.exec("docstra --version", (error) => {
      resolve(!error);
    });
  });
}

/**
 * Install Docstra using pip
 */
export async function installDocstra(): Promise<void> {
  const terminal = vscode.window.createTerminal("Docstra Installation");
  terminal.show();
  terminal.sendText("pip install docstra");

  // Give user time to see the installation progress
  await new Promise((resolve) => setTimeout(resolve, 5000));

  // Check installation again
  const isInstalled = await checkDocstraInstalled();
  if (!isInstalled) {
    throw new Error("Docstra installation failed");
  }
}

/**
 * Ensures Docstra is installed and offers to install if it's not
 */
export async function ensureDocstraInstalled(): Promise<boolean> {
  const isInstalled = await checkDocstraInstalled();

  if (!isInstalled) {
    const shouldInstall = await vscode.window.showInformationMessage(
      "Docstra is not installed. Install it now?",
      "Yes",
      "No"
    );

    if (shouldInstall === "Yes") {
      try {
        await installDocstra();
        return true;
      } catch (error: any) {
        vscode.window.showErrorMessage(
          `Failed to install Docstra: ${error.message}`
        );
        return false;
      }
    } else {
      return false;
    }
  }

  return true;
}
