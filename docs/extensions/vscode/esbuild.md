---
language: documenttype.javascript
source_file: /Users/jorgenosberg/development/docstra/extensions/vscode/esbuild.js
summary: 'esbuild.js

  ================'
title: esbuild

---

# esbuild.js
================

Overview
--------

This module uses the Esbuild library to build and bundle a VSCode extension. It provides a simple way to compile TypeScript code into JavaScript, minify it for production, and generate source maps.

Implementation Details
--------------------

The code utilizes the `esbuild` library to perform the following tasks:

*   Compile TypeScript code from `src/extension.ts` into JavaScript.
*   Bundle the compiled code into a single file (`dist/extension.js`).
*   Minify the bundled code for production builds.
*   Generate source maps for debugging purposes.

The build process is controlled by the `main()` function, which takes care of setting up the Esbuild context and executing the build.

### Main Function

```javascript
/**
 * The main entry point of the script.
 *
 * @async
 */
async function main() {
  // Set up the Esbuild context
  const ctx = await esbuild.context({
    // Entry points for the build
    entryPoints: ["src/extension.ts"],
    // Bundle the compiled code into a single file
    bundle: true,
    // Format of the output (in this case, CommonJS)
    format: "cjs",
    // Minify the bundled code for production builds
    minify: production,
    // Generate source maps for debugging purposes
    sourcemap: !production,
    // Disable loading of external modules
    sourcesContent: false,
    // Platform to build for (in this case, Node.js)
    platform: "node",
    // Output file path
    outfile: "dist/extension.js",
    // External modules to exclude from the build
    external: ["vscode"],
    // Log level for the build process
    logLevel: "silent",
    // Plugins to use during the build process
    plugins: [
      esbuildProblemMatcherPlugin,
    ],
  });

  // Watch for changes and rebuild if necessary
  if (watch) {
    await ctx.watch();
  } else {
    await ctx.rebuild();
    await ctx.dispose();
  }
}
```

### Esbuild Problem Matcher Plugin

```javascript
/**
 * A plugin that logs errors during the build process.
 *
 * @type {import('esbuild').Plugin}
 */
const esbuildProblemMatcherPlugin = {
  /**
   * The name of the plugin.
   */
  name: "esbuild-problem-matcher",

  /**
   * Setup function for the plugin.
   *
   * @param {import('esbuild').Build} build
   */
  setup(build) {
    // Log a message when the build starts
    build.onStart(() => {
      console.log("[watch] build started");
    });

    // Log errors during the build process
    build.onEnd((result) => {
      result.errors.forEach(({ text, location }) => {
        console.error(`✘ [ERROR] ${text}`);
        console.error(
          `    ${location.file}:${location.line}:${location.column}:`
        );
      });
      console.log("[watch] build finished");
    });
  },
};
```

### Usage Examples

To use this script, simply run it from the command line and pass in any desired flags:

```bash
node esbuild.js --production --watch
```

This will compile the TypeScript code, bundle it into a single file, minify it for production, and generate source maps. If the `--watch` flag is passed, the script will watch for changes to the source code and rebuild as necessary.

### Important Parameters

*   `entryPoints`: An array of entry points for the build (in this case, `src/extension.ts`).
*   `bundle`: A boolean indicating whether to bundle the compiled code into a single file.
*   `format`: The format of the output (in this case, CommonJS).
*   `minify`: A boolean indicating whether to minify the bundled code for production builds.
*   `sourcemap`: A boolean indicating whether to generate source maps for debugging purposes.

### Return Values

The `main()` function returns a promise that resolves when the build process is complete. If an error occurs during the build, it will be logged to the console and the script will exit with a non-zero status code.

### Side Effects

The `main()` function has the following side effects:

*   Compiles the TypeScript code into JavaScript.
*   Bundles the compiled code into a single file.
*   Minifies the bundled code for production builds.
*   Generates source maps for debugging purposes.
*   Logs errors during the build process.

### Notes

*   This script assumes that you have already installed the necessary dependencies, including Esbuild and VSCode.
*   You will need to modify the `entryPoints` array to include your own TypeScript files.
*   The `--watch` flag is optional and can be used to watch for changes to the source code and rebuild as necessary.


## Source Code

```documenttype.javascript
const esbuild = require("esbuild");

const production = process.argv.includes("--production");
const watch = process.argv.includes("--watch");

/**
 * @type {import('esbuild').Plugin}
 */
const esbuildProblemMatcherPlugin = {
  name: "esbuild-problem-matcher",

  setup(build) {
    build.onStart(() => {
      console.log("[watch] build started");
    });
    build.onEnd((result) => {
      result.errors.forEach(({ text, location }) => {
        console.error(`✘ [ERROR] ${text}`);
        console.error(
          `    ${location.file}:${location.line}:${location.column}:`
        );
      });
      console.log("[watch] build finished");
    });
  },
};

async function main() {
  const ctx = await esbuild.context({
    entryPoints: ["src/extension.ts"],
    bundle: true,
    format: "cjs",
    minify: production,
    sourcemap: !production,
    sourcesContent: false,
    platform: "node",
    outfile: "dist/extension.js",
    external: ["vscode"],
    logLevel: "silent",
    plugins: [
      /* add to the end of plugins array */
      esbuildProblemMatcherPlugin,
    ],
  });
  if (watch) {
    await ctx.watch();
  } else {
    await ctx.rebuild();
    await ctx.dispose();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

```
