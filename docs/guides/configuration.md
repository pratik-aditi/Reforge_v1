# Configuration

Reforge is configured through `.reforge/config.json` in your target project. This file is created during installation and can be edited at any time.

## config.json Reference

```json
{
  "$schema": "https://reforge.dev/schema/config.json",
  "version": "1.0.0",
  "project": {
    "name": "",
    "root": "./",
    "description": ""
  },
  "analysis": {
    "exclusions": [
      "**/node_modules/**",
      "**/vendor/**",
      "**/.git/**",
      "**/dist/**",
      "**/build/**",
      "**/target/**",
      "**/*.min.js",
      "**/*.min.css",
      "**/generated/**",
      "**/__pycache__/**",
      "**/.venv/**",
      "**/venv/**"
    ],
    "binaryExtensions": [
      ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
      ".pdf", ".doc", ".docx", ".xls", ".xlsx",
      ".zip", ".tar", ".gz", ".rar",
      ".exe", ".dll", ".so", ".dylib",
      ".class", ".jar", ".war",
      ".woff", ".woff2", ".ttf", ".eot",
      ".mp3", ".mp4", ".wav", ".avi", ".mov"
    ],
    "maxFileSize": 1048576,
    "chunkSize": 5000
  },
  "output": {
    "directory": "reforge_output",
    "formats": {
      "analysis": "xml",
      "userStories": ["md", "json", "csv"],
      "diagrams": ["plantuml", "mermaid"]
    }
  },
  "extraction": {
    "confidenceThreshold": "medium",
    "includeSnippets": true,
    "maxSnippetLines": 10
  }
}
```

## Field Reference

### `project`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | `""` | Project identifier used in output filenames and report headers. Set this to a short, descriptive name (e.g., `my-legacy-app`). |
| `root` | string | `"./"` | Root directory of the codebase to analyze, relative to the config file location. |
| `description` | string | `""` | Brief project description included in generated documentation headers. |

### `analysis`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `exclusions` | string[] | *(see above)* | Glob patterns for files and directories to skip during analysis. |
| `binaryExtensions` | string[] | *(see above)* | File extensions treated as binary and skipped automatically. |
| `maxFileSize` | integer | `1048576` | Maximum file size in bytes (default: 1 MB). Files exceeding this limit are skipped. |
| `chunkSize` | integer | `5000` | Lines per processing chunk for large files. Lower values reduce memory pressure but increase processing time. |

### `output`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `directory` | string | `"reforge_output"` | Base directory for all generated output. Created automatically as `<directory>/<project.name>/`. |
| `formats.analysis` | string | `"xml"` | Output format for analysis inventory. |
| `formats.userStories` | string[] | `["md", "json", "csv"]` | Output formats for user story generation. |
| `formats.diagrams` | string[] | `["plantuml", "mermaid"]` | Diagram notation formats. |

### `extraction`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `confidenceThreshold` | string | `"medium"` | Minimum confidence level to include in extractions. Options: `low`, `medium`, `high`. |
| `includeSnippets` | boolean | `true` | Whether to include source code snippets in extraction XML output. |
| `maxSnippetLines` | integer | `10` | Maximum lines per code snippet when `includeSnippets` is enabled. |

## Example Configurations

### Node.js Application

```json
{
  "project": {
    "name": "express-api",
    "root": "./",
    "description": "Express.js REST API with MongoDB backend"
  },
  "analysis": {
    "exclusions": [
      "**/node_modules/**",
      "**/dist/**",
      "**/coverage/**",
      "**/.git/**",
      "**/*.min.js",
      "**/*.test.js",
      "**/*.spec.js",
      "**/test/**",
      "**/__tests__/**"
    ],
    "maxFileSize": 1048576,
    "chunkSize": 5000
  },
  "output": {
    "directory": "reforge_output"
  },
  "extraction": {
    "confidenceThreshold": "medium",
    "includeSnippets": true,
    "maxSnippetLines": 10
  }
}
```

### Java Monolith

```json
{
  "project": {
    "name": "erp-system",
    "root": "./",
    "description": "Enterprise Java ERP monolith with Spring Framework"
  },
  "analysis": {
    "exclusions": [
      "**/target/**",
      "**/build/**",
      "**/.gradle/**",
      "**/.git/**",
      "**/*.class",
      "**/generated-sources/**",
      "**/test/**",
      "**/node_modules/**"
    ],
    "maxFileSize": 2097152,
    "chunkSize": 3000
  },
  "output": {
    "directory": "reforge_output"
  },
  "extraction": {
    "confidenceThreshold": "low",
    "includeSnippets": true,
    "maxSnippetLines": 15
  }
}
```

!!! tip
    For large Java monoliths, set `confidenceThreshold` to `low` to capture more items, and increase `maxSnippetLines` for longer method signatures.

### Python Project

```json
{
  "project": {
    "name": "django-app",
    "root": "./",
    "description": "Django web application with PostgreSQL"
  },
  "analysis": {
    "exclusions": [
      "**/__pycache__/**",
      "**/.venv/**",
      "**/venv/**",
      "**/migrations/**",
      "**/.git/**",
      "**/static/vendor/**",
      "**/*.pyc",
      "**/htmlcov/**"
    ],
    "maxFileSize": 1048576,
    "chunkSize": 5000
  },
  "output": {
    "directory": "reforge_output"
  },
  "extraction": {
    "confidenceThreshold": "medium",
    "includeSnippets": true,
    "maxSnippetLines": 10
  }
}
```

## Exclusion Pattern Tips

Exclusion patterns use glob syntax. Some common patterns:

| Pattern | Effect |
|---------|--------|
| `**/node_modules/**` | Skip all `node_modules` directories at any depth |
| `**/dist/**` | Skip all `dist` build output directories |
| `**/*.min.js` | Skip minified JavaScript files |
| `**/*.test.ts` | Skip TypeScript test files |
| `**/migrations/**` | Skip database migration files (often auto-generated) |
| `**/vendor/**` | Skip vendored third-party code |
| `src/legacy/archived/**` | Skip a specific archived directory |

!!! note
    Exclusion patterns are applied during `/reforge.analyze`. Changing exclusions after analysis requires re-running the analysis command.

## Output Directory Structure

The output directory is created automatically with this structure:

```
reforge_output/<project.name>/
├── analysis/           # Codebase inventory (analysis.xml)
├── extractions/        # Extracted knowledge (XML per type)
├── derived/            # Cross-referenced artifacts
│   ├── cross-mappings/
│   ├── features-requirements/
│   └── registries/
├── generated/          # Documentation output
│   ├── markdown/
│   ├── user-stories/
│   └── data-dictionary/
├── audit/              # Audit reports and correction plans
└── diagrams/           # UML/SysML diagram sources and renders
```

To use a custom output location, change `output.directory`:

```json
{
  "output": {
    "directory": "/shared/docs/reforge-output"
  }
}
```

!!! warning
    The `reforge_output/` directory is added to `.gitignore` during installation. If you change the output directory, add the new path to `.gitignore` manually.
