"""Reforge helper scripts - pure stdlib implementations of shell script functionality."""

from .common import (
    get_repo_root,
    get_config_value,
    get_project_name,
    get_output_dir,
    get_project_output_dir,
    ensure_dir,
    ReforgeError,
    # Subdirectory helpers
    get_analysis_dir,
    get_extractions_dir,
    get_derived_dir,
    get_generated_dir,
    get_diagrams_dir,
    get_audit_dir,
    # Backward-compatible resolvers
    resolve_analysis_file,
    resolve_extraction_file,
)
from .init_project import init_project, InitResult
from .check_prerequisites import check_prerequisites, PrerequisitesResult
from .manage_checkpoint import (
    read_checkpoint,
    create_checkpoint,
    delete_checkpoint,
    CheckpointStatus,
    CheckpointPath,
    CheckpointDeleted,
)
from .update_agent_context import update_agent_context, AgentContextResult
from .migrate_output import migrate_output, MigrationResult

__all__ = [
    # common - core
    "get_repo_root",
    "get_config_value",
    "get_project_name",
    "get_output_dir",
    "get_project_output_dir",
    "ensure_dir",
    "ReforgeError",
    # common - subdirectory helpers
    "get_analysis_dir",
    "get_extractions_dir",
    "get_derived_dir",
    "get_generated_dir",
    "get_diagrams_dir",
    "get_audit_dir",
    # common - backward-compatible resolvers
    "resolve_analysis_file",
    "resolve_extraction_file",
    # init_project
    "init_project",
    "InitResult",
    # check_prerequisites
    "check_prerequisites",
    "PrerequisitesResult",
    # manage_checkpoint
    "read_checkpoint",
    "create_checkpoint",
    "delete_checkpoint",
    "CheckpointStatus",
    "CheckpointPath",
    "CheckpointDeleted",
    # update_agent_context
    "update_agent_context",
    "AgentContextResult",
    # migrate_output
    "migrate_output",
    "MigrationResult",
]
