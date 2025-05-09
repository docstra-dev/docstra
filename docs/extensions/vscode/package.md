---
language: documenttype.other
source_file: /Users/jorgenosberg/development/docstra/extensions/vscode/package.json
summary: 'Docstra Extension for VS Code

  ====================================='
title: package

---

# Docstra Extension for VS Code
=====================================

## Overview
------------

The `package.json` file is the main configuration file for the Docstra extension in VS Code. It defines the metadata, dependencies, and functionality of the extension.

## Implementation Details
------------------------

The extension uses the following technologies:

*   **VS Code API**: The extension interacts with VS Code using its API to provide features such as command execution, menu contribution, and configuration management.
*   **Docstra API**: The extension communicates with the Docstra API server to retrieve data and send requests.

## Usage Examples
-----------------

### Starting a Chat

To start a chat, use the `docstra.startChat` command:

```json
{
  "command": "docstra.startChat",
  "title": "Docstra: Start Chat"
}
```

### Asking About Selected Code

To ask about selected code, use the `docstra.askAboutSelection` command:

```json
{
  "when": "editorHasSelection",
  "command": "docstra.askAboutSelection",
  "group": "docstra"
}
```

## Configuration
--------------

The extension provides a configuration object that can be accessed through the VS Code API. The configuration includes:

*   **`docstra.apiUrl`**: The URL of the Docstra API server.
*   **`docstra.autoStartServer`**: A boolean indicating whether to automatically start the Docstra server when VS Code starts.

```json
{
  "configuration": {
    "title": "Docstra",
    "properties": {
      "docstra.apiUrl": {
        "type": "string",
        "default": "http://localhost:8000",
        "description": "URL of the Docstra API server"
      },
      "docstra.autoStartServer": {
        "type": "boolean",
        "default": true,
        "description": "Automatically start the Docstra server when VS Code starts"
      }
    }
  }
}
```

## Dependencies
--------------

The extension depends on the following modules:

*   **`@types/mocha`**: A type definition for Mocha testing framework.
*   **`@types/node`**: A type definition for Node.js.
*   **`@types/vscode`**: A type definition for VS Code API.
*   **`@typescript-eslint/eslint-plugin`**: An ESLint plugin for TypeScript.
*   **`@typescript-eslint/parser`**: A parser for TypeScript.
*   **`esbuild`**: A fast and efficient bundler.
*   **`eslint`**: A linter for JavaScript code.
*   **`npm-run-all`**: A utility for running multiple npm scripts concurrently.
*   **`typescript`**: A superset of JavaScript that adds optional static typing.

```json
{
  "devDependencies": {
    "@types/mocha": "^10.0.10",
    "@types/node": "20.x",
    "@types/vscode": "^1.97.0",
    "@typescript-eslint/eslint-plugin": "^8.22.0",
    "@typescript-eslint/parser": "^8.22.0",
    "@vscode/test-cli": "^0.0.10",
    "@vscode/test-electron": "^2.4.1",
    "esbuild": "^0.24.2",
    "eslint": "^9.19.0",
    "npm-run-all": "^4.1.5",
    "typescript": "^5.7.3"
  }
}
```

## Scripts
------------

The extension uses the following scripts:

*   **`vscode:prepublish`**: A script that runs before publishing the extension.
*   **`compile`**: A script that compiles the code using ESLint and esbuild.
*   **`watch`**: A script that watches for changes in the code and recompiles as needed.
*   **`watch:esbuild`**: A script that watches for changes in the code and rebuilds the extension using esbuild.
*   **`watch:tsc`**: A script that watches for changes in the code and compiles TypeScript files using TSC.
*   **`package`**: A script that packages the extension for distribution.

```json
{
  "scripts": {
    "vscode:prepublish": "npm run package",
    "compile": "npm run check-types && npm run lint && node esbuild.js",
    "watch": "npm-run-all -p watch:*",
    "watch:esbuild": "node esbuild.js --watch",
    "watch:tsc": "tsc --noEmit --watch --project tsconfig.json",
    "package": "npm run check-types && npm run lint && node esbuild.js --production",
    "compile-tests": "tsc -p . --outDir out",
    "watch-tests": "tsc -p . -w --outDir out",
    "pretest": "npm run compile-tests && npm run compile && npm run lint",
    "check-types": "tsc --noEmit",
    "lint": "eslint src",
    "test": "vscode-test"
  }
}
```


## Source Code

```documenttype.other
{
  "name": "docstra",
  "displayName": "docstra",
  "description": "",
  "version": "0.0.1",
  "engines": {
    "vscode": "^1.97.0"
  },
  "categories": [
    "Other"
  ],
  "activationEvents": [],
  "main": "./dist/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "docstra.startChat",
        "title": "Docstra: Start Chat"
      },
      {
        "command": "docstra.askAboutSelection",
        "title": "Docstra: Ask About Selected Code"
      }
    ],
    "menus": {
      "editor/context": [
        {
          "when": "editorHasSelection",
          "command": "docstra.askAboutSelection",
          "group": "docstra"
        }
      ]
    },
    "configuration": {
      "title": "Docstra",
      "properties": {
        "docstra.apiUrl": {
          "type": "string",
          "default": "http://localhost:8000",
          "description": "URL of the Docstra API server"
        },
        "docstra.autoStartServer": {
          "type": "boolean",
          "default": true,
          "description": "Automatically start the Docstra server when VS Code starts"
        }
      }
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run package",
    "compile": "npm run check-types && npm run lint && node esbuild.js",
    "watch": "npm-run-all -p watch:*",
    "watch:esbuild": "node esbuild.js --watch",
    "watch:tsc": "tsc --noEmit --watch --project tsconfig.json",
    "package": "npm run check-types && npm run lint && node esbuild.js --production",
    "compile-tests": "tsc -p . --outDir out",
    "watch-tests": "tsc -p . -w --outDir out",
    "pretest": "npm run compile-tests && npm run compile && npm run lint",
    "check-types": "tsc --noEmit",
    "lint": "eslint src",
    "test": "vscode-test"
  },
  "devDependencies": {
    "@types/mocha": "^10.0.10",
    "@types/node": "20.x",
    "@types/vscode": "^1.97.0",
    "@typescript-eslint/eslint-plugin": "^8.22.0",
    "@typescript-eslint/parser": "^8.22.0",
    "@vscode/test-cli": "^0.0.10",
    "@vscode/test-electron": "^2.4.1",
    "esbuild": "^0.24.2",
    "eslint": "^9.19.0",
    "npm-run-all": "^4.1.5",
    "typescript": "^5.7.3"
  },
  "dependencies": {
    "@types/ws": "^8.18.0",
    "axios": "^1.8.1",
    "ws": "^8.18.1"
  }
}

```
