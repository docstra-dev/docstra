---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/extensions/vscode/README.md
summary: 'docstra README

  ====================='
title: README

---

# docstra README
=====================

## Overview

This is the README for the "docstra" extension, providing a brief description of its purpose and features.

## Features
------------

The docstra extension offers several key features that enhance the user experience in Visual Studio Code. Below are some screenshots showcasing these features:

\[Feature 1]\(images/feature-1.png\)

\[Feature 2]\(images/feature-2.png\)

> Tip: Many popular extensions utilize animations to demonstrate their capabilities. We recommend using short, focused animations that are easy to follow.

## Requirements
--------------

To use the docstra extension, you will need to install and configure the following dependencies:

*   **Node.js**: Ensure you have Node.js installed on your system.
*   **npm**: Install npm (the package manager for Node.js) if it's not already available.

You can install these dependencies using npm by running the following command in your terminal:

```bash
npm install
```

## Extension Settings
---------------------

The docstra extension contributes the following settings through the `contributes.configuration` extension point:

*   `myExtension.enable`: Enable/disable this extension.
*   `myExtension.thing`: Set to `blah` to do something.

These settings can be accessed in the VS Code settings panel by navigating to `Extensions > Docstra`.

## Known Issues
--------------

Calling out known issues can help limit users opening duplicate issues against your extension:

*   **Issue #1**: Fixed in version 1.0.1.
*   **Issue #2**: Resolved in version 1.1.0.

## Release Notes
----------------

### 1.0.0

Initial release of the docstra extension.

### 1.0.1

Fixed issue \#1.

### 1.1.0

Added features X, Y, and Z.

---

## Working with Markdown
-------------------------

You can author your README using Visual Studio Code. Here are some useful editor keyboard shortcuts:

*   Split the editor (`Cmd+\` on macOS or `Ctrl+\` on Windows and Linux).
*   Toggle preview (`Shift+Cmd+V` on macOS or `Shift+Ctrl+V` on Windows and Linux).
*   Press `Ctrl+Space` (Windows, Linux, macOS) to see a list of Markdown snippets.

For more information:

*   [Visual Studio Code's Markdown Support](http://code.visualstudio.com/docs/languages/markdown)
*   [Markdown Syntax Reference](https://help.github.com/articles/markdown-basics/)

## Usage Examples
-----------------

To use the docstra extension, follow these steps:

1.  Install the extension by navigating to the Extensions panel in VS Code and searching for "docstra".
2.  Once installed, you can enable or disable the extension using the `myExtension.enable` setting.
3.  To set the `myExtension.thing` setting, navigate to the Settings panel and enter the desired value.

## Important Parameters
----------------------

The following parameters are used in the docstra extension:

*   `enable`: A boolean indicating whether the extension is enabled or disabled.
*   `thing`: The value of the `myExtension.thing` setting.

## Return Values
----------------

The docstra extension returns the following values:

*   `boolean`: The result of the `enable` parameter.
*   `string`: The value of the `thing` parameter.

## Side Effects
--------------

The docstra extension has the following side effects:

*   Enables or disables the extension based on the `enable` parameter.
*   Sets the `myExtension.thing` setting to the specified value.

## Notes
------

Please note that this documentation is subject to change as the extension evolves.


## Source Code

```documenttype.markdown
# docstra README

This is the README for your extension "docstra". After writing up a brief description, we recommend including the following sections.

## Features

Describe specific features of your extension including screenshots of your extension in action. Image paths are relative to this README file.

For example if there is an image subfolder under your extension project workspace:

\!\[feature X\]\(images/feature-x.png\)

> Tip: Many popular extensions utilize animations. This is an excellent way to show off your extension! We recommend short, focused animations that are easy to follow.

## Requirements

If you have any requirements or dependencies, add a section describing those and how to install and configure them.

## Extension Settings

Include if your extension adds any VS Code settings through the `contributes.configuration` extension point.

For example:

This extension contributes the following settings:

* `myExtension.enable`: Enable/disable this extension.
* `myExtension.thing`: Set to `blah` to do something.

## Known Issues

Calling out known issues can help limit users opening duplicate issues against your extension.

## Release Notes

Users appreciate release notes as you update your extension.

### 1.0.0

Initial release of ...

### 1.0.1

Fixed issue #.

### 1.1.0

Added features X, Y, and Z.

---

## Working with Markdown

You can author your README using Visual Studio Code.  Here are some useful editor keyboard shortcuts:

* Split the editor (`Cmd+\` on macOS or `Ctrl+\` on Windows and Linux).
* Toggle preview (`Shift+Cmd+V` on macOS or `Shift+Ctrl+V` on Windows and Linux).
* Press `Ctrl+Space` (Windows, Linux, macOS) to see a list of Markdown snippets.

## For more information

* [Visual Studio Code's Markdown Support](http://code.visualstudio.com/docs/languages/markdown)
* [Markdown Syntax Reference](https://help.github.com/articles/markdown-basics/)

**Enjoy!**

```
