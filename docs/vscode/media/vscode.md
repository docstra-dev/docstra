---
language: documenttype.other
source_file: /Users/jorgenosberg/development/docstra/extensions/vscode/media/vscode.css
summary: 'vscode.css

  ================'
title: vscode

---

# vscode.css
================

Overview
--------

This CSS file provides a set of styles for the Visual Studio Code (VSCode) editor and its components. It defines various classes and properties to customize the appearance of the editor, including typography, colors, and layout.

Implementation Details
--------------------

The code is written in CSS and uses the `:root` pseudo-class to define variables that can be used throughout the document. These variables include padding, input padding, margin, font sizes, and colors.

The styles are applied using various selectors, such as `body`, `ol`, `ul`, `a`, `code`, `button`, `input`, and `textarea`. The code also uses pseudo-classes like `:focus` to apply styles when an element is focused.

Usage Examples
-------------

To use this CSS file in your VSCode extension, simply include it in the `media/vscode.css` directory of your extension's manifest.json file.

```json
{
  "manifest_version": 2,
  "name": "My Extension",
  "version": "1.0.0",
  "description": "A brief description of my extension.",
  "content_scripts": [
    {
      "matches": ["*://*.vscode.com/*"],
      "js": ["media/vscode.css"]
    }
  ]
}
```

Important Parameters and Return Values
--------------------------------------

### Variables

The code defines several variables using the `:root` pseudo-class, including:

* `--container-padding`: The padding for the container element.
* `--input-padding-vertical`: The vertical padding for input elements.
* `--input-padding-horizontal`: The horizontal padding for input elements.
* `--input-margin-vertical`: The vertical margin for input elements.
* `--input-margin-horizontal`: The horizontal margin for input elements.

### Styles

The code defines various styles using the following selectors:

* `body`: Applies global styles to the body element.
* `ol`, `ul`: Applies padding to ordered and unordered lists.
* `a`: Applies color to links.
* `code`: Applies font size and family to code elements.
* `button`: Applies border, padding, width, text alignment, outline, and colors to buttons.
* `input`, `textarea`: Applies display, width, border, font family, padding, color, and background color to input and textarea elements.

### Pseudo-Classes

The code uses pseudo-classes like `:focus` to apply styles when an element is focused.

Important Dependencies
---------------------

This CSS file depends on the VSCode editor's theme and layout. It also assumes that the extension is being used in a VSCode environment.

Notes
----

* This code does not include any JavaScript functionality.
* The variables defined using the `:root` pseudo-class can be overridden by other styles or themes.
* The styles defined in this file are intended to work with the default VSCode theme and layout.


## Source Code

```documenttype.other
:root {
  --container-padding: 20px;
  --input-padding-vertical: 6px;
  --input-padding-horizontal: 4px;
  --input-margin-vertical: 4px;
  --input-margin-horizontal: 0;
}

body {
  padding: 0 var(--container-padding);
  color: var(--vscode-foreground);
  font-size: var(--vscode-font-size);
  font-weight: var(--vscode-font-weight);
  font-family: var(--vscode-font-family);
  background-color: var(--vscode-editor-background);
}

ol,
ul {
  padding-left: var(--container-padding);
}

body > *,
form > * {
  margin-block-start: var(--input-margin-vertical);
  margin-block-end: var(--input-margin-vertical);
}

*:focus {
  outline-color: var(--vscode-focusBorder) !important;
}

a {
  color: var(--vscode-textLink-foreground);
}

a:hover,
a:active {
  color: var(--vscode-textLink-activeForeground);
}

code {
  font-size: var(--vscode-editor-font-size);
  font-family: var(--vscode-editor-font-family);
}

button {
  border: none;
  padding: var(--input-padding-vertical) var(--input-padding-horizontal);
  width: 100%;
  text-align: center;
  outline: 1px solid transparent;
  outline-offset: 2px !important;
  color: var(--vscode-button-foreground);
  background: var(--vscode-button-background);
}

button:hover {
  cursor: pointer;
  background: var(--vscode-button-hoverBackground);
}

button:focus {
  outline-color: var(--vscode-focusBorder);
}

button.secondary {
  color: var(--vscode-button-secondaryForeground);
  background: var(--vscode-button-secondaryBackground);
}

button.secondary:hover {
  background: var(--vscode-button-secondaryHoverBackground);
}

input:not([type="checkbox"]),
textarea {
  display: block;
  width: 100%;
  border: none;
  font-family: var(--vscode-font-family);
  padding: var(--input-padding-vertical) var(--input-padding-horizontal);
  color: var(--vscode-input-foreground);
  outline-color: var(--vscode-input-border);
  background-color: var(--vscode-input-background);
}

input::placeholder,
textarea::placeholder {
  color: var(--vscode-input-placeholderForeground);
}

```
