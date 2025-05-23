// src/server/serverManager.ts
import * as vscode from "vscode";
import * as path from "path";
import * as cp from "child_process";
import * as fs from "fs";
import axios from "axios";
import { getWorkspaceFolder } from "../utils/workspaceUtils";
import {
  checkDocstraInstalled,
  installDocstra,
  getDocstraPath,
  getVenvPythonPath,
} from "../utils/installUtils";

export class ServerManager {
  // Configuration
  private readonly DOCSTRA_PORT = 8000;
  private readonly DOCSTRA_CONFIG_FOLDER = ".docstra";
  private statusBar: vscode.StatusBarItem | null = null;
  private serverProcess: cp.ChildProcess | null = null;
  private context: vscode.ExtensionContext;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.statusBar = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Left
    );
    this.statusBar.text = "Docstra: Idle";
    this.statusBar.command = "docstra.startChat";
    this.statusBar.show();
  }

  /**
   * Get the base API URL
   */
  public getApiUrl(): string {
    const config = vscode.workspace.getConfiguration("docstra");
    return config.get("apiUrl") || `http://127.0.0.1:${this.DOCSTRA_PORT}`;
  }

  /**
   * Gets the health endpoint URL
   */
  public getHealthEndpoint(): string {
    return `${this.getApiUrl()}/health`;
  }

  /**
   * Ensures Docstra is running in the current workspace
   */
  public async ensureDocstraRunning(): Promise<boolean> {
    try {
      // Step 1: Check if we're in a valid workspace
      const workspaceFolder = getWorkspaceFolder();
      if (!workspaceFolder) {
        vscode.window.showInformationMessage("Open a folder to use Docstra");
        return false;
      }

      // Step 2: Check if Docstra server is already running for this project
      const isRunning = await this.checkServerRunning(workspaceFolder);
      if (isRunning) {
        console.log("Docstra server is already running for this project");
        return true;
      }

      // Step 3: Check if we have a Docstra config in this workspace
      const hasDocstraConfig = await this.checkDocstraConfigExists(
        workspaceFolder
      );
      if (!hasDocstraConfig) {
        const shouldInit = await this.promptForInit();
        if (shouldInit) {
          await this.initializeDocstra(workspaceFolder);
        } else {
          return false;
        }
      }

      // Step 4: Check if Docstra is installed in the virtual environment
      const isInstalled = await checkDocstraInstalled(this.context);
      if (!isInstalled) {
        const shouldInstall = await this.promptForInstallation();
        if (shouldInstall) {
          await installDocstra(this.context);
        } else {
          return false;
        }
      }

      // Step 5: Start Docstra server
      await this.startDocstraServer(workspaceFolder);
      return true;
    } catch (error: any) {
      vscode.window.showErrorMessage(
        `Failed to start Docstra: ${error.message}`
      );
      return false;
    }
  }

  /**
   * Checks if a Docstra server is running for the specified workspace
   */
  public async checkServerRunning(expectedWorkspace: string): Promise<boolean> {
    try {
      const response = await axios.get(this.getHealthEndpoint(), {
        timeout: 2000,
      });

      // If server is running, check if it's for the right project
      if (response.data && response.data.project_path) {
        const serverProjectPath = response.data.project_path;

        // Normalize paths for comparison (especially important on Windows)
        const normalizedServerPath = path.normalize(serverProjectPath);
        const normalizedExpectedPath = path.normalize(expectedWorkspace);

        if (normalizedServerPath === normalizedExpectedPath) {
          console.log("Found Docstra server for current project");
          this.updateStatusBar("connected");
          return true;
        } else {
          console.log("Found Docstra server but for a different project");
          console.log(`Server path: ${normalizedServerPath}`);
          console.log(`Expected path: ${normalizedExpectedPath}`);

          // Ask user if they want to stop existing server before starting new one
          const shouldStopExisting = await this.promptToStopExistingServer(
            serverProjectPath
          );
          if (shouldStopExisting) {
            await this.stopExistingServer();
          }
          return false;
        }
      }

      return false;
    } catch (error) {
      this.updateStatusBar("disconnected");
      return false;
    }
  }

  /**
   * Checks if the Docstra server is running (without path verification)
   */
  private async checkServerRunningSimple(): Promise<boolean> {
    try {
      await axios.get(this.getHealthEndpoint(), { timeout: 1000 });
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Stops an existing Docstra server
   */
  private async stopExistingServer(): Promise<void> {
    this.updateStatusBar("stopping");

    try {
      // Send shutdown request to the server
      await axios.post(`${this.getApiUrl()}/shutdown`, {}, { timeout: 2000 });

      // Wait for server to shut down
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Check if it's really stopped
      const isStillRunning = await this.checkServerRunningSimple();
      if (isStillRunning) {
        throw new Error("Server did not shut down properly");
      }

      this.updateStatusBar("disconnected");
      vscode.window.showInformationMessage("Existing Docstra server stopped");
    } catch (error: any) {
      this.updateStatusBar("error");
      vscode.window.showErrorMessage(
        `Failed to stop existing server: ${error.message}`
      );
      throw error;
    }
  }

  /**
   * Prompt the user about stopping an existing server
   */
  private async promptToStopExistingServer(
    serverPath: string
  ): Promise<boolean> {
    const response = await vscode.window.showWarningMessage(
      `Another Docstra server is running for ${path.basename(
        serverPath
      )}. Stop it before starting a new one?`,
      "Yes",
      "No"
    );
    return response === "Yes";
  }

  /**
   * Check if a Docstra configuration exists in the specified workspace
   */
  private async checkDocstraConfigExists(
    workspaceFolder: string
  ): Promise<boolean> {
    const configPath = path.join(workspaceFolder, this.DOCSTRA_CONFIG_FOLDER);
    return new Promise<boolean>((resolve) => {
      fs.access(configPath, fs.constants.F_OK, (err) => {
        resolve(!err);
      });
    });
  }

  /**
   * Prompt the user about initializing Docstra
   */
  private async promptForInit(): Promise<boolean> {
    const response = await vscode.window.showInformationMessage(
      "Docstra configuration not found in this project. Initialize it now?",
      "Yes",
      "No"
    );
    return response === "Yes";
  }

  /**
   * Initialize Docstra in the specified workspace
   */
  private async initializeDocstra(workspaceFolder: string): Promise<void> {
    this.updateStatusBar("initializing");

    const docstraPath = getDocstraPath(this.context);
    return new Promise<void>((resolve, reject) => {
      const process = cp.spawn(docstraPath, ["init"], { cwd: workspaceFolder });

      process.on("close", (code) => {
        if (code === 0) {
          vscode.window.showInformationMessage(
            "Docstra initialized successfully"
          );
          resolve();
        } else {
          this.updateStatusBar("error");
          reject(new Error(`Docstra initialization failed with code ${code}`));
        }
      });

      process.on("error", (err) => {
        this.updateStatusBar("error");
        reject(err);
      });
    });
  }

  /**
   * Start the Docstra server
   */
  private async startDocstraServer(workspaceFolder: string): Promise<void> {
    this.updateStatusBar("starting");

    const docstraPath = getDocstraPath(this.context);
    console.log("Starting Docstra server with path:", docstraPath);
    console.log("Workspace folder:", workspaceFolder);

    // Check if the executable exists
    if (!fs.existsSync(docstraPath)) {
      throw new Error(`Docstra executable not found at ${docstraPath}`);
    }

    // Get the virtual environment's Python path
    const venvPythonPath = getVenvPythonPath(this.context);
    console.log("Using Python from virtual environment:", venvPythonPath);

    // Start the server with the virtual environment's Python
    this.serverProcess = cp.spawn(venvPythonPath, ["-m", "docstra", "serve"], {
      cwd: workspaceFolder,
      env: {
        ...process.env,
        PYTHONPATH: path.dirname(venvPythonPath),
      },
    });

    // Collect server output for error reporting
    let serverOutput = "";
    let serverError = "";

    // Log server output
    this.serverProcess.stdout?.on("data", (data) => {
      const output = data.toString();
      console.log("Docstra server stdout:", output);
      serverOutput += output;
    });

    this.serverProcess.stderr?.on("data", (data) => {
      const error = data.toString();
      console.error("Docstra server stderr:", error);
      serverError += error;
    });

    // Handle server process events
    this.serverProcess.on("error", (err) => {
      console.error("Failed to start Docstra server:", err);
      this.updateStatusBar("error");
      vscode.window.showErrorMessage(
        `Failed to start Docstra server: ${err.message}`
      );
    });

    this.serverProcess.on("close", (code) => {
      console.log(`Docstra server exited with code ${code}`);
      this.updateStatusBar("disconnected");
      this.serverProcess = null;
    });

    // Wait for server to start
    await new Promise<void>((resolve, reject) => {
      const timeout = setTimeout(() => {
        if (this.serverProcess) {
          this.serverProcess.kill();
        }
        // Include server output in the error message
        const errorMessage =
          serverError || serverOutput || "No server output available";
        reject(
          new Error(
            `Server failed to start within 10 seconds. Error: ${errorMessage}`
          )
        );
      }, 10000);

      const checkServer = async () => {
        try {
          const response = await axios.get(this.getHealthEndpoint(), {
            timeout: 1000,
            validateStatus: (status) => status === 200, // Only accept 200 as success
          });
          console.log("Server health check response:", response.data);
          clearTimeout(timeout);
          this.updateStatusBar("connected");
          resolve();
        } catch (error) {
          console.log("Server not ready yet, retrying...");
          setTimeout(checkServer, 1000);
        }
      };

      checkServer();
    });
  }

  /**
   * Update the status bar with the current state
   */
  private updateStatusBar(
    state:
      | "idle"
      | "starting"
      | "connected"
      | "disconnected"
      | "error"
      | "stopping"
      | "initializing"
  ): void {
    if (!this.statusBar) {
      return;
    }

    switch (state) {
      case "idle":
        this.statusBar.text = "Docstra: Idle";
        this.statusBar.tooltip = "Click to start chat";
        break;
      case "starting":
        this.statusBar.text = "Docstra: Starting...";
        this.statusBar.tooltip = "Starting Docstra server";
        break;
      case "connected":
        this.statusBar.text = "Docstra: Connected";
        this.statusBar.tooltip = "Click to start chat";
        break;
      case "disconnected":
        this.statusBar.text = "Docstra: Disconnected";
        this.statusBar.tooltip = "Click to start chat";
        break;
      case "error":
        this.statusBar.text = "Docstra: Error";
        this.statusBar.tooltip = "Click to start chat";
        break;
      case "stopping":
        this.statusBar.text = "Docstra: Stopping...";
        this.statusBar.tooltip = "Stopping Docstra server";
        break;
      case "initializing":
        this.statusBar.text = "Docstra: Initializing...";
        this.statusBar.tooltip = "Initializing Docstra configuration";
        break;
    }
  }

  /**
   * Prompt the user about installing Docstra
   */
  private async promptForInstallation(): Promise<boolean> {
    const response = await vscode.window.showInformationMessage(
      "Docstra is not installed. Install it now?",
      "Yes",
      "No"
    );
    return response === "Yes";
  }
}
