"""Tests for reforge_cli.scripts - cross-platform Python utilities."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from reforge_cli import (
    __version__,
    app,
    scripts,
    copy_framework,
    create_memory_dirs,
    do_install,
    do_remove,
    do_update,
    generate_wrappers,
    merge_config,
    merge_settings,
    update_gitignore,
    validate_source,
    validate_target,
)
from reforge_cli.scripts import (
    check_prerequisites,
    check_xmllint_available,
    create_checkpoint,
    delete_checkpoint,
    format_list_schemas,
    format_structured_output,
    generate_suggestion,
    get_analysis_dir,
    get_audit_dir,
    get_available_schemas,
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
    parse_xmllint_errors,
    read_checkpoint,
    resolve_analysis_file,
    resolve_extraction_file,
    update_agent_context,
    validate_xml,
    ValidationError,
    ValidationResult,
    EXIT_VALID,
    EXIT_INVALID,
    EXIT_ERROR,
)
from reforge_cli.scripts.common import (
    ReforgeError,
    check_dir,
    check_file,
    ensure_dir,
)

runner = CliRunner()


@pytest.fixture(autouse=True)
def preserve_cwd():
    """Preserve the current working directory across tests."""
    original_cwd = os.getcwd()
    yield
    os.chdir(original_cwd)


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

        migrate_output()  # Result not needed, checking side effects

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


class TestXmlValidation:
    """Tests for validation.py XSD validation functions."""

    @pytest.fixture
    def temp_repo_with_schemas(self, temp_repo: Path) -> Path:
        """Create a temp repo with XSD schemas."""
        xsd_dir = temp_repo / ".reforge" / "schemas" / "xsd"
        xsd_dir.mkdir(parents=True)

        # Create a simple XSD schema for testing
        analysis_xsd = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://reforge.dev/schema/analysis"
           xmlns:tns="http://reforge.dev/schema/analysis"
           elementFormDefault="qualified">
  <xs:element name="analysis">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="project" minOccurs="0">
          <xs:complexType>
            <xs:attribute name="id" type="xs:string" use="required"/>
            <xs:attribute name="name" type="xs:string" use="required"/>
            <xs:attribute name="root-path" type="xs:string" use="required"/>
            <xs:attribute name="status" type="xs:string" use="optional"/>
          </xs:complexType>
        </xs:element>
        <xs:element name="files" minOccurs="0">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="file" minOccurs="0" maxOccurs="unbounded">
                <xs:complexType>
                  <xs:attribute name="path" type="xs:string" use="required"/>
                  <xs:attribute name="language" type="xs:string" use="required"/>
                  <xs:attribute name="file-type" type="xs:string" use="required"/>
                  <xs:attribute name="size-bytes" type="xs:integer" use="required"/>
                  <xs:attribute name="analysis-status" type="xs:string" use="required"/>
                  <xs:attribute name="hash" type="xs:string" use="optional"/>
                </xs:complexType>
              </xs:element>
            </xs:sequence>
            <xs:attribute name="count" type="xs:integer"/>
          </xs:complexType>
        </xs:element>
        <xs:element name="summary" minOccurs="0">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="languages" minOccurs="0">
                <xs:complexType>
                  <xs:sequence>
                    <xs:element name="language" minOccurs="0" maxOccurs="unbounded">
                      <xs:complexType>
                        <xs:attribute name="name" type="xs:string" use="required"/>
                        <xs:attribute name="count" type="xs:integer" use="required"/>
                        <xs:attribute name="lines" type="xs:integer" use="required"/>
                      </xs:complexType>
                    </xs:element>
                  </xs:sequence>
                </xs:complexType>
              </xs:element>
              <xs:element name="file-types" minOccurs="0">
                <xs:complexType>
                  <xs:sequence>
                    <xs:element name="type" minOccurs="0" maxOccurs="unbounded">
                      <xs:complexType>
                        <xs:attribute name="name" type="xs:string" use="required"/>
                        <xs:attribute name="count" type="xs:integer" use="required"/>
                      </xs:complexType>
                    </xs:element>
                  </xs:sequence>
                </xs:complexType>
              </xs:element>
            </xs:sequence>
            <xs:attribute name="total-files" type="xs:integer"/>
            <xs:attribute name="total-lines" type="xs:integer"/>
            <xs:attribute name="analyzed" type="xs:integer"/>
            <xs:attribute name="skipped" type="xs:integer"/>
          </xs:complexType>
        </xs:element>
      </xs:sequence>
      <xs:attribute name="version" type="xs:string" use="optional"/>
      <xs:attribute name="generated" type="xs:dateTime" use="optional"/>
    </xs:complexType>
  </xs:element>
</xs:schema>
"""
        (xsd_dir / "analysis.xsd").write_text(analysis_xsd)

        # Create other schema stubs for list-schemas test
        for name in ["business-rules", "database", "ui-flows", "workflows",
                     "user-stories", "audit-report", "correction-plan"]:
            (xsd_dir / f"{name}.xsd").write_text(f"<!-- {name} schema stub -->")

        return temp_repo

    def test_check_xmllint_available(self):
        """check_xmllint_available returns availability status."""
        available, version, instructions = check_xmllint_available()

        # Either xmllint is available or we get install instructions
        if available:
            assert version is not None
            assert instructions is None
        else:
            assert version is None
            assert instructions is not None
            assert "install" in instructions.lower()

    def test_get_available_schemas(self, temp_repo_with_schemas: Path):
        """get_available_schemas finds XSD files."""
        schemas = get_available_schemas(temp_repo_with_schemas)

        assert "analysis" in schemas
        assert schemas["analysis"].name == "analysis.xsd"
        assert len(schemas) == 8  # 8 schema files

    def test_get_available_schemas_empty_dir(self, temp_repo: Path):
        """get_available_schemas returns empty dict when no schemas."""
        schemas = get_available_schemas(temp_repo)
        assert schemas == {}

    def test_generate_suggestion_unknown_element(self):
        """generate_suggestion handles unknown element errors."""
        msg = "Element 'projetc': This element is not expected. Expected is 'project'."
        suggestion = generate_suggestion(msg, 10, "projetc")

        assert suggestion is not None
        assert "line 10" in suggestion
        assert "project" in suggestion

    def test_generate_suggestion_missing_attribute(self):
        """generate_suggestion handles missing attribute errors."""
        msg = "Missing required attribute 'status' on element"
        suggestion = generate_suggestion(msg, 5, "project")

        assert suggestion is not None
        assert "line 5" in suggestion
        assert "project" in suggestion

    def test_generate_suggestion_invalid_value(self):
        """generate_suggestion handles invalid value errors."""
        msg = "'abc' is not a valid value for type integer"
        suggestion = generate_suggestion(msg, 15, "count")

        assert suggestion is not None
        assert "line 15" in suggestion

    def test_generate_suggestion_generic(self):
        """generate_suggestion provides generic suggestion for unknown errors."""
        msg = "Some unknown error type"
        suggestion = generate_suggestion(msg, 20, None)

        assert suggestion is not None
        assert "line 20" in suggestion

    def test_parse_xmllint_errors_valid_output(self):
        """parse_xmllint_errors parses xmllint stderr correctly."""
        stderr = """test.xml:10: element projetc: Schemas validity error : Element 'projetc': This element is not expected.
test.xml:15: element file: Schemas validity error : Missing required attribute 'hash'.
test.xml fails to validate"""

        errors = parse_xmllint_errors(stderr, "test.xml")

        assert len(errors) == 2
        assert errors[0].line == 10
        assert errors[0].element == "projetc"
        assert "not expected" in errors[0].message
        assert errors[0].suggestion is not None

        assert errors[1].line == 15
        assert errors[1].element == "file"

    def test_parse_xmllint_errors_empty(self):
        """parse_xmllint_errors returns empty list for valid output."""
        stderr = "test.xml validates"

        errors = parse_xmllint_errors(stderr, "test.xml")

        assert len(errors) == 0

    def test_validate_xml_missing_file(self, temp_repo_with_schemas: Path):
        """validate_xml returns error for missing XML file."""
        result = validate_xml(
            xml_file=temp_repo_with_schemas / "nonexistent.xml",
            schema_type="analysis",
            repo_root=temp_repo_with_schemas,
        )

        assert result.valid is False
        assert result.exit_code == EXIT_ERROR
        assert len(result.errors) == 1
        assert "not found" in result.errors[0].message

    def test_validate_xml_missing_schema(self, temp_repo: Path):
        """validate_xml returns error for missing schema."""
        # Create XML file but no schemas
        xml_file = temp_repo / "test.xml"
        xml_file.write_text("<test/>")

        result = validate_xml(
            xml_file=xml_file,
            schema_type="nonexistent",
            repo_root=temp_repo,
        )

        assert result.valid is False
        assert result.exit_code == EXIT_ERROR
        assert "Schema not found" in result.errors[0].message

    def test_validate_xml_missing_xmllint(self, temp_repo_with_schemas: Path):
        """validate_xml returns error when xmllint not available."""
        xml_file = temp_repo_with_schemas / "test.xml"
        xml_file.write_text("<test/>")

        with patch("reforge_cli.scripts.validation.check_xmllint_available") as mock:
            mock.return_value = (False, None, "Install xmllint: apt install libxml2-utils")

            result = validate_xml(
                xml_file=xml_file,
                schema_type="analysis",
                repo_root=temp_repo_with_schemas,
            )

        assert result.valid is False
        assert result.exit_code == EXIT_ERROR
        assert "xmllint" in result.errors[0].message.lower()

    def test_validate_xml_valid_file(self, temp_repo: Path):
        """validate_xml returns success for valid XML."""
        # Use the fixture from tests/fixtures/validation
        fixtures_dir = Path(__file__).parent / "fixtures" / "validation"
        valid_xml = fixtures_dir / "valid-analysis.xml"

        if not valid_xml.exists():
            pytest.skip("Test fixture not found")

        available, _, _ = check_xmllint_available()
        if not available:
            pytest.skip("xmllint not available")

        # Use the actual project XSD schemas (copied to temp repo)
        project_xsd_dir = Path(__file__).parent.parent / ".reforge" / "schemas" / "xsd"
        if not project_xsd_dir.exists():
            pytest.skip("Project XSD schemas not found")

        # Copy actual XSD to temp repo
        target_xsd_dir = temp_repo / ".reforge" / "schemas" / "xsd"
        target_xsd_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy(project_xsd_dir / "analysis.xsd", target_xsd_dir / "analysis.xsd")

        result = validate_xml(
            xml_file=valid_xml,
            schema_type="analysis",
            repo_root=temp_repo,
        )

        assert result.valid is True
        assert result.exit_code == EXIT_VALID
        assert len(result.errors) == 0

    def test_validate_xml_invalid_file(self, temp_repo: Path):
        """validate_xml returns errors for invalid XML."""
        # Use the fixture from tests/fixtures/validation
        fixtures_dir = Path(__file__).parent / "fixtures" / "validation"
        invalid_xml = fixtures_dir / "invalid-analysis.xml"

        if not invalid_xml.exists():
            pytest.skip("Test fixture not found")

        available, _, _ = check_xmllint_available()
        if not available:
            pytest.skip("xmllint not available")

        # Use the actual project XSD schemas
        project_xsd_dir = Path(__file__).parent.parent / ".reforge" / "schemas" / "xsd"
        if not project_xsd_dir.exists():
            pytest.skip("Project XSD schemas not found")

        # Copy actual XSD to temp repo
        target_xsd_dir = temp_repo / ".reforge" / "schemas" / "xsd"
        target_xsd_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy(project_xsd_dir / "analysis.xsd", target_xsd_dir / "analysis.xsd")

        result = validate_xml(
            xml_file=invalid_xml,
            schema_type="analysis",
            repo_root=temp_repo,
        )

        assert result.valid is False
        assert result.exit_code == EXIT_INVALID
        assert len(result.errors) > 0

    def test_format_structured_output_valid(self):
        """format_structured_output formats valid result correctly."""
        result = ValidationResult(
            valid=True,
            exit_code=EXIT_VALID,
            xml_file="test.xml",
            schema_type="analysis",
            schema_file="analysis.xsd",
            elapsed_ms=50,
        )

        output = format_structured_output(result)

        assert "VALIDATION_OK" in output
        assert "FILE: test.xml" in output
        assert "SCHEMA: analysis" in output
        assert "ELAPSED_MS: 50" in output

    def test_format_structured_output_invalid(self):
        """format_structured_output formats invalid result correctly."""
        result = ValidationResult(
            valid=False,
            exit_code=EXIT_INVALID,
            xml_file="test.xml",
            schema_type="analysis",
            schema_file="analysis.xsd",
            errors=[
                ValidationError(
                    line=10,
                    column=None,
                    element="projetc",
                    message="Element not expected",
                    suggestion="Check spelling",
                    raw_output="test.xml:10: ...",
                )
            ],
            error_count=1,
        )

        output = format_structured_output(result)

        assert "VALIDATION_FAILED" in output
        assert "ERROR_COUNT: 1" in output
        assert "---" in output
        assert "LINE: 10" in output
        assert "ELEMENT: projetc" in output
        assert "MESSAGE: Element not expected" in output
        assert "SUGGESTION: Check spelling" in output

    def test_format_list_schemas(self, temp_repo_with_schemas: Path):
        """format_list_schemas formats schema list correctly."""
        schemas = get_available_schemas(temp_repo_with_schemas)
        output = format_list_schemas(schemas)

        assert "Available schemas:" in output
        assert "analysis" in output
        assert "business-rules" in output

    def test_validation_result_to_json(self):
        """ValidationResult.to_json produces valid JSON."""
        result = ValidationResult(
            valid=True,
            exit_code=EXIT_VALID,
            xml_file="test.xml",
            schema_type="analysis",
            schema_file="analysis.xsd",
            elapsed_ms=50,
        )

        json_str = result.to_json()
        data = json.loads(json_str)

        assert data["valid"] is True
        assert data["exit_code"] == 0
        assert data["xml_file"] == "test.xml"


class TestValidateCLI:
    """Tests for validate-xml CLI command."""

    def test_validate_xml_help(self):
        """validate-xml --help shows usage."""
        result = runner.invoke(scripts, ["validate-xml", "--help"])

        assert result.exit_code == 0
        assert "validate-xml" in result.output.lower() or "validate" in result.output.lower()

    def test_validate_xml_list_schemas(self, temp_repo: Path, monkeypatch):
        """validate-xml --list-schemas shows available schemas."""
        # Create schemas directory
        xsd_dir = temp_repo / ".reforge" / "schemas" / "xsd"
        xsd_dir.mkdir(parents=True)
        (xsd_dir / "analysis.xsd").write_text("<schema/>")
        (xsd_dir / "business-rules.xsd").write_text("<schema/>")

        monkeypatch.chdir(temp_repo)
        result = runner.invoke(scripts, ["validate-xml", "--list-schemas"])

        assert result.exit_code == 0
        assert "analysis" in result.output
        assert "business-rules" in result.output

    def test_validate_xml_missing_args(self, temp_repo: Path, monkeypatch):
        """validate-xml without args shows usage or error."""
        monkeypatch.chdir(temp_repo)
        result = runner.invoke(scripts, ["validate-xml"])

        # Should exit with error or show usage
        # Either behavior is acceptable
        assert result.exit_code != 0 or "Usage" in result.output or "Missing" in result.output


# --- CLI Integration Tests ---


class TestCLI:
    """Test CLI commands using Typer's CliRunner."""

    def test_version_flag(self):
        """--version prints version and exits."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert f"reforge v{__version__}" in result.output

    def test_help_without_command(self):
        """No args shows help."""
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "Usage:" in result.output or "Options:" in result.output

    def test_claude_install_dry_run(self, tmp_path: Path):
        """--claude --dry-run shows what would be done."""
        # Create a mock reforge home
        mock_home = tmp_path / "reforge-home"
        mock_home.mkdir()
        (mock_home / ".reforge" / "commands").mkdir(parents=True)
        (mock_home / ".reforge" / "config.json").write_text('{"project": {}}')
        (mock_home / ".reforge" / "schemas").mkdir()
        (mock_home / ".reforge" / "templates").mkdir()

        target = tmp_path / "target-project"
        target.mkdir()

        with patch("reforge_cli.get_reforge_home", return_value=mock_home):
            result = runner.invoke(app, ["--claude", "--dry-run", str(target)])

        assert result.exit_code == 0
        assert "Would" in result.output
        assert "Dry run complete" in result.output

    def test_claude_install_fails_if_already_installed(self, tmp_path: Path):
        """--claude fails when .reforge/ already exists."""
        mock_home = tmp_path / "reforge-home"
        mock_home.mkdir()
        (mock_home / ".reforge" / "commands").mkdir(parents=True)
        (mock_home / ".reforge" / "config.json").write_text('{"project": {}}')

        target = tmp_path / "target-project"
        target.mkdir()
        (target / ".reforge").mkdir()  # Already installed

        with patch("reforge_cli.get_reforge_home", return_value=mock_home):
            result = runner.invoke(app, ["--claude", str(target)])

        assert result.exit_code == 1
        assert "already has .reforge" in result.output

    def test_update_requires_existing_install(self, tmp_path: Path):
        """--claude --update fails without .reforge."""
        mock_home = tmp_path / "reforge-home"
        mock_home.mkdir()
        (mock_home / ".reforge" / "commands").mkdir(parents=True)
        (mock_home / ".reforge" / "config.json").write_text('{"project": {}}')

        target = tmp_path / "target-project"
        target.mkdir()
        # No .reforge directory

        with patch("reforge_cli.get_reforge_home", return_value=mock_home):
            result = runner.invoke(app, ["--claude", "--update", str(target)])

        assert result.exit_code == 1
        assert "No .reforge/ directory found" in result.output

    def test_remove_dry_run(self, tmp_path: Path):
        """--remove --dry-run shows what would be removed."""
        target = tmp_path / "target-project"
        target.mkdir()
        (target / ".reforge").mkdir()

        result = runner.invoke(app, ["--remove", "--dry-run", str(target)])

        assert result.exit_code == 0
        assert "Would remove" in result.output
        assert "Dry run complete" in result.output

    def test_remove_force_skips_confirmation(self, tmp_path: Path):
        """--remove --force skips confirmation."""
        target = tmp_path / "target-project"
        target.mkdir()
        (target / ".reforge").mkdir()
        (target / ".reforge" / "config.json").write_text("{}")

        result = runner.invoke(app, ["--remove", "--force", str(target)])

        assert result.exit_code == 0
        assert "Removed .reforge" in result.output
        assert not (target / ".reforge").exists()

    def test_remove_requires_reforge_dir(self, tmp_path: Path):
        """--remove fails when no .reforge/ directory."""
        target = tmp_path / "target-project"
        target.mkdir()

        result = runner.invoke(app, ["--remove", str(target)])

        assert result.exit_code == 1
        assert "No .reforge/ directory found" in result.output

    def test_init_project_command(self, temp_repo: Path):
        """init-project subcommand works via reforge-scripts."""
        result = runner.invoke(scripts, ["init-project", str(temp_repo)])

        assert result.exit_code == 0
        assert "Project initialized" in result.output

    def test_init_project_command_json(self, temp_repo: Path):
        """init-project --json outputs JSON."""
        result = runner.invoke(scripts, ["init-project", "--json", str(temp_repo)])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "PROJECT_NAME" in data

    def test_check_prerequisites_command(self, temp_repo: Path, monkeypatch):
        """check-prerequisites subcommand works via reforge-scripts."""
        monkeypatch.chdir(temp_repo)
        result = runner.invoke(scripts, ["check-prerequisites"])

        assert result.exit_code == 0
        assert "Prerequisites check" in result.output

    def test_checkpoint_invalid_action(self, temp_repo: Path, monkeypatch):
        """checkpoint with unknown action exits with error."""
        monkeypatch.chdir(temp_repo)
        result = runner.invoke(scripts, ["checkpoint", "invalid-action"])

        assert result.exit_code == 1
        assert "Unknown action" in result.output

    def test_checkpoint_read_command(self, temp_repo: Path, monkeypatch):
        """checkpoint read subcommand works."""
        monkeypatch.chdir(temp_repo)
        result = runner.invoke(scripts, ["checkpoint", "read"])

        assert result.exit_code == 0
        assert "No checkpoint found" in result.output

    def test_checkpoint_create_command(self, temp_repo: Path, monkeypatch):
        """checkpoint create subcommand works."""
        monkeypatch.chdir(temp_repo)
        result = runner.invoke(scripts, ["checkpoint", "create"])

        assert result.exit_code == 0
        assert "Checkpoint path" in result.output

    def test_checkpoint_delete_command(self, temp_repo: Path, monkeypatch):
        """checkpoint delete subcommand works."""
        monkeypatch.chdir(temp_repo)
        result = runner.invoke(scripts, ["checkpoint", "delete"])

        assert result.exit_code == 0
        # Either deleted or not found is valid
        assert "delete" in result.output.lower() or "checkpoint" in result.output.lower()

    def test_update_context_command(self, temp_repo_with_analysis: Path, monkeypatch):
        """update-context subcommand works via reforge-scripts."""
        monkeypatch.chdir(temp_repo_with_analysis)
        result = runner.invoke(scripts, ["update-context"])

        assert result.exit_code == 0
        # Either updated or skipped is valid (depending on CLAUDE.md presence)

    def test_update_context_without_analysis(self, temp_repo: Path, monkeypatch):
        """update-context fails without analysis.xml."""
        monkeypatch.chdir(temp_repo)
        result = runner.invoke(scripts, ["update-context"])

        assert result.exit_code == 1
        assert "analysis.xml not found" in result.output


# --- Install/Update/Remove Workflow Tests ---


@pytest.fixture
def mock_reforge_home(tmp_path: Path) -> Path:
    """Create a mock reforge framework home directory."""
    home = tmp_path / "reforge-home"
    reforge_dir = home / ".reforge"

    # Create framework structure
    (reforge_dir / "commands").mkdir(parents=True)
    (reforge_dir / "commands" / "analyze.md").write_text("> Analyze codebase\n\nContent")
    (reforge_dir / "commands" / "extract.md").write_text("> Extract knowledge\n\nContent")
    (reforge_dir / "schemas").mkdir()
    # Create XSD schemas subdirectory
    (reforge_dir / "schemas" / "xsd").mkdir()
    for name in ["analysis", "business-rules", "database", "ui-flows",
                 "workflows", "user-stories", "audit-report", "correction-plan"]:
        (reforge_dir / "schemas" / "xsd" / f"{name}.xsd").write_text(f"<!-- {name} XSD schema -->")
    (reforge_dir / "templates").mkdir()
    (reforge_dir / "memory").mkdir()
    (reforge_dir / "memory" / "constitution.md").write_text("# Constitution")
    (reforge_dir / "config.json").write_text(json.dumps({
        "project": {"name": "", "root": ".", "description": ""},
        "output": {"directory": "reforge_output"},
        "analysis": {"exclusions": []},
        "extraction": {"confidenceThreshold": 0.7},
    }))
    (reforge_dir / "README.md").write_text("# Reforge")

    return home


class TestValidation:
    """Tests for validation functions."""

    def test_validate_source_valid(self, mock_reforge_home: Path):
        """validate_source passes with valid source."""
        # Should not raise
        validate_source(mock_reforge_home)

    def test_validate_source_missing_commands(self, tmp_path: Path):
        """validate_source fails without commands directory."""
        import typer

        home = tmp_path / "incomplete"
        (home / ".reforge").mkdir(parents=True)
        (home / ".reforge" / "config.json").write_text("{}")

        with pytest.raises(typer.Exit):
            validate_source(home)

    def test_validate_source_missing_config(self, tmp_path: Path):
        """validate_source fails without config.json."""
        import typer

        home = tmp_path / "incomplete"
        (home / ".reforge" / "commands").mkdir(parents=True)

        with pytest.raises(typer.Exit):
            validate_source(home)

    def test_validate_target_prevents_self_install(self, mock_reforge_home: Path):
        """validate_target rejects installing into framework repo."""
        import typer

        with pytest.raises(typer.Exit):
            validate_target(mock_reforge_home, mock_reforge_home)

    def test_validate_target_rejects_nonexistent(self, tmp_path: Path, mock_reforge_home: Path):
        """validate_target rejects nonexistent directory."""
        import typer

        with pytest.raises(typer.Exit):
            validate_target(tmp_path / "nonexistent", mock_reforge_home)

    def test_validate_target_valid(self, tmp_path: Path, mock_reforge_home: Path):
        """validate_target passes with valid target."""
        target = tmp_path / "valid-target"
        target.mkdir()
        # Should not raise
        validate_target(target, mock_reforge_home)


class TestInstallWorkflow:
    """Test framework installation."""

    def test_copy_framework_copies_expected_dirs(self, tmp_path: Path, mock_reforge_home: Path):
        """copy_framework copies commands, schemas, templates."""
        target = tmp_path / "target"
        target.mkdir()

        copy_framework(target, mock_reforge_home, dry_run=False)

        assert (target / ".reforge" / "commands").is_dir()
        assert (target / ".reforge" / "schemas").is_dir()
        assert (target / ".reforge" / "templates").is_dir()
        assert (target / ".reforge" / "config.json").is_file()
        assert (target / ".reforge" / ".version").is_file()

    def test_copy_framework_dry_run(self, tmp_path: Path, mock_reforge_home: Path):
        """copy_framework dry run doesn't create files."""
        target = tmp_path / "target"
        target.mkdir()

        copy_framework(target, mock_reforge_home, dry_run=True)

        assert not (target / ".reforge").exists()

    def test_create_memory_dirs_creates_structure(self, tmp_path: Path):
        """create_memory_dirs creates memory structure."""
        target = tmp_path / "target"
        target.mkdir()

        create_memory_dirs(target, dry_run=False)

        assert (target / ".reforge" / "memory" / "history").is_dir()
        assert (target / ".reforge" / "memory" / "backups").is_dir()
        assert (target / ".reforge" / "memory" / "checkpoints").is_dir()
        assert (target / ".reforge" / "memory" / "clarifications").is_dir()
        assert (target / ".reforge" / "memory" / "logs").is_dir()
        assert (target / ".reforge" / "memory" / "analysis").is_dir()

    def test_generate_wrappers_creates_claude_commands(self, tmp_path: Path, mock_reforge_home: Path):
        """generate_wrappers creates .claude/commands/*.md."""
        target = tmp_path / "target"
        target.mkdir()

        generate_wrappers(target, mock_reforge_home, dry_run=False)

        assert (target / ".claude" / "commands").is_dir()
        assert (target / ".claude" / "commands" / "reforge.analyze.md").is_file()
        assert (target / ".claude" / "commands" / "reforge.extract.md").is_file()

        # Check wrapper content
        wrapper_content = (target / ".claude" / "commands" / "reforge.analyze.md").read_text()
        assert "description:" in wrapper_content
        assert "$ARGUMENTS" in wrapper_content

    def test_merge_settings_creates_new_file(self, tmp_path: Path):
        """merge_settings creates settings.local.json if missing."""
        target = tmp_path / "target"
        target.mkdir()

        merge_settings(target, dry_run=False)

        settings_file = target / ".claude" / "settings.local.json"
        assert settings_file.is_file()

        settings = json.loads(settings_file.read_text())
        assert "permissions" in settings
        assert "allow" in settings["permissions"]

    def test_merge_settings_adds_permissions(self, tmp_path: Path):
        """merge_settings adds reforge permissions to existing file."""
        target = tmp_path / "target"
        (target / ".claude").mkdir(parents=True)
        settings_file = target / ".claude" / "settings.local.json"
        settings_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(other:*)"]}
        }))

        merge_settings(target, dry_run=False)

        settings = json.loads(settings_file.read_text())
        assert "Bash(other:*)" in settings["permissions"]["allow"]
        assert any("reforge" in p for p in settings["permissions"]["allow"])

    def test_merge_settings_handles_malformed_json(self, tmp_path: Path):
        """merge_settings handles malformed existing settings."""
        target = tmp_path / "target"
        (target / ".claude").mkdir(parents=True)
        settings_file = target / ".claude" / "settings.local.json"
        settings_file.write_text("{ invalid json }")

        merge_settings(target, dry_run=False)

        settings = json.loads(settings_file.read_text())
        assert "permissions" in settings

    def test_update_gitignore_appends_entries(self, tmp_path: Path):
        """update_gitignore adds reforge entries."""
        target = tmp_path / "target"
        target.mkdir()
        gitignore = target / ".gitignore"
        gitignore.write_text("node_modules/\n")

        update_gitignore(target, dry_run=False)

        content = gitignore.read_text()
        assert "reforge_output/" in content
        assert "# Reforge Framework" in content
        assert "node_modules/" in content

    def test_update_gitignore_idempotent(self, tmp_path: Path):
        """update_gitignore doesn't duplicate entries."""
        target = tmp_path / "target"
        target.mkdir()
        gitignore = target / ".gitignore"

        # Run twice
        update_gitignore(target, dry_run=False)
        first_content = gitignore.read_text()
        update_gitignore(target, dry_run=False)
        second_content = gitignore.read_text()

        assert first_content == second_content

    def test_merge_config_creates_fresh(self, tmp_path: Path, mock_reforge_home: Path):
        """merge_config copies config when none exists."""
        target = tmp_path / "target"
        (target / ".reforge").mkdir(parents=True)

        merge_config(target, mock_reforge_home, dry_run=False)

        assert (target / ".reforge" / "config.json").is_file()

    def test_merge_config_preserves_user_fields(self, tmp_path: Path, mock_reforge_home: Path):
        """merge_config keeps project.name, exclusions, etc."""
        target = tmp_path / "target"
        (target / ".reforge").mkdir(parents=True)

        existing = {
            "project": {"name": "my-custom-name", "root": ".", "description": "My desc"},
            "output": {"directory": "custom_output"},
            "analysis": {"exclusions": ["vendor/", "build/"]},
            "extraction": {"confidenceThreshold": 0.9},
        }
        (target / ".reforge" / "config.json").write_text(json.dumps(existing))

        merge_config(target, mock_reforge_home, dry_run=False)

        result = json.loads((target / ".reforge" / "config.json").read_text())
        assert result["project"]["name"] == "my-custom-name"
        assert result["project"]["description"] == "My desc"
        assert result["output"]["directory"] == "custom_output"
        assert "vendor/" in result["analysis"]["exclusions"]
        assert result["extraction"]["confidenceThreshold"] == 0.9

    def test_do_install_full_flow(self, tmp_path: Path, mock_reforge_home: Path):
        """do_install creates complete installation."""
        target = tmp_path / "target"
        target.mkdir()

        do_install(target, mock_reforge_home, dry_run=False)

        # Check all components installed
        assert (target / ".reforge" / "commands").is_dir()
        assert (target / ".reforge" / "config.json").is_file()
        assert (target / ".reforge" / ".version").is_file()
        assert (target / ".claude" / "commands").is_dir()
        assert (target / ".claude" / "settings.local.json").is_file()
        assert (target / ".gitignore").is_file()

    def test_do_install_fails_if_exists(self, tmp_path: Path, mock_reforge_home: Path):
        """do_install fails when .reforge/ already exists."""
        import typer

        target = tmp_path / "target"
        target.mkdir()
        (target / ".reforge").mkdir()

        with pytest.raises(typer.Exit):
            do_install(target, mock_reforge_home, dry_run=False)


class TestXsdDeployment:
    """Tests for XSD schema deployment during install/update."""

    def test_install_copies_xsd_schemas(self, tmp_path: Path, mock_reforge_home: Path):
        """do_install copies XSD schemas to target."""
        target = tmp_path / "target"
        target.mkdir()

        do_install(target, mock_reforge_home, dry_run=False)

        # Verify XSD directory exists
        xsd_dir = target / ".reforge" / "schemas" / "xsd"
        assert xsd_dir.is_dir()

        # Verify all 8 XSD files are copied
        xsd_files = list(xsd_dir.glob("*.xsd"))
        assert len(xsd_files) == 8

        # Verify specific schemas exist
        assert (xsd_dir / "analysis.xsd").is_file()
        assert (xsd_dir / "business-rules.xsd").is_file()
        assert (xsd_dir / "database.xsd").is_file()

    def test_update_refreshes_xsd_schemas(self, tmp_path: Path, mock_reforge_home: Path):
        """do_update refreshes XSD schemas."""
        target = tmp_path / "target"
        target.mkdir()

        # Initial install
        do_install(target, mock_reforge_home, dry_run=False)

        # Modify an XSD file
        xsd_file = target / ".reforge" / "schemas" / "xsd" / "analysis.xsd"
        original_content = xsd_file.read_text()
        xsd_file.write_text("<!-- modified content -->")

        # Update
        do_update(target, mock_reforge_home, dry_run=False)

        # Should be restored to original
        restored_content = xsd_file.read_text()
        assert restored_content == original_content
        assert "modified content" not in restored_content


class TestUpdateWorkflow:
    """Test framework update."""

    def test_do_update_refreshes_commands(self, tmp_path: Path, mock_reforge_home: Path):
        """do_update refreshes framework files."""
        target = tmp_path / "target"
        target.mkdir()

        # Initial install
        do_install(target, mock_reforge_home, dry_run=False)

        # Modify a command file
        (target / ".reforge" / "commands" / "analyze.md").write_text("old content")

        # Update
        do_update(target, mock_reforge_home, dry_run=False)

        # Should be restored
        content = (target / ".reforge" / "commands" / "analyze.md").read_text()
        assert "old content" not in content

    def test_do_update_requires_existing(self, tmp_path: Path, mock_reforge_home: Path):
        """do_update fails without existing installation."""
        import typer

        target = tmp_path / "target"
        target.mkdir()

        with pytest.raises(typer.Exit):
            do_update(target, mock_reforge_home, dry_run=False)


class TestRemoveWorkflow:
    """Test framework removal."""

    def test_do_remove_cleans_reforge_dir(self, tmp_path: Path, mock_reforge_home: Path):
        """do_remove deletes .reforge/."""
        target = tmp_path / "target"
        target.mkdir()
        do_install(target, mock_reforge_home, dry_run=False)

        do_remove(target, force=True, dry_run=False)

        assert not (target / ".reforge").exists()

    def test_do_remove_cleans_wrappers(self, tmp_path: Path, mock_reforge_home: Path):
        """do_remove removes .claude/commands/reforge.*.md."""
        target = tmp_path / "target"
        target.mkdir()
        do_install(target, mock_reforge_home, dry_run=False)

        do_remove(target, force=True, dry_run=False)

        # Check wrappers removed
        if (target / ".claude" / "commands").exists():
            wrappers = list((target / ".claude" / "commands").glob("reforge.*.md"))
            assert len(wrappers) == 0

    def test_do_remove_cleans_settings(self, tmp_path: Path, mock_reforge_home: Path):
        """do_remove removes permissions from settings.local.json."""
        target = tmp_path / "target"
        target.mkdir()
        do_install(target, mock_reforge_home, dry_run=False)

        do_remove(target, force=True, dry_run=False)

        settings_file = target / ".claude" / "settings.local.json"
        if settings_file.exists():
            settings = json.loads(settings_file.read_text())
            permissions = settings.get("permissions", {}).get("allow", [])
            reforge_perms = [p for p in permissions if "reforge" in p]
            assert len(reforge_perms) == 0

    def test_do_remove_cleans_gitignore(self, tmp_path: Path, mock_reforge_home: Path):
        """do_remove removes reforge entries from .gitignore."""
        target = tmp_path / "target"
        target.mkdir()
        (target / ".gitignore").write_text("node_modules/\n")
        do_install(target, mock_reforge_home, dry_run=False)

        do_remove(target, force=True, dry_run=False)

        content = (target / ".gitignore").read_text()
        assert "reforge_output/" not in content
        assert "node_modules/" in content

    def test_do_remove_requires_reforge_dir(self, tmp_path: Path):
        """do_remove fails without .reforge/."""
        import typer

        target = tmp_path / "target"
        target.mkdir()

        with pytest.raises(typer.Exit):
            do_remove(target, force=True, dry_run=False)


# --- Edge Case Tests ---


class TestCheckpointEdgeCases:
    """Edge cases for checkpoint management."""

    def test_read_checkpoint_extraction_type(self, temp_repo: Path):
        """read_checkpoint works with extraction type."""
        os.chdir(temp_repo)

        # Create extraction checkpoint
        checkpoint_dir = temp_repo / ".reforge" / "memory" / "checkpoints"
        checkpoint_file = checkpoint_dir / "extraction-checkpoint.xml"
        checkpoint_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<checkpoint>
  <total-files>50</total-files>
  <processed-files>25</processed-files>
  <current-file>src/app.py</current-file>
  <started-at>2024-01-15T10:00:00Z</started-at>
  <elapsed-seconds>60</elapsed-seconds>
</checkpoint>
""")

        result = read_checkpoint(checkpoint_type="extraction")

        assert result.exists is True
        assert result.checkpoint_type == "extraction"
        assert result.total_files == 50
        assert result.processed_files == 25

    def test_read_checkpoint_zero_total_files(self, temp_repo: Path):
        """read_checkpoint handles zero total files."""
        os.chdir(temp_repo)

        checkpoint_dir = temp_repo / ".reforge" / "memory" / "checkpoints"
        checkpoint_file = checkpoint_dir / "analysis-checkpoint.xml"
        checkpoint_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<checkpoint>
  <total-files>0</total-files>
  <processed-files>0</processed-files>
  <current-file></current-file>
  <started-at>2024-01-15T10:00:00Z</started-at>
  <elapsed-seconds>0</elapsed-seconds>
</checkpoint>
""")

        result = read_checkpoint()

        assert result.exists is True
        assert result.total_files == 0
        assert result.percentage == 0  # Should not divide by zero

    def test_read_checkpoint_malformed_xml(self, temp_repo: Path):
        """read_checkpoint handles malformed XML gracefully."""
        os.chdir(temp_repo)

        checkpoint_dir = temp_repo / ".reforge" / "memory" / "checkpoints"
        checkpoint_file = checkpoint_dir / "analysis-checkpoint.xml"
        checkpoint_file.write_text("not valid xml at all")

        result = read_checkpoint()

        # Should still return a result with defaults
        assert result.exists is True
        assert result.total_files == 0
        assert result.processed_files == 0


class TestUpdateAgentContextEdgeCases:
    """Edge cases for agent context updates."""

    def test_update_gemini_context(self, temp_repo_with_analysis: Path):
        """update_agent_context works with gemini type."""
        gemini_md = temp_repo_with_analysis / "GEMINI.md"
        gemini_md.write_text("# Gemini Context\n\nExisting content.\n")

        os.chdir(temp_repo_with_analysis)
        result = update_agent_context(agent_type="gemini")

        assert result.agent_type == "gemini"
        assert result.updated is True
        content = gemini_md.read_text()
        assert "## Active Technologies" in content

    def test_update_copilot_context(self, temp_repo_with_analysis: Path):
        """update_agent_context creates .github/copilot-instructions.md."""
        github_dir = temp_repo_with_analysis / ".github"
        github_dir.mkdir()
        copilot_md = github_dir / "copilot-instructions.md"
        copilot_md.write_text("# Copilot Instructions\n")

        os.chdir(temp_repo_with_analysis)
        result = update_agent_context(agent_type="copilot")

        assert result.agent_type == "copilot"
        assert result.updated is True

    def test_update_cursor_context(self, temp_repo_with_analysis: Path):
        """update_agent_context updates .cursorrules."""
        cursorrules = temp_repo_with_analysis / ".cursorrules"
        cursorrules.write_text("# Cursor Rules\n")

        os.chdir(temp_repo_with_analysis)
        result = update_agent_context(agent_type="cursor")

        assert result.agent_type == "cursor"
        assert result.updated is True

    def test_update_windsurf_context(self, temp_repo_with_analysis: Path):
        """update_agent_context updates .windsurfrules."""
        windsurfrules = temp_repo_with_analysis / ".windsurfrules"
        windsurfrules.write_text("# Windsurf Rules\n")

        os.chdir(temp_repo_with_analysis)
        result = update_agent_context(agent_type="windsurf")

        assert result.agent_type == "windsurf"
        assert result.updated is True

    def test_unknown_agent_falls_back_to_claude(self, temp_repo_with_analysis: Path):
        """Unknown agent type defaults to claude."""
        claude_md = temp_repo_with_analysis / "CLAUDE.md"
        claude_md.write_text("# Claude Context\n")

        os.chdir(temp_repo_with_analysis)
        result = update_agent_context(agent_type="unknown-agent")

        assert result.agent_type == "claude"
        assert result.context_file == temp_repo_with_analysis / "CLAUDE.md"

    def test_raises_without_analysis(self, temp_repo: Path):
        """update_agent_context raises ReforgeError without analysis.xml."""
        os.chdir(temp_repo)

        with pytest.raises(ReforgeError, match="analysis.xml not found"):
            update_agent_context()

    def test_empty_languages_in_analysis(self, temp_repo: Path):
        """update_agent_context handles empty languages in analysis XML."""
        output_dir = temp_repo / "reforge_output" / "test-project"
        analysis_dir = output_dir / "analysis"
        analysis_dir.mkdir(parents=True)

        # Analysis with no languages
        analysis_xml = """<?xml version="1.0" encoding="UTF-8"?>
<analysis total-files="0" total-lines="0">
  <languages/>
</analysis>
"""
        (analysis_dir / "analysis.xml").write_text(analysis_xml)
        claude_md = temp_repo / "CLAUDE.md"
        claude_md.write_text("# Project\n")

        os.chdir(temp_repo)
        result = update_agent_context()

        assert result.languages == ""
        assert result.frameworks == ""


class TestPrerequisitesEdgeCases:
    """Edge cases for prerequisites check."""

    def test_require_extraction_missing(self, temp_repo_with_analysis: Path):
        """require_extraction raises when extraction missing."""
        os.chdir(temp_repo_with_analysis)

        with pytest.raises(ReforgeError, match="Extraction 'workflows' not found"):
            check_prerequisites(require_extraction="workflows")

    def test_require_extraction_passes(self, temp_repo_with_analysis: Path):
        """require_extraction passes when extraction exists."""
        output_dir = temp_repo_with_analysis / "reforge_output" / "test-project"
        extractions_dir = output_dir / "extractions"
        extractions_dir.mkdir(parents=True)
        (extractions_dir / "database.xml").write_text("<database/>")

        os.chdir(temp_repo_with_analysis)
        result = check_prerequisites(require_extraction="database")

        assert "database" in result.available_extractions

    def test_include_checkpoint_returns_path(self, temp_repo_with_analysis: Path):
        """include_checkpoint returns checkpoint path when exists."""
        checkpoint_dir = temp_repo_with_analysis / ".reforge" / "memory" / "checkpoints"
        checkpoint_file = checkpoint_dir / "analysis-checkpoint.xml"
        checkpoint_file.write_text("<checkpoint/>")

        os.chdir(temp_repo_with_analysis)
        result = check_prerequisites(include_checkpoint=True)

        assert result.checkpoint is not None
        assert result.checkpoint == checkpoint_file


# --- Common.py Helper Tests ---


class TestCommonHelpers:
    """Tests for common.py helper functions."""

    def test_ensure_dir_creates_directories(self, tmp_path: Path):
        """ensure_dir creates directory and parents."""
        deep_path = tmp_path / "a" / "b" / "c"
        assert not deep_path.exists()

        ensure_dir(deep_path)

        assert deep_path.is_dir()

    def test_ensure_dir_idempotent(self, tmp_path: Path):
        """ensure_dir is idempotent."""
        path = tmp_path / "existing"
        path.mkdir()

        # Should not raise
        ensure_dir(path)
        assert path.is_dir()

    def test_check_file_exists(self, tmp_path: Path):
        """check_file returns True for existing file."""
        file = tmp_path / "test.txt"
        file.write_text("content")

        assert check_file(file) is True

    def test_check_file_not_exists(self, tmp_path: Path):
        """check_file returns False for missing file."""
        file = tmp_path / "missing.txt"

        assert check_file(file) is False

    def test_check_file_directory(self, tmp_path: Path):
        """check_file returns False for directory."""
        assert check_file(tmp_path) is False

    def test_check_dir_exists(self, tmp_path: Path):
        """check_dir returns True for existing directory."""
        assert check_dir(tmp_path) is True

    def test_check_dir_not_exists(self, tmp_path: Path):
        """check_dir returns False for missing directory."""
        assert check_dir(tmp_path / "missing") is False

    def test_check_dir_file(self, tmp_path: Path):
        """check_dir returns False for file."""
        file = tmp_path / "test.txt"
        file.write_text("content")

        assert check_dir(file) is False

    def test_get_repo_root_prefers_reforge_over_git(self, tmp_path: Path):
        """get_repo_root prefers .reforge over .git."""
        # Create both markers
        (tmp_path / ".reforge").mkdir()
        (tmp_path / ".git").mkdir()

        subdir = tmp_path / "src" / "app"
        subdir.mkdir(parents=True)

        result = get_repo_root(subdir)

        # Should find .reforge first (it's checked first in the function)
        assert result == tmp_path
