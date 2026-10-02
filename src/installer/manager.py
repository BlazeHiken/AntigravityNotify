import json
import os
import sys
from pathlib import Path

# Identifier used to find our specific hooks inside the global config
APP_HOOK_KEY = "antigravity-notify-hook"

def get_global_hooks_path() -> Path:
    """Returns the path to the global Antigravity hooks.json."""
    home = Path(os.path.expanduser("~"))
    config_dir = home / ".gemini" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "hooks.json"

def get_entry_script_path() -> str:
    """Returns the absolute path to our hook entry script (native OS path)."""
    project_root = Path(__file__).resolve().parent.parent.parent
    entry_path = project_root / "src" / "hook" / "entry.py"
    return str(entry_path)

def get_python_executable() -> str:
    """Returns the current python executable path (native OS path)."""
    return sys.executable

def generate_our_hook_config() -> dict:
    """Generates the dictionary representing our hooks."""
    python_exe = get_python_executable()
    script_path = get_entry_script_path()
    
    # No quotes needed since paths have no spaces. cmd /c on Windows chokes on forward slashes + quotes.
    cmd_template = f'{python_exe} {script_path}'
    
    return {
        "PreToolUse": [
            {
                "matcher": "ask_question",
                "hooks": [
                    {
                        "type": "command",
                        "command": f'{cmd_template} PreToolUse',
                        "timeout": 5
                    }
                ]
            },
            {
                "matcher": "ask_permission",
                "hooks": [
                    {
                        "type": "command",
                        "command": f'{cmd_template} PreToolUse',
                        "timeout": 5
                    }
                ]
            },
            {
                "matcher": "run_command",
                "hooks": [
                    {
                        "type": "command",
                        "command": f'{cmd_template} PreToolUse',
                        "timeout": 5
                    }
                ]
            }
        ],
        "Stop": [
            {
                "type": "command",
                "command": f'{cmd_template} Stop',
                "timeout": 5
            }
        ]
    }

def install_hooks() -> bool:
    """
    Merges our hooks into the global hooks.json.
    Returns True if successful.
    """
    hooks_path = get_global_hooks_path()
    
    # Backup original if exists
    if hooks_path.exists():
        backup_path = hooks_path.with_suffix(".json.bak")
        try:
            import shutil
            shutil.copy2(hooks_path, backup_path)
        except Exception:
            pass
            
    current_hooks = {}
    if hooks_path.exists():
        try:
            with open(hooks_path, "r", encoding="utf-8") as f:
                current_hooks = json.load(f)
        except Exception:
            current_hooks = {}
            
    # Overwrite just our namespaced key
    current_hooks[APP_HOOK_KEY] = generate_our_hook_config()
    
    try:
        with open(hooks_path, "w", encoding="utf-8") as f:
            json.dump(current_hooks, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to install hooks: {e}")
        return False

def remove_hooks() -> bool:
    """
    Removes only our hooks from the global hooks.json.
    Returns True if successful.
    """
    hooks_path = get_global_hooks_path()
    
    if not hooks_path.exists():
        return True
        
    try:
        with open(hooks_path, "r", encoding="utf-8") as f:
            current_hooks = json.load(f)
            
        if APP_HOOK_KEY in current_hooks:
            del current_hooks[APP_HOOK_KEY]
            
            with open(hooks_path, "w", encoding="utf-8") as f:
                json.dump(current_hooks, f, indent=2)
                
        return True
    except Exception as e:
        print(f"Failed to remove hooks: {e}")
        return False

def check_status() -> bool:
    """
    Returns True if our hooks are correctly installed in the global hooks.json.
    """
    hooks_path = get_global_hooks_path()
    
    if not hooks_path.exists():
        return False
        
    try:
        with open(hooks_path, "r", encoding="utf-8") as f:
            current_hooks = json.load(f)
            
        if APP_HOOK_KEY in current_hooks:
            # Basic validation that our script path is what it should be
            our_hook = current_hooks[APP_HOOK_KEY]
            expected = generate_our_hook_config()
            
            # Checking one command to ensure the paths match
            try:
                cmd_in_file = our_hook["PreToolUse"][0]["hooks"][0]["command"]
                cmd_expected = expected["PreToolUse"][0]["hooks"][0]["command"]
                return cmd_in_file == cmd_expected
            except KeyError:
                return False
                
        return False
    except Exception:
        return False
