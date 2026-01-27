"""Tests for reforge_cli.scripts - cross-platform Python utilities."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from reforge_cli.scripts import (
    check_prerequisites,
    create_checkpoint,
    delete_checkpoint,
    get_analysis_dir,
    get_audit_dir,
    get_config_value,
    get_derived_dir,
    get_diagrams_dir,
    get_extractions_dir,
    get_generated_dir,
    get_output_dir,
    get_project_name,
    get_project_output_dir,
    get_repo_root,
    init_project,
    migrate_output,
    read_checkpoint,
    resolve_analysis_file,
    resolve_extraction_file,
    update_agent_context,
)
from reforge_cli.scripts.common import ReforgeError


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Create a temporary repository with .reforge structure."""
    reforge_dir = tmp_path / ".reforge"
    reforge_dir.mkdir()

    config = {
        "project": {"name": "test-project", "root": ".", "description": ""},
        "output": {"directory": "reforge_output"},
        "analysis": {"exclusions": []},
        "extraction": {
            "confidenceThreshold": 0.7,
            "includeSnippets": True,
            "maxSnippetLines": 20,
        },
    }
    (reforge_dir / "config.json").write_text(json.dumps(config, indent=2))

    # Create memory directories
    (reforge_dir / "memory" / "checkpoints").mkdir(parents=True)
    (reforge_dir / "memory" / "clarifications").mkdir(parents=True)

    return tmp_path


@pytest.fixture
def temp_repo_with_analysis(temp_repo: Path) -> Path:
    """Create a temp repo with analysis.xml in new directory structure."""
    output_dir = temp_repo / "reforge_output" / "test-project"
    analysis_dir = output_dir / "analysis"
    analysis_dir.mkdir(parents=True)

    analysis_xml = """<?xml version="1.0" encoding="UTF-8"?>
<analysis total-files="42" total-lines="5000">
  <languages>
    <language name="Python" files="30" lines="4000"/>
    <language name="JavaScript" files="12" lines="1000"/>
  </languages>
  <language-hints>FastAPI</language-hints>
  <language-hints>React</language-hints>
</analysis>
"""
    (analysis_dir / "analysis.xml").write_text(analysis_xml)

    return temp_repo


@pytest.fixture
def temp_repo_with_legacy_structure(temp_repo: Path) -> Path:
    """Create a temp repo with legacy flat output structure."""
    output_dir = temp_repo / "reforge_output" / "test-project"
    output_dir.mkdir(parents=True)

    # Legacy flat structure
    (output_dir / "analysis.xml").write_text("<analysis/>")
    (output_dir / "business-rules.xml").write_text("<rules/>")
    (output_dir / "database.xml").write_text("<db/>")

    return temp_repo


class TestCommon:
    """Tests for common.py functions."""

    def test_get_repo_root_finds_reforge(self, temp_repo: Path):
        """get_repo_root finds .reforge directory."""
        subdir = temp_repo / "src" / "deep" / "nested"
        subdir.mkdir(parents=True)

        result = get_repo_root(subdir)
        assert result == temp_repo

    def test_get_repo_root_finds_git(self, tmp_path: Path):
        """get_repo_root finds .git directory as fallback."""
        (tmp_path / ".git").mkdir()
        subdir = tmp_path / "src"
        subdir.mkdir()

        result = get_repo_root(subdir)
        assert result == tmp_path

    def test_get_repo_root_raises_when_not_found(self, tmp_path: Path):
        """get_repo_root raises when no marker found."""
        isolated = tmp_path / "isolated"
        isolated.mkdir()

        with pytest.raises(ReforgeError, match="Could not find repository root"):
            get_repo_root(isolated)

    def test_get_config_value_simple_key(self, temp_repo: Path):
        """get_config_value reads simple keys."""
        config = temp_repo / ".reforge" / "config.json"
        result = get_config_value("project.name", config)
        assert result == "test-project"

    def test_get_config_value_nested_key(self, temp_repo: Path):
        """get_config_value reads nested keys."""
        config = temp_repo / ".reforge" / "config.json"
        result = get_config_value("output.directory", config)
        assert result == "reforge_output"

    def test_get_config_value_missing_key(self, temp_repo: Path):
        """get_config_value returns None for missing keys."""
        config = temp_repo / ".reforge" / "config.json"
        result = get_config_value("nonexistent.key", config)
        assert result is None

    def test_get_config_value_missing_file(self, tmp_path: Path):
        """get_config_value returns None for missing file."""
        result = get_config_value("any.key", tmp_path / "missing.json")
        assert result is None

    def test_get_project_name_from_config(self, temp_repo: Path):
        """get_project_name reads from config."""
        result = get_project_name(temp_repo)
        assert result == "test-project"

    def test_get_project_name_fallback_to_dir(self, tmp_path: Path):
        """get_project_name falls back to directory name."""
        reforge_dir = tmp_path / ".reforge"
        reforge_dir.mkdir()
        (reforge_dir / "config.json").write_text('{"project": {"name": ""}}')

        result = get_project_name(tmp_path)
        assert result == tmp_path.name

    def test_get_output_dir_from_config(self, temp_repo: Path):
        """get_output_dir reads from config."""
        result = get_output_dir(temp_repo)
        assert result == "reforge_output"

    def test_get_output_dir_default(self, tmp_path: Path):
        """get_output_dir defaults to reforge_output."""
        reforge_dir = tmp_path / ".reforge"
        reforge_dir.mkdir()
        (reforge_dir / "config.json").write_text('{"output": {}}')

        result = get_output_dir(tmp_path)
        assert result == "reforge_output"

    def test_get_project_output_dir(self, temp_repo: Path):
        """get_project_output_dir combines paths correctly."""
        result = get_project_output_dir(temp_repo)
        assert result == temp_repo / "reforge_output" / "test-project"


class TestInitProject:
    """Tests for init_project.py functions."""

    def test_init_project_creates_directories(self, temp_repo: Path):
        """init_project creates required directories."""
        os.chdir(temp_repo)

        result = init_project()

        assert result.project_name == "test-project"
        assert result.output_dir == "reforge_output"
        assert result.repo_root == temp_repo

        # Check new directory structure created
        project_dir = temp_repo / "reforge_output" / "test-project"
        assert (project_dir / "analysis").exists()
        assert (project_dir / "extractions").exists()
        assert (project_dir / "derived" / "registries").exists()
        assert (project_dir / "generated").exists()
        assert (project_dir / "audit").exists()
        assert (project_dir / "diagrams" / "sources").exists()
        assert (project_dir / "diagrams" / "rendered").exists()
        assert (temp_repo / ".reforge" / "memory" / "history").exists()
        assert (temp_repo / ".reforge" / "memory" / "backups").exists()

    def test_init_project_with_name_override(self, temp_repo: Path):
        """init_project uses name override."""
        os.chdir(temp_repo)

        result = init_project(project_name_override="custom-name")

        assert result.project_name == "custom-name"
        assert (temp_repo / "reforge_output" / "custom-name").exists()

    def test_init_project_json_output(self, temp_repo: Path):
        """init_project JSON output matches expected format."""
        os.chdir(temp_repo)

        result = init_project()
        json_str = result.to_json()
        data = json.loads(json_str)

        assert "PROJECT_NAME" in data
        assert "OUTPUT_DIR" in data
        assert "PROJECT_OUTPUT_DIR" in data
        assert "CONFIG" in data
        assert "REPO_ROOT" in data

    def test_init_project_raises_without_config(self, tmp_path: Path):
        """init_project raises when config missing."""
        (tmp_path / ".reforge").mkdir()
        os.chdir(tmp_path)

        with pytest.raises(ReforgeError, match="config.json not found"):
            init_project()


class TestCheckPrerequisites:
    """Tests for check_prerequisites.py functions."""

    def test_check_prerequisites_basic(self, temp_repo: Path):
        """check_prerequisites runs without analysis."""
        os.chdir(temp_repo)

        result = check_prerequisites()

        assert result.project_name == "test-project"
        assert result.analysis_status == "not-found"
        assert result.available_extractions == []

    def test_check_prerequisites_with_analysis(self, temp_repo_with_analysis: Path):
        """check_prerequisites detects analysis."""
        os.chdir(temp_repo_with_analysis)

        result = check_prerequisites()

        assert result.analysis_status == "completed"

    def test_check_prerequisites_require_analysis_fails(self, temp_repo: Path):
        """check_prerequisites raises when analysis required but missing."""
        os.chdir(temp_repo)

        with pytest.raises(ReforgeError, match="Analysis not found"):
            check_prerequisites(require_analysis=True)

    def test_check_prerequisites_require_analysis_passes(self, temp_repo_with_analysis: Path):
        """check_prerequisites passes when analysis exists."""
        os.chdir(temp_repo_with_analysis)

        result = check_prerequisites(require_analysis=True)
        assert result.analysis_status == "completed"

    def test_check_prerequisites_detects_extractions(self, temp_repo_with_analysis: Path):
        """check_prerequisites lists available extractions."""
        output_dir = temp_repo_with_analysis / "reforge_output" / "test-project"
        extractions_dir = output_dir / "extractions"
        extractions_dir.mkdir(parents=True)
        (extractions_dir / "business-rules.xml").write_text("<rules/>")
        (extractions_dir / "database.xml").write_text("<db/>")

        os.chdir(temp_repo_with_analysis)
        result = check_prerequisites()

        assert "business-rules" in result.available_extractions
        assert "database" in result.available_extractions

    def test_check_prerequisites_require_audit_fails(self, temp_repo_with_analysis: Path):
        """check_prerequisites raises when audit required but missing."""
        os.chdir(temp_repo_with_analysis)

        with pytest.raises(ReforgeError, match="Correction plan not found"):
            check_prerequisites(require_audit=True)

    def test_check_prerequisites_require_audit_passes(self, temp_repo_with_analysis: Path):
        """check_prerequisites passes when audit exists."""
        output_dir = temp_repo_with_analysis / "reforge_output" / "test-project"
        audit_dir = output_dir / "audit"
        audit_dir.mkdir(parents=True)
        (audit_dir / "correction-plan.xml").write_text("<correction-plan/>")

        os.chdir(temp_repo_with_analysis)
        result = check_prerequisites(require_audit=True)
        assert result.analysis_status == "completed"

    def test_check_prerequisites_json_output(self, temp_repo: Path):
        """check_prerequisites JSON output matches expected format."""
        os.chdir(temp_repo)

        result = check_prerequisites()
        json_str = result.to_json()
        data = json.loads(json_str)

        assert "PROJECT_NAME" in data
        assert "ANALYSIS_STATUS" in data
        assert "AVAILABLE_EXTRACTIONS" in data


class TestManageCheckpoint:
    """Tests for manage_checkpoint.py functions."""

    def test_read_checkpoint_not_found(self, temp_repo: Path):
        """read_checkpoint returns exists=False when missing."""
        os.chdir(temp_repo)

        result = read_checkpoint()

        assert result.exists is False
        assert result.checkpoint_type == "analysis"

    def test_create_and_read_checkpoint(self, temp_repo: Path):
        """create_checkpoint and read_checkpoint work together."""
        os.chdir(temp_repo)

        # Create checkpoint path
        create_result = create_checkpoint()
        assert create_result.checkpoint_file.parent.exists()

        # Write checkpoint content
        checkpoint_xml = """<?xml version="1.0" encoding="UTF-8"?>
<checkpoint>
  <total-files>100</total-files>
  <processed-files>50</processed-files>
  <current-file>src/main.py</current-file>
  <started-at>2024-01-15T10:00:00Z</started-at>
  <elapsed-seconds>120</elapsed-seconds>
</checkpoint>
"""
        create_result.checkpoint_file.write_text(checkpoint_xml)

        # Read it back
        read_result = read_checkpoint()

        assert read_result.exists is True
        assert read_result.total_files == 100
        assert read_result.processed_files == 50
        assert read_result.current_file == "src/main.py"
        assert read_result.percentage == 50

    def test_delete_checkpoint(self, temp_repo: Path):
        """delete_checkpoint removes checkpoint file."""
        os.chdir(temp_repo)

        # Create a checkpoint
        checkpoint_dir = temp_repo / ".reforge" / "memory" / "checkpoints"
        checkpoint_file = checkpoint_dir / "analysis-checkpoint.xml"
        checkpoint_file.write_text("<checkpoint/>")

        # Delete it
        result = delete_checkpoint()

        assert result.deleted is True
        assert not checkpoint_file.exists()

    def test_delete_checkpoint_not_found(self, temp_repo: Path):
        """delete_checkpoint returns deleted=False when missing."""
        os.chdir(temp_repo)

        result = delete_checkpoint()

        assert result.deleted is False

    def test_checkpoint_json_output(self, temp_repo: Path):
        """checkpoint JSON output matches expected format."""
        os.chdir(temp_repo)

        result = read_checkpoint()
        json_str = result.to_json()
        data = json.loads(json_str)

        assert "EXISTS" in data
        assert "TYPE" in data
        assert "TOTAL_FILES" in data
        assert "PERCENTAGE" in data


class TestUpdateAgentContext:
    """Tests for update_agent_context.py functions."""

    def test_update_agent_context_no_context_file(self, temp_repo_with_analysis: Path):
        """update_agent_context handles missing context file."""
        os.chdir(temp_repo_with_analysis)

        result = update_agent_context()

        assert result.updated is False
        assert result.languages == "Python, JavaScript"

    def test_update_agent_context_appends_section(self, temp_repo_with_analysis: Path):
        """update_agent_context appends to existing file."""
        claude_md = temp_repo_with_analysis / "CLAUDE.md"
        claude_md.write_text("# My Project\n\nExisting content.\n")

        os.chdir(temp_repo_with_analysis)
        result = update_agent_context()

        assert result.updated is True
        content = claude_md.read_text()
        assert "## Active Technologies" in content
        assert "Python, JavaScript" in content

    def test_update_agent_context_replaces_section(self, temp_repo_with_analysis: Path):
        """update_agent_context replaces existing section."""
        claude_md = temp_repo_with_analysis / "CLAUDE.md"
        claude_md.write_text("""# My Project

## Active Technologies

Old content here.

## Other Section

Keep this.
""")

        os.chdir(temp_repo_with_analysis)
        result = update_agent_context()

        assert result.updated is True
        content = claude_md.read_text()
        assert "Old content here" not in content
        assert "Python, JavaScript" in content
        assert "## Other Section" in content
        assert "Keep this" in content

    def test_update_agent_context_json_output(self, temp_repo_with_analysis: Path):
        """update_agent_context JSON output matches expected format."""
        os.chdir(temp_repo_with_analysis)

        result = update_agent_context()
        json_str = result.to_json()
        data = json.loads(json_str)

        assert "AGENT_TYPE" in data
        assert "LANGUAGES" in data
        assert "FRAMEWORKS" in data
        assert "TOTAL_FILES" in data


class TestConfigParsing:
    """Tests for correct config.json parsing behavior."""

    def test_get_config_value_reads_nested_json_correctly(self, temp_repo: Path):
        """get_config_value correctly parses nested JSON values.

        This verifies that Python's json module correctly extracts nested values,
        which is especially important for complex config structures.
        """
        config = temp_repo / ".reforge" / "config.json"

        # Verify nested values are read correctly
        assert get_config_value("project.name", config) == "test-project"
        assert get_config_value("output.directory", config) == "reforge_output"
        assert get_config_value("extraction.confidenceThreshold", config) == "0.7"
        assert get_config_value("extraction.includeSnippets", config) == "True"

    def test_get_config_value_handles_deeply_nested_config(self, tmp_path: Path):
        """get_config_value handles deeply nested JSON structures."""
        reforge_dir = tmp_path / ".reforge"
        reforge_dir.mkdir()

        config = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deeply-nested"
                    }
                }
            }
        }
        config_file = reforge_dir / "config.json"
        config_file.write_text(json.dumps(config))

        result = get_config_value("level1.level2.level3.value", config_file)
        assert result == "deeply-nested"

    def test_get_config_value_handles_arrays_in_config(self, temp_repo: Path):
        """get_config_value handles array values by converting to string."""
        config = temp_repo / ".reforge" / "config.json"

        # analysis.exclusions is an array
        result = get_config_value("analysis.exclusions", config)
        assert result == "[]"

    def test_get_config_value_handles_invalid_json(self, tmp_path: Path):
        """get_config_value returns None for invalid JSON."""
        reforge_dir = tmp_path / ".reforge"
        reforge_dir.mkdir()

        config_file = reforge_dir / "config.json"
        config_file.write_text("{ invalid json }")

        result = get_config_value("any.key", config_file)
        assert result is None


class TestSubdirectoryHelpers:
    """Tests for subdirectory helper functions."""

    def test_get_analysis_dir(self, tmp_path: Path):
        """get_analysis_dir returns correct path."""
        result = get_analysis_dir(tmp_path)
        assert result == tmp_path / "analysis"

    def test_get_extractions_dir(self, tmp_path: Path):
        """get_extractions_dir returns correct path."""
        result = get_extractions_dir(tmp_path)
        assert result == tmp_path / "extractions"

    def test_get_derived_dir(self, tmp_path: Path):
        """get_derived_dir returns correct path."""
        result = get_derived_dir(tmp_path)
        assert result == tmp_path / "derived"

    def test_get_generated_dir(self, tmp_path: Path):
        """get_generated_dir returns correct path."""
        result = get_generated_dir(tmp_path)
        assert result == tmp_path / "generated"

    def test_get_diagrams_dir(self, tmp_path: Path):
        """get_diagrams_dir returns correct path."""
        result = get_diagrams_dir(tmp_path)
        assert result == tmp_path / "diagrams"

    def test_get_audit_dir(self, tmp_path: Path):
        """get_audit_dir returns correct path."""
        result = get_audit_dir(tmp_path)
        assert result == tmp_path / "audit"


class TestBackwardCompatibleResolvers:
    """Tests for backward-compatible file resolvers."""

    def test_resolve_analysis_file_new_location(self, tmp_path: Path):
        """resolve_analysis_file finds file in new location."""
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()
        (analysis_dir / "analysis.xml").write_text("<analysis/>")

        result = resolve_analysis_file(tmp_path)
        assert result == analysis_dir / "analysis.xml"

    def test_resolve_analysis_file_old_location(self, tmp_path: Path):
        """resolve_analysis_file finds file in old flat location."""
        (tmp_path / "analysis.xml").write_text("<analysis/>")

        result = resolve_analysis_file(tmp_path)
        assert result == tmp_path / "analysis.xml"

    def test_resolve_analysis_file_prefers_new(self, tmp_path: Path):
        """resolve_analysis_file prefers new location when both exist."""
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()
        (analysis_dir / "analysis.xml").write_text("<new/>")
        (tmp_path / "analysis.xml").write_text("<old/>")

        result = resolve_analysis_file(tmp_path)
        assert result == analysis_dir / "analysis.xml"

    def test_resolve_analysis_file_default_new(self, tmp_path: Path):
        """resolve_analysis_file defaults to new location when neither exists."""
        result = resolve_analysis_file(tmp_path)
        assert result == tmp_path / "analysis" / "analysis.xml"

    def test_resolve_extraction_file_new_location(self, tmp_path: Path):
        """resolve_extraction_file finds file in new location."""
        extractions_dir = tmp_path / "extractions"
        extractions_dir.mkdir()
        (extractions_dir / "business-rules.xml").write_text("<rules/>")

        result = resolve_extraction_file(tmp_path, "business-rules")
        assert result == extractions_dir / "business-rules.xml"

    def test_resolve_extraction_file_old_location(self, tmp_path: Path):
        """resolve_extraction_file finds file in old flat location."""
        (tmp_path / "database.xml").write_text("<db/>")

        result = resolve_extraction_file(tmp_path, "database")
        assert result == tmp_path / "database.xml"


class TestMigrateOutput:
    """Tests for migrate_output function."""

    def test_migrate_output_moves_analysis(self, temp_repo_with_legacy_structure: Path):
        """migrate_output moves analysis.xml to analysis/."""
        output_dir = temp_repo_with_legacy_structure / "reforge_output" / "test-project"
        os.chdir(temp_repo_with_legacy_structure)

        result = migrate_output()

        assert result.migrated is True
        assert result.moved_files >= 1
        assert (output_dir / "analysis" / "analysis.xml").exists()
        assert not (output_dir / "analysis.xml").exists()

    def test_migrate_output_moves_extractions(self, temp_repo_with_legacy_structure: Path):
        """migrate_output moves extraction XMLs to extractions/."""
        output_dir = temp_repo_with_legacy_structure / "reforge_output" / "test-project"
        os.chdir(temp_repo_with_legacy_structure)

        result = migrate_output()

        assert (output_dir / "extractions" / "business-rules.xml").exists()
        assert (output_dir / "extractions" / "database.xml").exists()
        assert not (output_dir / "business-rules.xml").exists()
        assert not (output_dir / "database.xml").exists()

    def test_migrate_output_no_files_to_move(self, temp_repo: Path):
        """migrate_output handles empty output directory."""
        output_dir = temp_repo / "reforge_output" / "test-project"
        output_dir.mkdir(parents=True)
        os.chdir(temp_repo)

        result = migrate_output()

        assert result.migrated is True
        assert result.moved_files == 0

    def test_migrate_output_json_format(self, temp_repo_with_legacy_structure: Path):
        """migrate_output JSON output matches expected format."""
        os.chdir(temp_repo_with_legacy_structure)

        result = migrate_output()
        json_str = result.to_json()
        data = json.loads(json_str)

        assert "MIGRATED" in data
        assert "MOVED_FILES" in data
        assert "PROJECT_OUTPUT_DIR" in data
