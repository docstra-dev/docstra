---
language: documenttype.typescript
source_file: /Users/jorgenosberg/development/docstra/extensions/vscode/src/utils/workspaceUtils.ts
summary: 'WorkspaceUtils

  ================'
title: workspaceUtils

---

# WorkspaceUtils
================

## Overview

The `WorkspaceUtils` module provides a utility function to retrieve the current workspace folder path in a Visual Studio Code (VSCode) extension.

## Implementation Details

The `WorkspaceUtils` module uses the VSCode API to access the workspace folder. If no workspace is open, it falls back to the current working directory.

### getWorkspaceFolder Function

```typescript
/**
 * Get the current workspace folder path.
 *
 * Falls back to the current working directory if no workspace is open.
 *
 * @returns {string | undefined} The current workspace folder path or undefined if no workspace is open.
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
```

## Usage Examples

To use the `getWorkspaceFolder` function, simply import it in your VSCode extension and call it as needed.

```typescript
import { getWorkspaceFolder } from 'src/utils/workspaceUtils';

const workspaceFolder = await getWorkspaceFolder();
console.log(workspaceFolder);
```

## Important Dependencies and Relationships

The `WorkspaceUtils` module depends on the following modules:

* `vscode`: The VSCode API module.
* `process`: The Node.js process module.

## Notes

* This function only works in a VSCode extension context. If you try to use it outside of an extension, it will fall back to the current working directory.
* If no workspace is open, this function returns undefined.

## Parameters and Return Values

| Parameter | Type | Description |
| --- | --- | --- |
| `undefined` | `string | undefined` | The current workspace folder path or undefined if no workspace is open. |

## Side Effects

None.

## Attributes

None.

## Classes

None.

## Functions

### getWorkspaceFolder

* Parameters: None
* Return Value: `string | undefined`
* Description: Retrieves the current workspace folder path.
* Notes: Falls back to the current working directory if no workspace is open.


## Source Code

```documenttype.typescript
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

```
