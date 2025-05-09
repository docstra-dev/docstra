---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/extensions/vscode/vsc-extension-quickstart.md
summary: 'VSC Extension Quickstart

  =========================='
title: vsc-extension-quickstart

---

# VSC Extension Quickstart
==========================

## Overview

This is a quickstart guide for creating a VS Code extension. It covers the necessary files and setup to get you started with developing a web extension.

## Setup

To start, install the recommended extensions:

* amodio.tsl-problem-matcher
* ms-vscode.extension-test-runner
* dbaeumer.vscode-eslint

Additionally, create a new folder for your extension and add the following files:

### package.json

```json
{
  "name": "vsc-extension-quickstart",
  "version": "1.0.0",
  "description": "",
  "main": "src/web/extension.ts",
  "scripts": {
    "test": "tsc && tsc -p tsconfig.json"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "@types/node": "^14.13.0",
    "@types/vscode": "^1.63.2",
    "ts-node": "^10.3.1",
    "typescript": "^4.2.3"
  }
}
```

### src/web/extension.ts

```typescript
// Import required modules and classes
import * as vscode from 'vscode';
import { ExtensionContext } from 'vscode';

// Define the extension's main class
class MyExtension {
  // Constructor for the extension
  constructor(private readonly extensionUri: Uri) {}

  // Method to handle activation of the extension
  activate(context: ExtensionContext) {
    console.log('Extension activated');

    // Create a command to execute when F1 is pressed
    context.subscriptions.push(
      vscode.commands.registerCommand('myextension.helloWorld', () => {
        vscode.window.showInformationMessage('Hello, World!');
      })
    );
  }

  // Method to handle deactivation of the extension
  deactivate() {}
}

// Export the main class
export default MyExtension;
```

### webpack.config.js

```javascript
module.exports = {
  entry: './src/web/extension.ts',
  output: {
    path: __dirname,
    filename: 'extension.js'
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/
      }
    ]
  },
  resolve: {
    extensions: ['.ts', '.js']
  }
};
```

## Usage

To get started with your extension, follow these steps:

1. Open the Command Palette in VS Code by pressing `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac).
2. Type "Open Folder" and select the folder containing your extension's files.
3. Press `F5` to run the extension.

## Testing

To test your extension, follow these steps:

1. Open the Debug View by pressing `Ctrl+Shift+D` (Windows/Linux) or `Cmd+Shift+D` (Mac).
2. Select "Extension Tests" from the launch configuration dropdown.
3. Press `F5` to run the tests in a new window with your extension loaded.

## API Documentation

For more information on the VS Code API, refer to the official documentation:

* [VS Code API](https://code.visualstudio.com/api)
* [Web Extension Guide](https://code.visualstudio.com/api/extension-guides/web-extensions)

## Notes

* Make sure to update the `package.json` file with your extension's metadata.
* Use the `tsconfig.json` file to configure TypeScript settings for your project.
* For more information on Continuous Integration, refer to the official VS Code documentation: [Continuous Integration](https://code.visualstudio.com/api/working-with-extensions/continuous-integration)


## Source Code

```documenttype.markdown
# Welcome to your VS Code Extension

## What's in the folder

* This folder contains all of the files necessary for your web extension.
* `package.json` * this is the manifest file in which you declare your extension and command.
* `src/web/extension.ts` * this is the main file for the browser
* `webpack.config.js` * the webpack config file for the web main

## Setup

* install the recommended extensions (amodio.tsl-problem-matcher, ms-vscode.extension-test-runner, and dbaeumer.vscode-eslint)

## Get up and running the Web Extension

* Run `pnpm install`.
* Place breakpoints in `src/web/extension.ts`.
* Debug via F5 (Run Web Extension).
* Execute extension code via `F1 > Hello world`.

## Make changes

* You can relaunch the extension from the debug toolbar after changing code in `src/web/extension.ts`.
* You can also reload (`Ctrl+R` or `Cmd+R` on Mac) the VS Code window with your extension to load your changes.

## Explore the API

* You can open the full set of our API when you open the file `node_modules/@types/vscode/index.d.ts`.

## Run tests

* Open the debug viewlet (`Ctrl+Shift+D` or `Cmd+Shift+D` on Mac) and from the launch configuration dropdown pick `Extension Tests`.
* Press `F5` to run the tests in a new window with your extension loaded.
* See the output of the test result in the debug console.
* Make changes to `src/web/test/suite/extension.test.ts` or create new test files inside the `test/suite` folder.
  * The provided test runner will only consider files matching the name pattern `**.test.ts`.
  * You can create folders inside the `test` folder to structure your tests any way you want.

## Go further

* [Follow UX guidelines](https://code.visualstudio.com/api/ux-guidelines/overview) to create extensions that seamlessly integrate with VS Code's native interface and patterns.
* Check out the [Web Extension Guide](https://code.visualstudio.com/api/extension-guides/web-extensions).
* [Publish your extension](https://code.visualstudio.com/api/working-with-extensions/publishing-extension) on the VS Code extension marketplace.
* Automate builds by setting up [Continuous Integration](https://code.visualstudio.com/api/working-with-extensions/continuous-integration).

```
