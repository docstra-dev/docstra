---
language: documenttype.other
source_file: /Users/jorgenosberg/development/docstra/extensions/intellij/plugin.xml
summary: 'Docstra IntelliJ Plugin

  =========================='
title: plugin

---

# Docstra IntelliJ Plugin
==========================

## Overview
------------

The Docstra IntelliJ plugin is a plugin for the IntelliJ Platform that provides a code assistant for understanding and working with your codebase. It utilizes Large Language Models (LLMs) to provide contextual code understanding, interactive chat interface, and code-aware responses.

## Implementation Details
------------------------

### Plugin Structure

The plugin consists of several key components:

*   `plugin.xml`: The main configuration file that defines the plugin's metadata, dependencies, and functionality.
*   `DocstraToolWindowFactory`: A factory class responsible for creating the Docstra tool window.
*   `AskAboutSelectionAction`: An action class that provides the "Ask Docstra About Selection" feature.

### Compatibility

The plugin is designed to work with IntelliJ Platform versions 203.0 and later.

### Dependencies

The plugin depends on the following modules:

*   `com.intellij.modules.platform`

## Usage Examples
-----------------

### Enabling the Plugin

To enable the plugin, follow these steps:

1.  Open your IntelliJ project.
2.  Go to **Settings** (or **Preferences** on macOS) and navigate to **Plugins**.
3.  Click the **Browse Repositories** button and search for "com.docstra.intellij".
4.  Select the Docstra plugin and click **Install**.

### Using the Plugin

Once installed, you can use the plugin's features as follows:

*   To ask Docstra about a selected code snippet, press `Ctrl + Shift + D` (Windows/Linux) or `Cmd + Shift + D` (macOS).
*   The Docstra tool window will appear, providing contextual information and suggestions.

## Classes
------------

### `com.docstra.intellij.DocstraToolWindowFactory`

#### Attributes:

*   `id`: Unique identifier for the factory class.
*   `secondary`: Indicates whether the tool window is secondary or primary.
*   `icon`: Path to the icon file for the tool window.
*   `anchor`: Anchor point for the tool window.

#### Methods:

*   `createToolWindow`: Creates a new instance of the Docstra tool window.

### `com.docstra.intellij.AskAboutSelectionAction`

#### Attributes:

*   `id`: Unique identifier for the action class.
*   `class`: Class name for the action class.
*   `text`: Text displayed in the action menu.
*   `description`: Description of the action's purpose.

#### Methods:

*   `performAction`: Performs the action when triggered.

## Functions
-------------

### `com.docstra.intellij.DocstraSettingsConfigurable`

#### Parameters:

*   `parentId`: Parent ID for the settings configuration.
*   `instance`: Instance name for the settings configuration.
*   `id`: Unique identifier for the settings configuration.
*   `displayName`: Display name for the settings configuration.

#### Return Value:

*   None

## Important Notes
------------------

*   The plugin uses Large Language Models (LLMs) to provide contextual code understanding and suggestions. However, the accuracy of these suggestions may vary depending on the quality of the LLM model.
*   The plugin is designed to work with IntelliJ Platform versions 203.0 and later.

### Code Blocks

```xml
<idea-plugin>
    <!-- Plugin metadata -->
    <id>com.docstra.intellij</id>
    <name>Docstra</name>
    <version>0.1</version>
    <vendor email="your-email@example.com" url="https://github.com/yourusername/docstra">Your Name</vendor>

    <!-- Plugin description -->
    <description><![CDATA[
        Docstra - LLM-powered code assistant for understanding and working with your codebase.
        
        Features:
        <ul>
            <li>Contextual code understanding with semantic search</li>
            <li>Interactive chat interface within your IDE</li>
            <li>Code-aware responses based on your project context</li>
        </ul>
    ]]></description>

    <!-- Plugin change notes -->
    <change-notes><![CDATA[
        Initial release of the Docstra IntelliJ plugin.
    ]]>
```

```xml
<actions>
    <!-- Ask Docstra action -->
    <action id="Docstra.AskAboutSelection" 
            class="com.docstra.intellij.AskAboutSelectionAction" 
            text="Ask Docstra About Selection" 
            description="Ask Docstra about the selected code">
        <add-to-group group-id="EditorPopupMenu" anchor="last"/>
        <keyboard-shortcut keymap="$default" first-keystroke="ctrl shift D"/>
    </action>
</actions>
```

### Dependencies

The plugin depends on the following modules:

*   `com.intellij.modules.platform`

### Compatibility

The plugin is designed to work with IntelliJ Platform versions 203.0 and later.

### Usage Examples

To enable the plugin, follow these steps:

1.  Open your IntelliJ project.
2.  Go to **Settings** (or **Preferences** on macOS) and navigate to **Plugins**.
3.  Click the **Browse Repositories** button and search for "com.docstra.intellij".
4.  Select the Docstra plugin and click **Install**.

Once installed, you can use the plugin's features as follows:

*   To ask Docstra about a selected code snippet, press `Ctrl + Shift + D` (Windows/Linux) or `Cmd + Shift + D` (macOS).
*   The Docstra tool window will appear, providing contextual information and suggestions.


## Source Code

```documenttype.other
<idea-plugin>
  <id>com.docstra.intellij</id>
  <name>Docstra</name>
  <version>0.1</version>
  <vendor email="your-email@example.com" url="https://github.com/yourusername/docstra">Your Name</vendor>

  <description><![CDATA[
      Docstra - LLM-powered code assistant for understanding and working with your codebase.
      
      Features:
      <ul>
        <li>Contextual code understanding with semantic search</li>
        <li>Interactive chat interface within your IDE</li>
        <li>Code-aware responses based on your project context</li>
      </ul>
    ]]></description>

  <change-notes><![CDATA[
      Initial release of the Docstra IntelliJ plugin.
    ]]>
  </change-notes>

  <!-- Compatibility with IntelliJ Platform -->
  <idea-version since-build="203.0"/>

  <!-- Dependencies -->
  <depends>com.intellij.modules.platform</depends>

  <extensions defaultExtensionNs="com.intellij">
    <!-- Tool Window -->
    <toolWindow id="Docstra" 
                secondary="true" 
                icon="/icons/docstra.svg" 
                anchor="right" 
                factoryClass="com.docstra.intellij.DocstraToolWindowFactory"/>
                
    <!-- Settings -->
    <applicationConfigurable 
        parentId="tools" 
        instance="com.docstra.intellij.DocstraSettingsConfigurable" 
        id="com.docstra.intellij.DocstraSettingsConfigurable" 
        displayName="Docstra"/>
  </extensions>

  <actions>
    <!-- Ask Docstra action -->
    <action id="Docstra.AskAboutSelection" 
            class="com.docstra.intellij.AskAboutSelectionAction" 
            text="Ask Docstra About Selection" 
            description="Ask Docstra about the selected code">
      <add-to-group group-id="EditorPopupMenu" anchor="last"/>
      <keyboard-shortcut keymap="$default" first-keystroke="ctrl shift D"/>
    </action>
  </actions>
</idea-plugin>
```
