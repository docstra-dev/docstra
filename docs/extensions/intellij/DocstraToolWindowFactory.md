---
language: documenttype.java
source_file: /Users/jorgenosberg/development/docstra/extensions/intellij/DocstraToolWindowFactory.java
summary: 'DocstraToolWindowFactory

  =========================='
title: DocstraToolWindowFactory

---

# DocstraToolWindowFactory
==========================

## Overview

The `DocstraToolWindowFactory` class is a tool window factory for the IntelliJ plugin "Docstra". It creates and manages the tool window UI, handles user input, and communicates with the Docstra API to send messages and add context.

## Implementation Details

The `DocstraToolWindowFactory` class implements the `ToolWindowFactory` interface and uses an executor service to handle asynchronous operations. It stores active chat sessions in a map for efficient lookup.

### Attributes

*   `executorService`: An instance of `ExecutorService` used to execute asynchronous tasks.
*   `httpClient`: An instance of `HttpClient` used to send HTTP requests to the Docstra API.
*   `sessions`: A map of active chat sessions, where each session is identified by a unique ID.

### Methods

#### createToolWindowContent(Project project, ToolWindow toolWindow)

Creates the content for the tool window. It creates a new instance of `DocstraToolWindow` and adds it to the tool window's content manager.

```java
public void createToolWindowContent(@NotNull Project project, @NotNull ToolWindow toolWindow) {
    DocstraToolWindow docstraToolWindow = new DocstraToolWindow(project, this);
    Content content = ContentFactory.SERVICE.getInstance().createContent(
            docstraToolWindow.getContent(), "", false);
    toolWindow.getContentManager().addContent(content);
}
```

#### createSession(Project project)

Creates a new chat session with the Docstra API. It sends a POST request to the `/sessions/create` endpoint with the project path as a JSON parameter.

```java
public CompletableFuture<String> createSession(Project project) {
    return CompletableFuture.supplyAsync(() -> {
        try {
            String projectPath = project.getBasePath();
            if (projectPath == null) {
                throw new IOException("Project path is null");
            }

            // API base URL from settings
            String apiUrl = DocstraSettings.getInstance().getApiUrl();

            // Create session request
            String jsonRequest = String.format("{\"working_dir\": \"%s\"}", projectPath);
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(new URI(apiUrl + "/sessions/create"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonRequest))
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() != 200) {
                throw new IOException("Failed to create session: " + response.body());
            }

            // Parse session ID from response
            String responseBody = response.body();
            String sessionId = responseBody
                    .replace("{", "")
                    .replace("}", "")
                    .replace("\"", "")
                    .replace("session_id:", "")
                    .trim();

            // Create a new session object
            DocstraSession session = new DocstraSession(sessionId, projectPath);
            sessions.put(sessionId, session);

            return sessionId;
        } catch (IOException | URISyntaxException | InterruptedException e) {
            throw new RuntimeException("Failed to create session", e);
        }
    }, executorService);
}
```

#### sendMessage(String sessionId, String message)

Sends a message to the Docstra API for the specified chat session. It sends a POST request to the `/sessions/{sessionId}/message` endpoint with the message as a JSON parameter.

```java
public CompletableFuture<String> sendMessage(String sessionId, String message) {
    return CompletableFuture.supplyAsync(() -> {
        try {
            DocstraSession session = sessions.get(sessionId);
            if (session == null) {
                throw new IOException("Session not found: " + sessionId);
            }

            // API base URL from settings
            String apiUrl = DocstraSettings.getInstance().getApiUrl();

            // Send message request
            String jsonRequest = String.format("{\"content\": \"%s\"}", 
                    message.replace("\"", "\\\""));

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(new URI(apiUrl + "/sessions/" + sessionId + "/message"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonRequest))
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() != 200) {
                throw new IOException("Failed to send message: " + response.body());
            }

            // Parse response from JSON
            String responseBody = response.body();
            String content = responseBody
                    .replace("{", "")
                    .replace("}", "")
                    .replace("\"", "")
                    .replace("response:", "")
                    .trim();

            // Add to session history
            session.addMessage("user", message);
            session.addMessage("assistant", content);

            return content;
        } catch (IOException | URISyntaxException | InterruptedException e) {
            throw new RuntimeException("Failed to send message", e);
        }
    }, executorService);
}
```

#### addContext(String sessionId, String filePath, String content, Long timestamp, Long lastModified)

Adds context for the specified chat session. It sends a POST request to the `/sessions/{sessionId}/context` endpoint with the file path and content as JSON parameters.

```java
public CompletableFuture<Void> addContext(String sessionId, String filePath, String content, Long timestamp, Long lastModified) {
    return factory.addContext(sessionId, filePath, content, null, null)
            .thenRun(() -> {
                // Add context to session history
                sessions.get(sessionId).addMessage("system", "[System] Added context from " + filePath);
            })
            .exceptionally(ex -> {
                // Handle exception
                return null;
            });
}
```

## Usage Examples

To use the `DocstraToolWindowFactory`, you need to create a new instance of it and pass it to the `createToolWindowContent` method.

```java
public class Main {
    public static void main(String[] args) {
        DocstraSettings settings = DocstraSettings.getInstance();
        settings.setApiUrl("http://localhost:8000");

        DocstraToolWindowFactory factory = new DocstraToolWindowFactory();

        Project project = // Create a new project instance
        ToolWindow toolWindow = // Create a new tool window instance

        factory.createToolWindowContent(project, toolWindow);
    }
}
```

## Important Dependencies and Relationships

The `DocstraToolWindowFactory` class depends on the following modules:

*   `HttpClient`: Used to send HTTP requests to the Docstra API.
*   `ExecutorService`: Used to execute asynchronous tasks.
*   `DocstraSettings`: Provides the API URL for the Docstra API.

## Notes and Limitations

The `DocstraToolWindowFactory` class has the following limitations:

*   It assumes that the project path is available when creating a new chat session.
*   It does not handle errors properly in some cases. You should add proper error handling to your application.
*   The `addContext` method does not handle exceptions properly. You should add proper exception handling to your application.

## Attributes and Methods

### DocstraToolWindowFactory

#### Attributes

*   `executorService`: An instance of `ExecutorService` used to execute asynchronous tasks.
*   `httpClient`: An instance of `HttpClient` used to send HTTP requests to the Docstra API.
*   `sessions`: A map of active chat sessions, where each session is identified by a unique ID.

#### Methods

*   `createToolWindowContent(Project project, ToolWindow toolWindow)`: Creates the content for the tool window.
*   `createSession(Project project)`: Creates a new chat session with the Docstra API.
*   `sendMessage(String sessionId, String message)`: Sends a message to the Docstra API for the specified chat session.
*   `addContext(String sessionId, String filePath, String content, Long timestamp, Long lastModified)`: Adds context for the specified chat session.

### DocstraSettings

#### Attributes

*   `apiUrl`: The base URL for the Docstra API.

#### Methods

*   `getInstance()`: Returns an instance of `DocstraSettings`.
*   `getApiUrl()`: Returns the base URL for the Docstra API.
*   `setApiUrl(String apiUrl)`: Sets the base URL for the Docstra API.


## Source Code

```documenttype.java
package com.docstra.intellij;

import com.intellij.openapi.project.Project;
import com.intellij.openapi.wm.ToolWindow;
import com.intellij.openapi.wm.ToolWindowFactory;
import com.intellij.ui.content.Content;
import com.intellij.ui.content.ContentFactory;
import org.jetbrains.annotations.NotNull;

import javax.swing.*;
import java.awt.*;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Path;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Main tool window factory for Docstra plugin
 */
public class DocstraToolWindowFactory implements ToolWindowFactory {
    private final ExecutorService executorService = Executors.newCachedThreadPool();
    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();
    
    // Store active chat sessions
    private final Map<String, DocstraSession> sessions = new HashMap<>();

    @Override
    public void createToolWindowContent(@NotNull Project project, @NotNull ToolWindow toolWindow) {
        DocstraToolWindow docstraToolWindow = new DocstraToolWindow(project, this);
        Content content = ContentFactory.SERVICE.getInstance().createContent(
                docstraToolWindow.getContent(), "", false);
        toolWindow.getContentManager().addContent(content);
    }
    
    /**
     * Creates a new chat session with the Docstra API
     */
    public CompletableFuture<String> createSession(Project project) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String projectPath = project.getBasePath();
                if (projectPath == null) {
                    throw new IOException("Project path is null");
                }
                
                // API base URL from settings
                String apiUrl = DocstraSettings.getInstance().getApiUrl();
                
                // Create session request
                String jsonRequest = String.format("{\"working_dir\": \"%s\"}", projectPath);
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(new URI(apiUrl + "/sessions/create"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(jsonRequest))
                        .build();
                
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                
                if (response.statusCode() != 200) {
                    throw new IOException("Failed to create session: " + response.body());
                }
                
                // Parse session ID from response
                // This is a simple JSON parsing without external library
                String responseBody = response.body();
                String sessionId = responseBody
                        .replace("{", "")
                        .replace("}", "")
                        .replace("\"", "")
                        .replace("session_id:", "")
                        .trim();
                
                // Create a new session object
                DocstraSession session = new DocstraSession(sessionId, projectPath);
                sessions.put(sessionId, session);
                
                return sessionId;
            } catch (IOException | URISyntaxException | InterruptedException e) {
                throw new RuntimeException("Failed to create session", e);
            }
        }, executorService);
    }
    
    /**
     * Sends a message to the Docstra API
     */
    public CompletableFuture<String> sendMessage(String sessionId, String message) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                DocstraSession session = sessions.get(sessionId);
                if (session == null) {
                    throw new IOException("Session not found: " + sessionId);
                }
                
                // API base URL from settings
                String apiUrl = DocstraSettings.getInstance().getApiUrl();
                
                // Send message request
                String jsonRequest = String.format("{\"content\": \"%s\"}", 
                        message.replace("\"", "\\\""));
                
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(new URI(apiUrl + "/sessions/" + sessionId + "/message"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(jsonRequest))
                        .build();
                
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                
                if (response.statusCode() != 200) {
                    throw new IOException("Failed to send message: " + response.body());
                }
                
                // Parse response from JSON
                String responseBody = response.body();
                String content = responseBody
                        .replace("{", "")
                        .replace("}", "")
                        .replace("\"", "")
                        .replace("response:", "")
                        .trim();
                
                // Add to session history
                session.addMessage("user", message);
                session.addMessage("assistant", content);
                
                return content;
            } catch (IOException | URISyntaxException | InterruptedException e) {
                throw new RuntimeException("Failed to send message", e);
            }
        }, executorService);
    }
    
    /**
     * Adds code context to the session
     */
    public CompletableFuture<Void> addContext(String sessionId, String filePath, String content, 
                                           Integer startLine, Integer endLine) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                DocstraSession session = sessions.get(sessionId);
                if (session == null) {
                    throw new IOException("Session not found: " + sessionId);
                }
                
                // API base URL from settings
                String apiUrl = DocstraSettings.getInstance().getApiUrl();
                
                // Build selection range JSON if lines provided
                String selectionRangeJson = "";
                if (startLine != null && endLine != null) {
                    selectionRangeJson = String.format(
                            ", \"selection_range\": {\"startLine\": %d, \"endLine\": %d}", 
                            startLine, endLine);
                }
                
                // Clean content for JSON
                String cleanContent = content.replace("\\", "\\\\")
                        .replace("\"", "\\\"")
                        .replace("\n", "\\n")
                        .replace("\r", "\\r")
                        .replace("\t", "\\t");
                
                // Add context request
                String jsonRequest = String.format(
                        "{\"file_path\": \"%s\", \"content\": \"%s\"%s}",
                        filePath.replace("\\", "/"),
                        cleanContent,
                        selectionRangeJson);
                
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(new URI(apiUrl + "/sessions/" + sessionId + "/context"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(jsonRequest))
                        .build();
                
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                
                if (response.statusCode() != 200) {
                    throw new IOException("Failed to add context: " + response.body());
                }
                
                return null;
            } catch (IOException | URISyntaxException | InterruptedException e) {
                throw new RuntimeException("Failed to add context", e);
            }
        }, executorService);
    }
    
    /**
     * Closes a session
     */
    public void closeSession(String sessionId) {
        try {
            DocstraSession session = sessions.get(sessionId);
            if (session == null) {
                return;
            }
            
            // API base URL from settings
            String apiUrl = DocstraSettings.getInstance().getApiUrl();
            
            // Delete session request
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(new URI(apiUrl + "/sessions/" + sessionId))
                    .DELETE()
                    .build();
            
            httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString());
            
            // Remove from local sessions
            sessions.remove(sessionId);
        } catch (Exception e) {
            // Just log and continue
            e.printStackTrace();
        }
    }
    
    /**
     * Gets a session by ID
     */
    public DocstraSession getSession(String sessionId) {
        return sessions.get(sessionId);
    }
}

/**
 * Main tool window UI
 */
class DocstraToolWindow {
    private final JPanel mainPanel;
    private final JTextArea chatHistory;
    private final JTextArea inputField;
    private final JButton sendButton;
    private final JButton addContextButton;
    private final Project project;
    private final DocstraToolWindowFactory factory;
    
    private String currentSessionId;
    
    public DocstraToolWindow(Project project, DocstraToolWindowFactory factory) {
        this.project = project;
        this.factory = factory;
        
        // Create UI components
        mainPanel = new JPanel(new BorderLayout());
        chatHistory = new JTextArea();
        chatHistory.setEditable(false);
        chatHistory.setLineWrap(true);
        chatHistory.setWrapStyleWord(true);
        
        JScrollPane chatScrollPane = new JScrollPane(chatHistory);
        
        inputField = new JTextArea(3, 40);
        inputField.setLineWrap(true);
        inputField.setWrapStyleWord(true);
        
        JScrollPane inputScrollPane = new JScrollPane(inputField);
        
        sendButton = new JButton("Send");
        addContextButton = new JButton("Add Current File");
        
        // Layout components
        JPanel inputPanel = new JPanel(new BorderLayout());
        inputPanel.add(inputScrollPane, BorderLayout.CENTER);
        
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        buttonPanel.add(addContextButton);
        buttonPanel.add(sendButton);
        
        inputPanel.add(buttonPanel, BorderLayout.SOUTH);
        
        mainPanel.add(chatScrollPane, BorderLayout.CENTER);
        mainPanel.add(inputPanel, BorderLayout.SOUTH);
        
        // Set up event handlers
        setupEventHandlers();
        
        // Create a new session
        createNewSession();
    }
    
    private void setupEventHandlers() {
        sendButton.addActionListener(e -> {
            String message = inputField.getText().trim();
            if (!message.isEmpty() && currentSessionId != null) {
                // Add user message to chat
                appendToChatHistory("You: " + message);
                inputField.setText("");
                
                // Send to API
                factory.sendMessage(currentSessionId, message)
                        .thenAccept(response -> {
                            SwingUtilities.invokeLater(() -> {
                                appendToChatHistory("Docstra: " + response);
                            });
                        })
                        .exceptionally(ex -> {
                            SwingUtilities.invokeLater(() -> {
                                appendToChatHistory("[Error] " + ex.getMessage());
                            });
                            return null;
                        });
            }
        });
        
        addContextButton.addActionListener(e -> {
            if (currentSessionId == null) {
                appendToChatHistory("[System] No active session");
                return;
            }
            
            // Get current editor and file
            // TODO: Implement getting the current editor contents
            appendToChatHistory("[System] Adding current file context...");
            
            // This is a placeholder - in a real implementation, you'd get the actual file content
            // from the current editor
            String filePath = "example/file.java";
            String content = "// Example file content";
            
            factory.addContext(currentSessionId, filePath, content, null, null)
                    .thenRun(() -> {
                        SwingUtilities.invokeLater(() -> {
                            appendToChatHistory("[System] Added context from " + filePath);
                        });
                    })
                    .exceptionally(ex -> {
                        SwingUtilities.invokeLater(() -> {
                            appendToChatHistory("[Error] " + ex.getMessage());
                        });
                        return null;
                    });
        });
    }
    
    private void createNewSession() {
        appendToChatHistory("[System] Initializing Docstra...");
        
        factory.createSession(project)
                .thenAccept(sessionId -> {
                    currentSessionId = sessionId;
                    SwingUtilities.invokeLater(() -> {
                        appendToChatHistory("[System] Docstra is ready! Session ID: " + sessionId);
                    });
                })
                .exceptionally(ex -> {
                    SwingUtilities.invokeLater(() -> {
                        appendToChatHistory("[Error] Failed to create session: " + ex.getMessage());
                    });
                    return null;
                });
    }
    
    private void appendToChatHistory(String text) {
        chatHistory.append(text + "\n\n");
        // Scroll to bottom
        chatHistory.setCaretPosition(chatHistory.getDocument().getLength());
    }
    
    public JPanel getContent() {
        return mainPanel;
    }
}

/**
 * Session data class
 */
class DocstraSession {
    private final String sessionId;
    private final String projectPath;
    private final java.util.List<DocstraMessage> messages = new java.util.ArrayList<>();
    
    public DocstraSession(String sessionId, String projectPath) {
        this.sessionId = sessionId;
        this.projectPath = projectPath;
    }
    
    public void addMessage(String role, String content) {
        messages.add(new DocstraMessage(role, content));
    }
    
    public String getSessionId() {
        return sessionId;
    }
    
    public String getProjectPath() {
        return projectPath;
    }
    
    public java.util.List<DocstraMessage> getMessages() {
        return new java.util.ArrayList<>(messages);
    }
}

/**
 * Message data class
 */
class DocstraMessage {
    private final String role;
    private final String content;
    private final long timestamp;
    
    public DocstraMessage(String role, String content) {
        this.role = role;
        this.content = content;
        this.timestamp = System.currentTimeMillis();
    }
    
    public String getRole() {
        return role;
    }
    
    public String getContent() {
        return content;
    }
    
    public long getTimestamp() {
        return timestamp;
    }
}

/**
 * Settings for the plugin
 */
class DocstraSettings {
    private static final DocstraSettings INSTANCE = new DocstraSettings();
    
    private String apiUrl = "http://localhost:8000";
    
    public static DocstraSettings getInstance() {
        return INSTANCE;
    }
    
    public String getApiUrl() {
        return apiUrl;
    }
    
    public void setApiUrl(String apiUrl) {
        this.apiUrl = apiUrl;
    }
}
```
