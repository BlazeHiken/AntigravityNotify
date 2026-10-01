import json
import os
import shutil
import tempfile
from pathlib import Path

APP_NAME = "AntigravityNotify"

def get_config_dir() -> Path:
    """Returns the %APPDATA% directory for the application."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~")
    return Path(appdata) / APP_NAME

def get_config_path() -> Path:
    return get_config_dir() / "config.json"

def get_default_config() -> dict:
    """Returns the default configuration dictionary."""
    # Resolve the absolute path to the bundled sounds directory
    project_root = Path(__file__).resolve().parent.parent.parent
    sounds_dir = project_root / "sounds"
    
    return {
        "enabled": True,
        "volume": 0.8,
        "events": {
            "approval": {
                "enabled": True,
                "sound": str(sounds_dir / "request_test_sound.wav")
            },
            "complete": {
                "enabled": True,
                "sound": str(sounds_dir / "completion_test_sound.wav")
            }
        }
    }

def load_config() -> dict:
    """Loads the config from disk, returning defaults if missing or invalid."""
    config_path = get_config_path()
    defaults = get_default_config()
    
    if not config_path.exists():
        return defaults
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
            
        # Merge top-level keys
        for key in ["enabled", "volume"]:
            if key in user_config and isinstance(user_config[key], type(defaults[key])):
                defaults[key] = user_config[key]
                
        # Merge events
        if "events" in user_config and isinstance(user_config["events"], dict):
            for event_name in ["approval", "complete"]:
                if event_name in user_config["events"] and isinstance(user_config["events"][event_name], dict):
                    user_evt = user_config["events"][event_name]
                    if "enabled" in user_evt and isinstance(user_evt["enabled"], bool):
                        defaults["events"][event_name]["enabled"] = user_evt["enabled"]
                    if "sound" in user_evt and isinstance(user_evt["sound"], str):
                        defaults["events"][event_name]["sound"] = user_evt["sound"]
                        
        return defaults
    except Exception:
        # Fallback to defaults on invalid JSON
        return defaults

def save_config(config_data: dict) -> None:
    """Saves the config to disk atomically."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_path = get_config_path()
    temp_path = config_path.with_suffix(".tmp")
    
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
            
        # Atomic replace (shutil.move or os.replace)
        os.replace(temp_path, config_path)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise e
