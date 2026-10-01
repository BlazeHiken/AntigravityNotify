import json
from typing import Optional

def get_internal_event(payload_str: str, cli_args: list[str]) -> Optional[str]:
    """
    Maps an Antigravity payload and CLI args to an internal event name:
    'approval' or 'complete'.
    Returns None if the event should be ignored.
    """
    if len(cli_args) > 1:
        # Some event schemas pass the event name as the first argument
        event_arg = cli_args[1]
        
        if event_arg == "PreToolUse":
            # For PreToolUse, we assume the tool name is in the payload.
            # However, Spike 0 proved we can just hook ask_permission or ask_question.
            # If this hook is firing for PreToolUse and we only registered it for prompting tools,
            # we can safely assume it's an 'approval' event.
            return "approval"
            
        if event_arg == "Stop":
            # The Stop event signifies task completion
            return "complete"
            
    return None
