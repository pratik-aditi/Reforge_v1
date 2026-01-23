# /reforge.analyze

> Scan and inventory a legacy codebase for analysis and documentation

## Command Syntax

```
/reforge.analyze [path] [--resume] [--force]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `path` | No | Target directory to analyze (defaults to current working directory) |
| `--resume` | No | Resume from last checkpoint if available |
| `--force` | No | Force full re-analysis, ignoring checkpoints |

## Overview

This command performs the initial inventory and analysis of a legacy codebase. It:

1. Scans all files in the target directory
2. Detects programming languages and frameworks
3. Identifies module boundaries
4. Creates a structured XML inventory
5. Saves progress checkpoints for resume capability

## Prerequisites

Before running this command, ensure:

1. The `.reforge/` directory structure exists
2. Configuration is set in `.reforge/config.json`
3. Output directory is writable (created automatically by `init-project.sh`)

---

## Workflow

### Step 0: Initialize Project

Run the initialization script to resolve paths and set up directories:

```bash
bash .reforge/scripts/bash/init-project.sh --json [--name <name>] [target-path]
```

This returns JSON with resolved variables:
```json
{"PROJECT_NAME":"...","OUTPUT_DIR":"...","PROJECT_OUTPUT_DIR":"...","CONFIG":"...","REPO_ROOT":"..."}
```

Use these variables (`$PROJECT_NAME`, `$PROJECT_OUTPUT_DIR`, `$CONFIG`, `$REPO_ROOT`) throughout subsequent steps.

The script handles:
- Deriving project name from config or directory basename
- Setting `project.name` in config.json if empty
- Creating output directory structure (`$PROJECT_OUTPUT_DIR/generated/diagrams/`)
- Creating memory subdirectories (`history/`, `backups/`, `checkpoints/`, `clarifications/`, `logs/`)

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs language/framework detection and pattern recognition
- **Domain Knowledge**: Provides business context for naming and categorization
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 1: Load Configuration

Read `$CONFIG` to obtain analysis-specific settings:

```
- Exclusion patterns (files/directories to skip)
- Binary file extensions (inventory only, no content analysis)
- Maximum file size for analysis
- Chunk size for large files
```

**Analysis Configuration Reference:**

```json
{
  "analysis": {
    "exclusions": ["**/node_modules/**", "**/vendor/**", ...],
    "binaryExtensions": [".png", ".jpg", ...],
    "maxFileSize": 1048576,
    "chunkSize": 5000
  }
}
```

### Step 2: Check for Existing Checkpoint

Look for checkpoint file: `.reforge/memory/checkpoints/analysis-checkpoint.xml`

**If checkpoint exists and `--resume` is specified (or no flag given):**
- Read checkpoint to determine progress state
- Report: "Found checkpoint from [timestamp]. [X] files completed, [Y] remaining."
- Ask user: "Resume from checkpoint? (Y/n)"
- If yes, skip to Step 4 with checkpoint state
- If no, proceed with fresh analysis

**If `--force` is specified:**
- Ignore checkpoint and start fresh

**If no checkpoint exists:**
- Proceed with fresh analysis

### Step 3: Initialize Analysis State

Output directories were created by Step 0 (`init-project.sh`).

Initialize analysis state:

```
- total_files: 0
- processed_files: 0
- skipped_files: 0
- current_file: null
- start_time: now()
- languages: {}
- file_types: {}
```

### Step 4: Discover Files

Use Glob tool to find all files in target directory:

```
Pattern: **/*
Exclude: patterns from config.analysis.exclusions
```

**Apply exclusion patterns:**

For each exclusion pattern in `config.analysis.exclusions`:
- Match files against glob pattern
- Mark matched files as `skipped` with reason "exclusion pattern"

**Categorize files:**

For each discovered file:
1. Check if extension is in `config.analysis.binaryExtensions`
   - If yes: Mark as `file-type: binary`, analysis-status: `inventory-only`
2. Check file size against `config.analysis.maxFileSize`
   - If exceeded: Mark for chunked processing
3. Detect language by extension (see Language Detection section)
4. Add to file inventory

**Report discovery:**
```
Discovered [X] files in [path]
- [Y] source files
- [Z] configuration files
- [W] binary files (inventory only)
- [V] files excluded by pattern
```

### Step 5: Analyze Files

Process each file in the inventory:

**For each file (not skipped, not binary):**

1. **Read file content** using Read tool

2. **Detect file type:**
   - `source`: Code files (.java, .js, .py, .cs, etc.)
   - `config`: Configuration files (.json, .xml, .yaml, .properties)
   - `template`: UI templates (.html, .jsp, .aspx, .vue, .jsx)
   - `data`: Data files (.sql, .csv)
   - `unknown`: Unrecognized

3. **Identify components:**
   - Classes, interfaces, enums
   - Functions, methods
   - Import statements
   - Export statements

4. **Detect frameworks** (see Framework Detection section)

5. **Identify module boundaries:**
   - Package/namespace declarations
   - Directory structure patterns
   - Dependency relationships

6. **Update progress:**
   - Increment `processed_files`
   - Calculate percentage: `(processed_files / total_files) * 100`
   - Report progress every 10 files or 5%: "[X]% complete ([Y]/[Z] files)"

7. **Create checkpoint** every 50 files or 10%:
   - Save state to `.reforge/memory/checkpoints/analysis-checkpoint.xml`

**For binary files:**
- Record: path, size, extension, type="binary"
- Do not read content

**For large files (exceeds maxFileSize):**
- Process in chunks of `config.analysis.chunkSize` lines
- Record chunk boundaries in file entry
- Track progress within file

### Step 6: Generate Output

Write analysis results to `$PROJECT_OUTPUT_DIR/analysis.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<analysis xmlns="http://reforge.dev/schema/analysis"
          version="1.0.0"
          generated="[ISO-8601 timestamp]">

  <project id="[project-name]" name="[Project Name]"
           root-path="[analyzed-path]" status="completed">
    <configuration>
      <exclusion-pattern>[pattern1]</exclusion-pattern>
      <exclusion-pattern>[pattern2]</exclusion-pattern>
      <language-hints>[hint1]</language-hints>
    </configuration>
  </project>

  <files count="[total-analyzed]">
    <file path="[relative-path]"
          language="[detected-language]"
          file-type="[source|config|template|data|binary|unknown]"
          size-bytes="[size]"
          line-count="[lines]"
          hash="[content-hash]"
          analysis-status="[completed|skipped|error]"
          analyzed-at="[timestamp]">
      <components>
        <component type="class" name="ClassName" line-start="10" line-end="150"/>
        <component type="method" name="methodName" line-start="25" line-end="40"/>
      </components>
      <imports>
        <import>package.or.module.name</import>
      </imports>
      <exports>
        <export>ExportedSymbol</export>
      </exports>
    </file>
    <!-- More files... -->
  </files>

  <summary total-files="[count]" total-lines="[count]"
           analyzed="[count]" skipped="[count]">
    <languages>
      <language name="java" count="[files]" lines="[total-lines]"/>
      <language name="javascript" count="[files]" lines="[total-lines]"/>
    </languages>
    <file-types>
      <type name="source" count="[files]"/>
      <type name="config" count="[files]"/>
      <type name="template" count="[files]"/>
    </file-types>
  </summary>

</analysis>
```

### Step 7: Finalize

1. **Remove checkpoint** (analysis complete):
   - Delete `.reforge/memory/checkpoints/analysis-checkpoint.xml`

2. **Write completion log** to `.reforge/memory/logs/`:
   ```
   analysis-[timestamp].log
   - Start time, end time, duration
   - Files processed, skipped, errors
   - Languages detected
   - Frameworks detected
   ```

3. **Report completion:**
   ```
   Analysis complete!

   Output: $PROJECT_OUTPUT_DIR/analysis.xml

   Summary:
   - Total files: [X]
   - Analyzed: [Y]
   - Skipped: [Z]
   - Languages: Java (45%), JavaScript (30%), SQL (15%), Other (10%)
   - Frameworks: Spring Boot, React, Hibernate

   Duration: [HH:MM:SS]

   Next steps:
   - Run /reforge.extract business-rules to extract business logic
   - Run /reforge.extract database to extract data model
   - Run /reforge.status to view detailed progress
   ```

### Step 8: Update Agent Context

Run the agent context update script to record discovered technologies:

```bash
bash .reforge/scripts/bash/update-agent-context.sh claude --json
```

This parses `$PROJECT_OUTPUT_DIR/analysis.xml` and updates CLAUDE.md with:
- Detected languages and their file counts
- Detected frameworks
- Total files and lines analyzed

For other agents, replace `claude` with: `gemini`, `copilot`, `cursor`, or `windsurf`.

---

## Language Detection

Detect programming language by file extension:

| Extension | Language |
|-----------|----------|
| `.java` | Java |
| `.js`, `.mjs` | JavaScript |
| `.ts`, `.tsx` | TypeScript |
| `.py` | Python |
| `.cs` | C# |
| `.cpp`, `.cc`, `.cxx`, `.c`, `.h` | C/C++ |
| `.rb` | Ruby |
| `.php` | PHP |
| `.go` | Go |
| `.rs` | Rust |
| `.swift` | Swift |
| `.kt`, `.kts` | Kotlin |
| `.scala` | Scala |
| `.groovy` | Groovy |
| `.pl`, `.pm` | Perl |
| `.sh`, `.bash` | Shell |
| `.ps1` | PowerShell |
| `.sql` | SQL |
| `.html`, `.htm` | HTML |
| `.css`, `.scss`, `.sass`, `.less` | CSS |
| `.xml` | XML |
| `.json` | JSON |
| `.yaml`, `.yml` | YAML |
| `.properties` | Properties |
| `.md`, `.markdown` | Markdown |
| `.jsp` | JSP |
| `.aspx`, `.ascx` | ASP.NET |
| `.vue` | Vue |
| `.jsx` | React JSX |
| `.svelte` | Svelte |

For ambiguous files, examine content for language indicators.

---

## Framework Detection

Detect frameworks by examining:

### Dependency Files

| File | Framework Indicators |
|------|---------------------|
| `pom.xml` | Spring, Spring Boot (spring-boot-starter-*) |
| `build.gradle` | Spring, Gradle plugins |
| `package.json` | React, Vue, Angular, Express, Next.js |
| `requirements.txt` | Django, Flask, FastAPI |
| `Gemfile` | Rails |
| `composer.json` | Laravel, Symfony |
| `.csproj` | ASP.NET, Entity Framework |
| `go.mod` | Go modules, Gin, Echo |
| `Cargo.toml` | Rust crates |

### Import Patterns

| Pattern | Framework |
|---------|-----------|
| `import org.springframework.*` | Spring |
| `import javax.persistence.*` | JPA/Hibernate |
| `import React from 'react'` | React |
| `import { Component } from '@angular/core'` | Angular |
| `import Vue from 'vue'` | Vue.js |
| `from django.*` | Django |
| `from flask import` | Flask |
| `require 'rails'` | Ruby on Rails |

### Configuration Files

| File Pattern | Framework |
|--------------|-----------|
| `application.properties`, `application.yml` | Spring Boot |
| `hibernate.cfg.xml`, `persistence.xml` | Hibernate/JPA |
| `web.xml` | Java EE |
| `angular.json` | Angular |
| `vue.config.js` | Vue CLI |
| `next.config.js` | Next.js |
| `nuxt.config.js` | Nuxt.js |

---

## Checkpoint Format

Checkpoint file: `.reforge/memory/checkpoints/analysis-checkpoint.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<checkpoint type="analysis" version="1.0.0">
  <project id="[project-name]" root-path="[path]"/>
  <progress>
    <total-files>[count]</total-files>
    <processed-files>[count]</processed-files>
    <skipped-files>[count]</skipped-files>
    <current-file>[path]</current-file>
    <current-position>[line-number or chunk]</current-position>
  </progress>
  <timing>
    <started-at>[ISO-8601]</started-at>
    <checkpoint-at>[ISO-8601]</checkpoint-at>
    <elapsed-seconds>[seconds]</elapsed-seconds>
  </timing>
  <processed>
    <file path="[path]" status="completed"/>
    <file path="[path]" status="completed"/>
    <!-- List of processed files -->
  </processed>
  <pending>
    <file path="[path]"/>
    <file path="[path]"/>
    <!-- List of remaining files -->
  </pending>
</checkpoint>
```

---

## Error Handling

### File Read Errors

If a file cannot be read:
- Record in output: `analysis-status="error"` with error message
- Log the error
- Continue to next file

### Large File Handling

For files exceeding `maxFileSize`:
- Process in chunks of `chunkSize` lines
- Include chunk identifiers in component references:
  ```xml
  <component type="class" name="LargeClass"
             line-start="1" line-end="5000" chunk="1"/>
  ```

### Encoding Issues

If file encoding cannot be determined:
- Try UTF-8, then ISO-8859-1, then skip
- Record encoding used or mark as `analysis-status="encoding-error"`

---

## Output Schema Reference

See `.reforge/schemas/analysis.md` for complete schema documentation.

Key elements:
- `<analysis>`: Root element with version and timestamp
- `<project>`: Project metadata and configuration
- `<files>`: Collection of analyzed files
- `<file>`: Individual file with attributes and components
- `<summary>`: Aggregate statistics

---

## Examples

### Basic Analysis

```
User: /reforge.analyze

Agent: Loading configuration from .reforge/config.json...
Project: legacy-ecommerce
Root path: /opt/codebase

Discovering files...
Found 1,247 files
- 892 source files
- 156 configuration files
- 45 template files
- 89 binary files (inventory only)
- 65 files excluded by patterns

Starting analysis...
10% complete (125/1,247 files)
20% complete (250/1,247 files)
...
100% complete (1,247/1,247 files)

Analysis complete!

Output: $PROJECT_OUTPUT_DIR/analysis.xml

Summary:
- Total files: 1,247
- Analyzed: 1,093
- Skipped: 154
- Languages: Java (55%), JavaScript (25%), SQL (10%), HTML (5%), Other (5%)
- Frameworks: Spring Boot, Hibernate, React, PostgreSQL

Duration: 01:23:45

Next steps:
- Run /reforge.extract business-rules to extract business logic
- Run /reforge.extract database to extract data model
- Run /reforge.status to view detailed progress
```

### Resume Analysis

```
User: /reforge.analyze --resume

Agent: Found checkpoint from 2024-01-15T10:30:00Z
- 500 files completed (40%)
- 747 files remaining

Resuming analysis...
50% complete (625/1,247 files)
...
```
