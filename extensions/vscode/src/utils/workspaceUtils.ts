// src/utils/workspaceUtils.ts
import * as vscode from "vscode";
import { cwd } from "process";

/**
 * Get the current workspace folder path
 * Falls back to the current working directory if no workspace is open
 */
export function getWorkspaceFolder(): string | undefined {
  if (
    vscode.workspace.workspaceFolders &&
    vscode.workspace.workspaceFolders.length > 0
  ) {
    return vscode.workspace.workspaceFolders[0].uri.fsPath;
  }

  // Fallback to current working directory if no workspace is open
  return cwd();
}
