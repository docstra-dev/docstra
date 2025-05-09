---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/extensions/vscode/CHANGELOG.md
summary: 'CHANGELOG

  ================'
title: CHANGELOG

---

# CHANGELOG
================

## Overview

This file serves as the change log for the "docstra" extension, detailing all notable changes and updates to the extension.

## Implementation Details

The docstra extension is a plugin designed to enhance the functionality of the Visual Studio Code (VSCode) editor. It provides a set of features that improve the user experience, including [list specific features or functionalities].

### Dependencies

The docstra extension relies on the following dependencies:

*   VSCode API
*   Markdown parser library (e.g., marked)

## Usage Examples

To use the docstra extension in VSCode, follow these steps:

1.  Install the extension from the VSCode Marketplace.
2.  Configure the extension settings to customize its behavior.

### Configuration Options

The following configuration options are available for the docstra extension:

*   `showTableOfContents`: A boolean flag that determines whether the table of contents is displayed in the editor.
*   `useMarkdownLinks`: A boolean flag that enables or disables markdown links in the editor.

## Classes and Methods

### DocstraExtension Class

The `DocstraExtension` class serves as the main entry point for the extension. It provides methods for configuring and managing the extension's behavior.

#### Attributes

*   `showTableOfContents`: A boolean flag that determines whether the table of contents is displayed in the editor.
*   `useMarkdownLinks`: A boolean flag that enables or disables markdown links in the editor.

#### Methods

*   `init()`: Initializes the extension and sets up its configuration.
*   `toggleShowTableOfContents()`: Toggles the display of the table of contents in the editor.
*   `toggleUseMarkdownLinks()`: Enables or disables markdown links in the editor.

### MarkdownParser Class

The `MarkdownParser` class is responsible for parsing markdown text in the editor. It provides methods for converting markdown to HTML and vice versa.

#### Attributes

*   `markdownText`: The markdown text to be parsed.
*   `htmlOutput`: The HTML output of the parsed markdown text.

#### Methods

*   `parseToHtml()`: Converts the markdown text to HTML.
*   `parseFromHtml()`: Converts the HTML text back to markdown.

## Functions

### configureExtensionSettings()

Configures the extension settings based on user input.

#### Parameters

*   `settings`: An object containing the user's configuration options.

#### Returns

*   A boolean flag indicating whether the configuration was successful.

### getTableOfContents()

Returns the table of contents for the current document.

#### Parameters

*   `documentPath`: The path to the current document.

#### Returns

*   A string representing the table of contents.

## Important Notes

*   The docstra extension is designed to work with VSCode 1.63 and later versions.
*   The extension uses a markdown parser library to convert markdown text to HTML and vice versa.
*   The extension has a limited set of configuration options, which can be customized through the VSCode Marketplace.

## Unreleased

### Initial Release

The initial release of the docstra extension includes the following features:

*   Basic markdown parsing and conversion
*   Table of contents display in the editor
*   Configuration options for showTableOfContents and useMarkdownLinks


## Source Code

```documenttype.markdown
# Change Log

All notable changes to the "docstra" extension will be documented in this file.

Check [Keep a Changelog](http://keepachangelog.com/) for recommendations on how to structure this file.

## [Unreleased]

- Initial release
```
