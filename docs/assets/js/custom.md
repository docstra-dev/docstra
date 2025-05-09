---
language: documenttype.javascript
source_file: /Users/jorgenosberg/development/docstra/docs/assets/js/custom.js
summary: 'Custom JavaScript Module

  =========================='
title: custom

---

# Custom JavaScript Module
==========================

## Overview
------------

This module provides custom JavaScript functionality for enhancing the search experience and adding syntax highlighting enhancements to code blocks.

## Implementation Details
------------------------

### Enhanced Search Data Loading

The module listens for the `DOMContentLoaded` event and checks if an extra search data script is available. If present, it loads and processes the enhanced search data by fetching the JSON data from the script's `src` attribute.

```javascript
// Load and process enhanced search data
fetch(extraSearchData.getAttribute('src'))
    .then(response => response.json())
    .then(data => {
        window.docstraExtraSearchData = data;
        console.log('Enhanced search data loaded');
    })
    .catch(err => console.error('Error loading enhanced search data:', err));
```

### Syntax Highlighting Enhancements

The module adds syntax highlighting enhancements to code blocks by checking if the `linenos` class is present. If not, it adds line numbers to the block if its length exceeds 3.

```javascript
// Add syntax highlighting enhancements
document.querySelectorAll('pre code').forEach(block => {
    // Add line numbers if not already present
    if (!block.classList.contains('linenos')) {
        const lineNumbers = block.innerHTML.split('\n').length;
        if (lineNumbers > 3) {
            block.classList.add('line-numbers');
        }
    }
});
```

## Usage Examples
-----------------

### Loading Enhanced Search Data

To load the enhanced search data, simply include this script in your HTML file and ensure that an extra search data script is available.

```html
<script src="/path/to/custom.js"></script>
<script src="extra-search-data.json"></script>
```

### Adding Syntax Highlighting Enhancements

To add syntax highlighting enhancements to code blocks, wrap the code block with a `pre` element and include the `code` element inside it. The module will automatically add line numbers if necessary.

```html
<pre class="line-numbers">
    <code>
        // Code snippet here
    </code>
</pre>
```

## Important Parameters, Return Values, and Side Effects
--------------------------------------------------------

### Parameters

* `extraSearchData`: The extra search data script element.
* `response`: The response object from the fetch API.

### Return Values

* `data`: The processed enhanced search data.
* `err`: The error object if loading fails.

### Side Effects

* Loads and processes enhanced search data on page load.
* Adds syntax highlighting enhancements to code blocks with line numbers if necessary.

## Notes
-------

* This module assumes that the extra search data script is available and can be loaded from its `src` attribute.
* The module uses the fetch API to load the enhanced search data, which may not work in all browsers or environments.
* The syntax highlighting enhancements are added using CSS classes, which may need to be adjusted depending on the specific styling used in your application.


## Source Code

```documenttype.javascript

document.addEventListener('DOMContentLoaded', function() {
    // Enable the enhanced search if available
    const extraSearchData = document.querySelector('script[src$="extra-search-data.json"]');
    if (extraSearchData) {
        // Load and process the enhanced search data
        fetch(extraSearchData.getAttribute('src'))
            .then(response => response.json())
            .then(data => {
                window.docstraExtraSearchData = data;
                console.log('Enhanced search data loaded');
            })
            .catch(err => console.error('Error loading enhanced search data:', err));
    }
    
    // Add syntax highlighting enhancements
    document.querySelectorAll('pre code').forEach(block => {
        // Add line numbers if not already present
        if (!block.classList.contains('linenos')) {
            const lineNumbers = block.innerHTML.split('\n').length;
            if (lineNumbers > 3) {
                block.classList.add('line-numbers');
            }
        }
    });
});

```
