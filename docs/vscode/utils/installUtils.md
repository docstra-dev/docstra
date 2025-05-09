---
language: documenttype.typescript
source_file: /Users/jorgenosberg/development/docstra/extensions/vscode/src/utils/installUtils.ts
summary: 'InstallUtils

  ================'
title: installUtils

---

# InstallUtils
================

## Overview

The `InstallUtils` module provides a set of functions for managing the installation and verification of Docstra in a Visual Studio Code (VSCode) extension.

## Implementation Details

The `InstallUtils` module relies on the following dependencies:

*   `vscode`: The VSCode API for interacting with the editor.
*   `child_process`: A Node.js module for executing system commands.
*   `path`, `os`, and `fs`: Node.js modules for working with file paths, operating system-specific functions, and file system operations.

The module consists of several key functions:

### getPythonPath

```typescript
/**
 * Get the Python executable path.
 *
 * @returns {Promise<string | null>} A promise that resolves to the Python executable path or `null` if not found.
 */
async function getPythonPath(): Promise<string | null> {
  // ...
}
```

This function attempts to find the Python executable using the `which` command. If successful, it returns the path; otherwise, it returns `null`.

### getVenvPath

```typescript
/**
 * Get the virtual environment path for the extension.
 *
 * @param {vscode.ExtensionContext} context The VSCode extension context.
 * @returns {string} The virtual environment path.
 */
function getVenvPath(context: vscode.ExtensionContext): string {
  // ...
}
```

This function determines the virtual environment path based on the extension mode. In development mode, it uses the extension's directory; otherwise, it uses a global storage URI.

### getVenvPythonPath

```typescript
/**
 * Get the Python executable path from the virtual environment.
 *
 * @param {vscode.ExtensionContext} context The VSCode extension context.
 * @returns {string} The Python executable path in the virtual environment.
 */
export function getVenvPythonPath(context: vscode.ExtensionContext): string {
  // ...
}
```

This function returns the Python executable path from the virtual environment, taking into account the operating system.

### createVenv

```typescript
/**
 * Create a virtual environment if it doesn't exist.
 *
 * @param {vscode.ExtensionContext} context The VSCode extension context.
 * @returns {Promise<void>} A promise that resolves when the virtual environment is created or already exists.
 */
async function createVenv(context: vscode.ExtensionContext): Promise<void> {
  // ...
}
```

This function creates a virtual environment if it doesn't exist. It attempts to find the Python executable and then creates the virtual environment using the `venv` command.

### checkDocstraInstalled

```typescript
/**
 * Check if Docstra is installed in the virtual environment.
 *
 * @param {vscode.ExtensionContext} context The VSCode extension context.
 * @returns {Promise<boolean>} A promise that resolves to `true` if Docstra is installed, `false` otherwise.
 */
export async function checkDocstraInstalled(context: vscode.ExtensionContext): Promise<boolean> {
  // ...
}
```

This function checks if Docstra is installed in the virtual environment by attempting to run the `docstra --version` command. If successful, it returns `true`; otherwise, it returns `false`.

### installDocstra

```typescript
/**
 * Install Docstra in the virtual environment.
 *
 * @param {vscode.ExtensionContext} context The VSCode extension context.
 * @returns {Promise<void>} A promise that resolves when the installation is complete.
 */
export async function installDocstra(context: vscode.ExtensionContext): Promise<void> {
  // ...
}
```

This function installs Docstra in the virtual environment by upgrading pip, installing Docstra with all dependencies, and verifying the installation.

### ensureDocstraInstalled

```typescript
/**
 * Ensure Docstra is installed and offer to install if it's not.
 *
 * @param {vscode.ExtensionContext} context The VSCode extension context.
 * @returns {Promise<boolean>} A promise that resolves to `true` if Docstra is installed, `false` otherwise.
 */
export async function ensureDocstraInstalled(context: vscode.ExtensionContext): Promise<boolean> {
  // ...
}
```

This function checks if Docstra is installed and offers to install it if not. It uses the `checkDocstraInstalled` function to determine the installation status.

### getDocstraPath

```typescript
/**
 * Get the path to the docstra executable in the virtual environment.
 *
 * @param {vscode.ExtensionContext} context The VSCode extension context.
 * @returns {string} The path to the docstra executable.
 */
export function getDocstraPath(context: vscode.ExtensionContext): string {
  // ...
}
```

This function returns the path to the docstra executable in the virtual environment, taking into account the operating system.

## Usage Examples

To use this module, you can import the functions and call them as needed:

```typescript
import { getPythonPath, createVenv, checkDocstraInstalled, installDocstra, ensureDocstraInstalled, getDocstraPath } from './installUtils';

// Get the Python executable path
const pythonPath = await getPythonPath();

// Create a virtual environment if it doesn't exist
await createVenv(context);

// Check if Docstra is installed
if (await checkDocstraInstalled(context)) {
  console.log('Docstra is already installed.');
} else {
  // Install Docstra
  await installDocstra(context);
}

// Ensure Docstra is installed and offer to install if it's not
const shouldInstall = await ensureDocstraInstalled(context);

// Get the path to the docstra executable
const docstraPath = getDocstraPath(context);
```

## Important Parameters, Return Values, or Side Effects

*   `getPythonPath`: Returns `null` if the Python executable is not found.
*   `createVenv`: Throws an error if the virtual environment creation fails.
*   `checkDocstraInstalled`: Returns `false` if Docstra is not installed.
*   `installDocstra`: Throws an error if the installation fails.
*   `ensureDocstraInstalled`: Offers to install Docstra if it's not already installed.

## Notes

*   This module assumes that the Python executable is available on the system.
*   The virtual environment creation process may take some time depending on the system resources.
*   The `installDocstra` function upgrades pip and installs Docstra with all dependencies.


## Source Code

```documenttype.typescript
// src/utils/installUtils.ts
import * as vscode from "vscode";
import * as cp from "child_process";
import * as path from "path";
import * as os from "os";
import * as fs from "fs";

/**
 * Get the Python executable path
 */
async function getPythonPath(): Promise<string | null> {
  return new Promise((resolve) => {
    // Try python3 first
    cp.exec("which python3", (error, stdout) => {
      if (!error) {
        resolve(stdout.trim());
        return;
      }
      // Try python as fallback
      cp.exec("which python", (error, stdout) => {
        if (!error) {
          resolve(stdout.trim());
          return;
        }
        resolve(null);
      });
    });
  });
}

/**
 * Get the virtual environment path for the extension
 */
function getVenvPath(context: vscode.ExtensionContext): string {
  // In development mode, use the extension's directory
  if (context.extensionMode === vscode.ExtensionMode.Development) {
    return path.join(context.extensionPath, ".venv");
  }
  return path.join(context.globalStorageUri.fsPath, "venv");
}

/**
 * Get the Python executable path from the virtual environment
 */
export function getVenvPythonPath(context: vscode.ExtensionContext): string {
  const venvPath = getVenvPath(context);
  return os.platform() === "win32"
    ? path.join(venvPath, "Scripts", "python.exe")
    : path.join(venvPath, "bin", "python");
}

/**
 * Create a virtual environment if it doesn't exist
 */
async function createVenv(context: vscode.ExtensionContext): Promise<void> {
  const pythonPath = await getPythonPath();
  if (!pythonPath) {
    throw new Error("Could not find Python installation");
  }

  const venvPath = getVenvPath(context);

  // In development mode, we can use fs directly
  if (context.extensionMode === vscode.ExtensionMode.Development) {
    if (!fs.existsSync(venvPath)) {
      fs.mkdirSync(venvPath, { recursive: true });
    }
  } else {
    // In production mode, use VSCode's workspace API
    try {
      await vscode.workspace.fs.createDirectory(context.globalStorageUri);
    } catch (error) {
      console.error("Failed to create global storage directory:", error);
      throw new Error("Failed to create extension storage directory");
    }
  }

  if (
    fs.existsSync(path.join(venvPath, "bin", "python")) ||
    fs.existsSync(path.join(venvPath, "Scripts", "python.exe"))
  ) {
    return; // Virtual environment already exists
  }

  // Create virtual environment
  await new Promise<void>((resolve, reject) => {
    const process = cp.spawn(pythonPath, ["-m", "venv", venvPath]);

    process.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(
          new Error(`Failed to create virtual environment with code ${code}`)
        );
      }
    });

    process.on("error", (err) => {
      reject(err);
    });
  });
}

/**
 * Check if Docstra is installed in the virtual environment
 */
export async function checkDocstraInstalled(
  context: vscode.ExtensionContext
): Promise<boolean> {
  return new Promise<boolean>(async (resolve) => {
    try {
      const venvPythonPath = getVenvPythonPath(context);

      // Try python -m docstra
      cp.exec(`${venvPythonPath} -m docstra --version`, (error) => {
        if (!error) {
          resolve(true);
          return;
        }

        // Try pip list to check if docstra is installed
        cp.exec(
          `${venvPythonPath} -m pip list | grep docstra`,
          (error, stdout) => {
            if (!error && stdout.trim()) {
              resolve(true);
              return;
            }
            resolve(false);
          }
        );
      });
    } catch (error) {
      console.error("Error checking docstra installation:", error);
      resolve(false);
    }
  });
}

/**
 * Install Docstra in the virtual environment
 */
export async function installDocstra(
  context: vscode.ExtensionContext
): Promise<void> {
  // Ensure virtual environment exists
  await createVenv(context);

  const venvPythonPath = getVenvPythonPath(context);
  const terminal = vscode.window.createTerminal("Docstra Installation");
  terminal.show();

  // First upgrade pip to ensure we have the latest version
  terminal.sendText(`${venvPythonPath} -m pip install --upgrade pip`);

  // Install docstra with all dependencies
  terminal.sendText(`${venvPythonPath} -m pip install "docstra[all]"`);

  // Give user time to see the installation progress
  await new Promise((resolve) => setTimeout(resolve, 5000));

  // Check installation again
  const isInstalled = await checkDocstraInstalled(context);
  if (!isInstalled) {
    throw new Error("Docstra installation failed");
  }

  // Verify the installation by checking the version
  try {
    const version = await new Promise<string>((resolve, reject) => {
      cp.exec(`${venvPythonPath} -m docstra --version`, (error, stdout) => {
        if (error) {
          reject(error);
          return;
        }
        resolve(stdout.trim());
      });
    });
    console.log("Installed Docstra version:", version);
  } catch (error) {
    console.error("Failed to verify docstra installation:", error);
    throw new Error("Failed to verify docstra installation");
  }
}

/**
 * Ensures Docstra is installed and offers to install if it's not
 */
export async function ensureDocstraInstalled(
  context: vscode.ExtensionContext
): Promise<boolean> {
  const isInstalled = await checkDocstraInstalled(context);

  if (!isInstalled) {
    const shouldInstall = await vscode.window.showInformationMessage(
      "Docstra is not installed. Install it now?",
      "Yes",
      "No"
    );

    if (shouldInstall === "Yes") {
      try {
        await installDocstra(context);
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

/**
 * Get the path to the docstra executable in the virtual environment
 */
export function getDocstraPath(context: vscode.ExtensionContext): string {
  const venvPath = getVenvPath(context);
  return os.platform() === "win32"
    ? path.join(venvPath, "Scripts", "docstra.exe")
    : path.join(venvPath, "bin", "docstra");
}

```
