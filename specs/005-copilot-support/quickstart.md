# Quickstart: GitHub Copilot Slash Command Support

**Feature**: 005-copilot-support

## Prerequisites

- Python 3.11+
- Reforge CLI installed (`uv tool install reforge-cli` or development mode)
- VS Code with GitHub Copilot extension

## Development Setup

```bash
# Clone and enter the repo
cd /path/to/reforge

# Switch to feature branch
git checkout 005-copilot-support

# Install in development mode
uv pip install -e ".[dev]"

# Run existing tests to verify baseline
pytest tests/
```

## Testing the Feature

### Install for Copilot

```bash
# Create a temporary test project
mkdir /tmp/test-project && cd /tmp/test-project
git init

# Install Reforge for Copilot
reforge --copilot .

# Verify generated files
ls .github/agents/        # Should show reforge.*.agent.md files
ls .github/prompts/       # Should show reforge.*.prompt.md files
cat .vscode/settings.json # Should show Copilot settings
ls .reforge/commands/     # Should show command templates
```

### Update Copilot Installation

```bash
reforge --copilot --update .
```

### Remove Installation

```bash
reforge --remove .
```

### Dry Run

```bash
reforge --copilot --dry-run .
```

### Coexistence with Claude

```bash
# Install both modes on the same project
reforge --claude .
reforge --copilot .

# Both should work
ls .claude/commands/reforge.*.md
ls .github/agents/reforge.*.agent.md
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run only Copilot-related tests
pytest tests/test_scripts.py -k "copilot"

# Run with verbose output
pytest tests/test_scripts.py -k "copilot" -v
```

## Key Files to Modify

| File | Changes |
|------|---------|
| `src/reforge_cli/__init__.py` | Add `--copilot` flag, generation functions, update install/update/remove |
| `tests/test_scripts.py` | Add Copilot test classes mirroring Claude test patterns |
