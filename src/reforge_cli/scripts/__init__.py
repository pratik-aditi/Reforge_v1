"""Reforge helper scripts - pure stdlib implementations of shell script functionality."""

from .common import (
    get_repo_root,
    get_config_value,
    get_project_name,
    get_output_dir,
    get_project_output_dir,
    ensure_dir,
    ReforgeError,
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

__all__ = [
    # common
    "get_repo_root",
    "get_config_value",
    "get_project_name",
    "get_output_dir",
    "get_project_output_dir",
    "ensure_dir",
    "ReforgeError",
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
]
