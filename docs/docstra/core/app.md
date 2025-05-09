---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/docstra/core/app.md
summary: 'Document Type: documenttype.'
title: app

---

Document Type: documenttype.markdown
Language: documenttype.python
Source File: /Users/jorgenosberg/development/docstra/docs/docstra/core/app.md
Summary: 'App.py

  ================'
Title: app

---

# App.py
================

## Overview

This module defines the main application for generating documentation using the Docstra framework.

## Implementation Details

The application is built on top of FastAPI, a modern Python web framework. It provides endpoints for uploading files and generating documentation in various formats (HTML, PDF, etc.).

### Key Components

*   `app`: The main FastAPI application instance.
*   `templates`: A Jinja2 template engine instance used for rendering HTML templates.
*   `StaticFiles` instances for serving static files from the `/static` and `/docs` directories.

## Usage Examples

To use this module, you'll need to create a new FastAPI application instance and mount the necessary endpoints. Here's an example:

```python
from fastapi import FastAPI
from app import app

# Create a new FastAPI application instance
app = FastAPI()

# Mount the documentation endpoint
app.mount("/docs", StaticFiles(directory="docs"), name="docs")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Functions

### `generate_docs`

*   **Purpose:** Generate documentation for uploaded files.
*   **Parameters:**
    *   `request`: The incoming request object.
    *   `files`: A list of uploaded files (optional).
    *   `output_format`: The desired output format (default: "html").
*   **Return Value:** A dictionary containing the status and documentation URL.

```python
@app.post("/generate-documentation")
async def generate_docs(
    request: Request,
    files: List[UploadFile] = File(...),
    output_format: str = Form("html"),
):
    """Generate documentation for uploaded files."""
    # Create temp directory for uploads
    temp_dir = Path("./temp_uploads")
    temp_dir.mkdir(exist_ok=True)

    # Process each uploaded file
    file_paths = []
    for file in files:
        file_path = temp_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        file_paths.append(str(file_path))

    # Generate documentation
    doc_dir = Path("./docs/generated")
    doc_dir.mkdir(exist_ok=True, parents=True)

    # Run the generation (this could use the function from CLI)
    for path in file_paths:
        subprocess.run(
            [
                "python",
                "-m",
                "docstra",
                "generate",
                path,
                "--output",
                str(doc_dir),
                "--format",
                output_format,
            ]
        )

    # Return documentation URL
    doc_url = request.url_for("docs", path="/generated/index.html")
    return {"status": "success", "documentation_url": doc_url}
```

### `documentation_ui`

*   **Purpose:** Render the documentation UI.
*   **Parameters:** The incoming request object.

```python
@app.get("/documentation", response_class=HTMLResponse)
async def documentation_ui(request: Request):
    """Documentation generation UI."""
    return templates.TemplateResponse("documentation.html", {"request": request})
```

## Important Dependencies

This module depends on the following external libraries:

*   `fastapi`: A modern Python web framework.
*   `jinja2`: A templating engine for rendering HTML templates.
*   `subprocess`: A module for running system commands.

## Notes

*   This code uses a temporary directory (`./temp_uploads`) to store uploaded files. Make sure to clean up this directory after use to avoid cluttering the file system.
*   The `generate_docs` function assumes that the `docstra` command is installed and available in the system's PATH. If not, you'll need to modify the command accordingly.

## API Endpoints

### `/generate-documentation`

*   **Method:** POST
*   **Description:** Generate documentation for uploaded files.
*   **Request Body:**
    *   `files`: A list of uploaded files (optional).
    *   `output_format`: The desired output format (default: "html").
*   **Response:**
    *   `status`: A dictionary containing the status and documentation URL.

### `/documentation`

*   **Method:** GET
*   **Description:** Render the documentation UI.
*   **Request Body:** None
*   **Response:** An HTML response containing the documentation UI.


## Source Code

```python
# File: ./docstra/core/app.py

from pathlib import Path
import subprocess
from typing import List
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/docs", StaticFiles(directory="docs"), name="docs")
templates = Jinja2Templates(directory="templates")


@app.post("/generate-documentation")
async def generate_docs(
    request: Request,
    files: List[UploadFile] = File(...),
    output_format: str = Form("html"),
):
    """Generate documentation for uploaded files."""
    # Create temp directory for uploads
    temp_dir = Path("./temp_uploads")
    temp_dir.mkdir(exist_ok=True)

    # Process each uploaded file
    file_paths = []
    for file in files:
        file_path = temp_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        file_paths.append(str(file_path))

    # Generate documentation
    doc_dir = Path("./docs/generated")
    doc_dir.mkdir(exist_ok=True, parents=True)

    # Run the generation (this could use the function from CLI)
    for path in file_paths:
        subprocess.run(
            [
                "python",
                "-m",
                "docstra",
                "generate",
                path,
                "--output",
                str(doc_dir),
                "--format",
                output_format,
            ]
        )

    # Return documentation URL
    doc_url = request.url_for("docs", path="/generated/index.html")
    return {"status": "success", "documentation_url": doc_url}


@app.get("/documentation", response_class=HTMLResponse)
async def documentation_ui(request: Request):
    """Documentation generation UI."""
    return templates.TemplateResponse("documentation.html", {"request": request})
```

```


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/app.py
summary: 'App.py

  ================'
title: app

---

# App.py
================

## Overview

This module defines the main application for generating documentation using the Docstra framework.

## Implementation Details

The application is built on top of FastAPI, a modern Python web framework. It provides endpoints for uploading files and generating documentation in various formats (HTML, PDF, etc.).

### Key Components

*   `app`: The main FastAPI application instance.
*   `templates`: A Jinja2 template engine instance used for rendering HTML templates.
*   `StaticFiles` instances for serving static files from the `/static` and `/docs` directories.

## Usage Examples

To use this module, you'll need to create a new FastAPI application instance and mount the necessary endpoints. Here's an example:

```python
from fastapi import FastAPI
from app import app

# Create a new FastAPI application instance
app = FastAPI()

# Mount the documentation endpoint
app.mount("/docs", StaticFiles(directory="docs"), name="docs")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Functions

### `generate_docs`

*   **Purpose:** Generate documentation for uploaded files.
*   **Parameters:**
    *   `request`: The incoming request object.
    *   `files`: A list of uploaded files (optional).
    *   `output_format`: The desired output format (default: "html").
*   **Return Value:** A dictionary containing the status and documentation URL.

```python
@app.post("/generate-documentation")
async def generate_docs(
    request: Request,
    files: List[UploadFile] = File(...),
    output_format: str = Form("html"),
):
    """Generate documentation for uploaded files."""
    # Create temp directory for uploads
    temp_dir = Path("./temp_uploads")
    temp_dir.mkdir(exist_ok=True)

    # Process each uploaded file
    file_paths = []
    for file in files:
        file_path = temp_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        file_paths.append(str(file_path))

    # Generate documentation
    doc_dir = Path("./docs/generated")
    doc_dir.mkdir(exist_ok=True, parents=True)

    # Run the generation (this could use the function from CLI)
    for path in file_paths:
        subprocess.run(
            [
                "python",
                "-m",
                "docstra",
                "generate",
                path,
                "--output",
                str(doc_dir),
                "--format",
                output_format,
            ]
        )

    # Return documentation URL
    doc_url = request.url_for("docs", path="/generated/index.html")
    return {"status": "success", "documentation_url": doc_url}
```

### `documentation_ui`

*   **Purpose:** Render the documentation UI.
*   **Parameters:** The incoming request object.

```python
@app.get("/documentation", response_class=HTMLResponse)
async def documentation_ui(request: Request):
    """Documentation generation UI."""
    return templates.TemplateResponse("documentation.html", {"request": request})
```

## Important Dependencies

This module depends on the following external libraries:

*   `fastapi`: A modern Python web framework.
*   `jinja2`: A templating engine for rendering HTML templates.
*   `subprocess`: A module for running system commands.

## Notes

*   This code uses a temporary directory (`./temp_uploads`) to store uploaded files. Make sure to clean up this directory after use to avoid cluttering the file system.
*   The `generate_docs` function assumes that the `docstra` command is installed and available in the system's PATH. If not, you'll need to modify the command accordingly.

## API Endpoints

### `/generate-documentation`

*   **Method:** POST
*   **Description:** Generate documentation for uploaded files.
*   **Request Body:**
    *   `files`: A list of uploaded files (optional).
    *   `output_format`: The desired output format (default: "html").
*   **Response:**
    *   `status`: A dictionary containing the status and documentation URL.

### `/documentation`

*   **Method:** GET
*   **Description:** Render the documentation UI.
*   **Request Body:** None
*   **Response:** An HTML response containing the documentation UI.


## Source Code

```documenttype.python
# File: ./docstra/core/app.py

from pathlib import Path
import subprocess
from typing import List
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/docs", StaticFiles(directory="docs"), name="docs")
templates = Jinja2Templates(directory="templates")


@app.post("/generate-documentation")
async def generate_docs(
    request: Request,
    files: List[UploadFile] = File(...),
    output_format: str = Form("html"),
):
    """Generate documentation for uploaded files."""
    # Create temp directory for uploads
    temp_dir = Path("./temp_uploads")
    temp_dir.mkdir(exist_ok=True)

    # Process each uploaded file
    file_paths = []
    for file in files:
        file_path = temp_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        file_paths.append(str(file_path))

    # Generate documentation
    doc_dir = Path("./docs/generated")
    doc_dir.mkdir(exist_ok=True, parents=True)

    # Run the generation (this could use the function from CLI)
    for path in file_paths:
        subprocess.run(
            [
                "python",
                "-m",
                "docstra",
                "generate",
                path,
                "--output",
                str(doc_dir),
                "--format",
                output_format,
            ]
        )

    # Return documentation URL
    doc_url = request.url_for("docs", path="/generated/index.html")
    return {"status": "success", "documentation_url": doc_url}


@app.get("/documentation", response_class=HTMLResponse)
async def documentation_ui(request: Request):
    """Documentation generation UI."""
    return templates.TemplateResponse("documentation.html", {"request": request})

```

```
