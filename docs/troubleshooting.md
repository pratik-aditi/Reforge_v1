# Troubleshooting

Common issues and solutions when working with Reforge.

## "Command not found" after installation

**Symptoms:** Running `reforge` in the terminal returns "command not found" or "not recognized".

**Cause:** The `uv tool` bin directory is not on your shell's `PATH`.

**Solution:**

1. Find where `uv` installs tools:

    ```bash
    uv tool dir --bin
    ```

2. Add that directory to your shell profile (`~/.zshrc`, `~/.bashrc`, or equivalent):

    ```bash
    export PATH="$HOME/.local/bin:$PATH"
    ```

3. Reload your shell:

    ```bash
    source ~/.zshrc  # or ~/.bashrc
    ```

## `/reforge.*` commands not recognized in Claude Code

**Symptoms:** Typing `/reforge.analyze` (or any `/reforge.*` command) in Claude Code does not show the command in autocomplete or produces no response.

**Cause:** The `.claude/commands/` directory was not created in your target project. This directory contains thin wrapper files that register the slash commands.

**Solution:**

1. Verify the directory exists:

    ```bash
    ls .claude/commands/reforge.*.md
    ```

2. If missing, re-run the installation:

    ```bash
    reforge --claude /path/to/your-project
    ```

3. Restart Claude Code to pick up the new commands.

## `@reforge.*` commands not recognized in Copilot Chat

**Symptoms:** Typing `@reforge.analyze` in GitHub Copilot Chat does not show the agent or produces no response.

**Cause:** The `.github/agents/` and `.github/prompts/` directories were not created, or VS Code needs a restart.

**Solution:**

1. Verify the directories exist:

    ```bash
    ls .github/agents/reforge.*.agent.md
    ls .github/prompts/reforge.*.prompt.md
    ```

2. If missing, re-run the installation:

    ```bash
    reforge --copilot /path/to/your-project
    ```

3. Restart VS Code (Copilot loads agents at startup).

## Analysis hangs on large codebases

**Symptoms:** `/reforge.analyze` appears to stall or runs for an extremely long time without producing output.

**Cause:** The agent is attempting to process a large number of files, including directories that should be excluded (e.g., `node_modules`, `vendor`, `dist`).

**Solution:**

1. Add exclusion patterns to `.reforge/config.json`:

    ```json
    {
      "analysis": {
        "exclusions": [
          "**/node_modules/**",
          "**/vendor/**",
          "**/dist/**",
          "**/build/**",
          "**/.git/**",
          "**/target/**"
        ]
      }
    }
    ```

2. Reduce `chunkSize` for very large files:

    ```json
    {
      "analysis": {
        "chunkSize": 3000
      }
    }
    ```

3. Use `--resume` if the analysis was interrupted -- it picks up from the last checkpoint rather than starting over.

## Extraction produces low-confidence results

**Symptoms:** Most extracted items have `confidence="low"` or `confidence="medium"`. Few high-confidence results.

**Cause:** The agent lacks project context and language-specific guidance. Without this context, it makes conservative confidence assessments.

**Solution:**

Run the setup commands before extracting:

1. **Initialize project context** -- provides domain knowledge, terminology, and focus areas:

    ```
    /reforge.init
    ```

2. **Generate extraction profile** -- produces language-specific and architecture-specific extraction guidance:

    ```
    /reforge.profile
    ```

3. Then re-run your extraction:

    ```
    /reforge.extract business-rules
    ```

The extraction command automatically loads the project context and extraction profile when they exist.

## "No extractions found" when generating

**Symptoms:** Running `/reforge.generate` produces an error saying no extractions were found, or generates empty output.

**Cause:** No `/reforge.extract` commands have been run yet. The generate command reads from extraction XML files that must already exist.

**Solution:**

1. Check what has been extracted:

    ```
    /reforge.status
    ```

2. Run at least one extraction before generating:

    ```
    /reforge.extract business-rules
    /reforge.extract database
    ```

3. Then generate:

    ```
    /reforge.generate markdown
    ```

The generate command requires extraction output files in `reforge_output/<project>/extractions/`.

## Checkpoint/resume not working

**Symptoms:** Running a command with `--resume` starts from the beginning instead of continuing from where it left off.

**Cause:** Checkpoint files are missing or corrupted. Checkpoints are stored in `.reforge/memory/checkpoints/` and are gitignored by default.

**Solution:**

1. Verify the checkpoint directory exists:

    ```bash
    ls .reforge/memory/checkpoints/
    ```

2. If the directory is empty or missing, the previous run did not save a checkpoint. This happens if the command completed successfully (checkpoints are cleaned up) or if it crashed before the first checkpoint.

3. If checkpoint files exist but `--resume` does not work, delete the stale checkpoint and start fresh:

    ```bash
    rm -rf .reforge/memory/checkpoints/*
    ```

4. Re-run the command without `--resume`.

!!! note
    Checkpoints are designed to handle interruptions (Ctrl+C, session timeouts). If the agent crashes mid-operation, the checkpoint may be incomplete.

## XML output validation errors

**Symptoms:** Downstream tools or audit commands report XML validation errors in extraction output files.

**Cause:** The extraction output does not conform to the expected schema. This can happen when:

- The extraction was run with an older framework version
- Manual edits introduced structural issues
- The agent produced non-conforming output

**Solution:**

1. Check which schema version the file was produced with -- look for the `schema-version` attribute on the root element.

2. If the file lacks `schema-version`, it is a legacy file from before the common schema was introduced. Re-run the extraction:

    ```
    /reforge.extract <type> --force
    ```

3. If the file has `schema-version` but still fails validation, run the audit to identify specific issues:

    ```
    /reforge.audit <type>
    ```

4. Use `/reforge.fix` to correct the identified issues automatically.

## HTML reports missing diagrams

**Symptoms:** Generated HTML reports show placeholder text or empty spaces where diagrams should appear.

**Cause:** The `html` generation format uses PlantUML to render inline SVG diagrams. If PlantUML is not available on your system, diagrams cannot be rendered.

**Solution:**

1. Install PlantUML (requires Java):

    ```bash
    # macOS
    brew install plantuml

    # Ubuntu/Debian
    sudo apt-get install plantuml
    ```

2. Verify it works:

    ```bash
    plantuml -version
    ```

3. Re-generate the HTML reports:

    ```
    /reforge.generate html
    ```

!!! tip
    If you cannot install PlantUML, use `markdown` format instead -- it includes diagram source code (PlantUML/Mermaid) that can be rendered separately.

## Audit shows high gap count

**Symptoms:** Running `/reforge.audit` reports a large number of coverage gaps (e.g., 60%+ of files have no extraction references).

**Cause:** This is expected behavior for a first-pass audit. The audit compares your analysis inventory (all discovered files) against extraction output (files that have been processed). If you have only extracted one or two types, many files will naturally show as gaps.

**Solution:**

1. **Run all relevant extraction types** -- gaps decrease as you extract more types:

    ```
    /reforge.extract business-rules
    /reforge.extract database
    /reforge.extract workflows
    /reforge.extract ui
    ```

2. **Use the fix cycle** to address remaining gaps:

    ```
    /reforge.audit
    /reforge.fix
    ```

3. **Review the audit report** -- not all gaps need fixing. Some files (configuration, build scripts, tests) may legitimately have no extractable business logic.

4. The audit/fix cycle is designed to be **iterative**. Run it multiple times to progressively improve coverage.

!!! note
    A coverage gap does not mean the extraction failed. It means the file was analyzed but no extraction type has referenced it yet. Some files simply do not contain business rules, database interactions, or other extractable elements.
