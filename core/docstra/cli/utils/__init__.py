"""Utilities for the Docstra CLI."""

from docstra.cli.utils.ui import (
    display_help_message,
    display_command_result,
    list_sessions,
    show_session_info,
    create_spinner,
    clear_screen,
    display_header,
)

from docstra.cli.utils.paths import (
    get_docstra_dir,
    ensure_docstra_dir,
    get_config_path,
    resolve_relative_path,
    is_docstra_initialized,
    suggest_file_paths,
)

from docstra.cli.utils.config import (
    configure_from_env,
    run_configuration_wizard,
    save_session_alias,
    get_session_aliases,
    get_session_by_alias,
    setup_history,
)

from docstra.cli.utils.session_utils import (
    get_user_input,
    select_session,
)

__all__ = [
    # UI utils
    "display_help_message",
    "display_command_result",
    "list_sessions",
    "show_session_info",
    "create_spinner",
    "clear_screen",
    "display_header",
    # Path utils
    "get_docstra_dir",
    "ensure_docstra_dir",
    "get_config_path",
    "resolve_relative_path",
    "is_docstra_initialized",
    "suggest_file_paths",
    # Config utils
    "configure_from_env",
    "run_configuration_wizard",
    "save_session_alias",
    "get_session_aliases",
    "get_session_by_alias",
    "setup_history",
    # Session utils
    "get_user_input",
    "select_session",
]
