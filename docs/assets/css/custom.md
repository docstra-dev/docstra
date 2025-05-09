---
language: documenttype.other
source_file: /Users/jorgenosberg/development/docstra/docs/assets/css/custom.css
summary: 'Custom CSS for MkDocs Material Theme

  ====================================='
title: custom

---

# Custom CSS for MkDocs Material Theme
=====================================

## Overview
------------

This file contains custom CSS styles to enhance the MkDocs Material theme. It improves code block styling, adds visual cues for classes and functions, highlights source files, and enhances admonitions.

## Implementation Details
------------------------

The custom CSS is written in a modular fashion, allowing for easy maintenance and modification of individual styles. The code uses various selectors to target specific elements within the MkDocs Material theme, including `pre` blocks, class and function cards, source files, parameter tables, type annotations, and admonitions.

### Code Block Styling

The following CSS rule improves code block styling by adding a subtle border radius:
```css
.md-typeset pre > code {
    border-radius: 4px;
}
```
This enhances the visual appeal of code blocks within MkDocs Material theme.

### Class and Function Cards

The `docstra-class` and `docstra-function` classes are used to style class and function cards, respectively. The following CSS rules apply:
```css
.docstra-class,
.docstra-function {
    padding: 1em;
    margin-bottom: 1.5em;
    border-left: 4px solid var(--md-primary-fg-color);
    background-color: rgba(0, 0, 0, 0.025);
}

.docstra-class h3,
.docstra-function h3 {
    margin-top: 0;
    color: var(--md-primary-fg-color);
}
```
These styles add a visually appealing design to class and function cards.

### Source File Highlight

The following CSS rule highlights source files by adding a subtle border:
```css
.docstra-source {
    margin-top: 2em;
    padding-top: 1em;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
}
```
This helps distinguish source files from other content.

### Parameter Tables

The following CSS rule styles parameter tables by reducing font size and adding a subtle background color:
```css
.docstra-params {
    font-size: 0.9em;
}

.docstra-params th {
    background-color: rgba(0, 0, 0, 0.05);
}
```
These styles make parameter tables easier to read.

### Type Annotations

The following CSS rule styles type annotations by changing text color and font family:
```css
.docstra-type {
    color: var(--md-code-fg-color);
    font-family: var(--md-code-font-family);
    font-size: 0.9em;
}
```
These styles make type annotations more readable.

### Enhance Admonitions

The following CSS rule enhances admonitions by increasing font size:
```css
.md-typeset .admonition {
    font-size: 0.9em;
}
```
This style makes admonitions easier to read.

## Usage Examples
-----------------

To use this custom CSS, simply include the `custom.css` file in your MkDocs project's `assets/css` directory.

### Example Use Case

```markdown
.. class:: docstra-class
    :class: docstra-function

This is a class card with a function.
```
In this example, the `docstra-class` and `docstra-function` classes are used to style a class card with a function. The custom CSS will apply the styles defined in the `custom.css` file.

## Important Dependencies
-------------------------

This code relies on MkDocs Material theme, which is included by default in most MkDocs projects.

## Notes
--------

* This custom CSS only applies to MkDocs Material theme.
* To customize other themes, modify the corresponding CSS files.
* For more information on MkDocs customization, refer to the [MkDocs documentation](https://mkdocs.palletsprojects.com/en/stable/customization/).

By following these guidelines and using this custom CSS, you can enhance the visual appeal of your MkDocs project.


## Source Code

```documenttype.other

/* Custom styles to enhance MkDocs Material theme */

/* Improve code block styling */
.md-typeset pre > code {
    border-radius: 4px;
}

/* Add styling for class and function cards */
.docstra-class,
.docstra-function {
    padding: 1em;
    margin-bottom: 1.5em;
    border-left: 4px solid var(--md-primary-fg-color);
    background-color: rgba(0, 0, 0, 0.025);
}

.docstra-class h3,
.docstra-function h3 {
    margin-top: 0;
    color: var(--md-primary-fg-color);
}

/* Source file highlight */
.docstra-source {
    margin-top: 2em;
    padding-top: 1em;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
}

/* Parameter tables */
.docstra-params {
    font-size: 0.9em;
}

.docstra-params th {
    background-color: rgba(0, 0, 0, 0.05);
}

/* Type annotations */
.docstra-type {
    color: var(--md-code-fg-color);
    font-family: var(--md-code-font-family);
    font-size: 0.9em;
}

/* Enhance admonitions */
.md-typeset .admonition {
    font-size: 0.9em;
}

```
