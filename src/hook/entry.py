import sys
import os
from pathlib import Path

# Add src to sys.path so we can import internal modules when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.hook.adapter import get_internal_event
from src.config.manager import load_config, get_config_dir
from src.audio.player import play_sound
import json
import time

def write_state(event_type: str) -> None:
    try:
        config_dir = get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        state_path = config_dir / "state.json"
        
        state_data = {
            "last_event": event_type,
            "timestamp": time.time()
        }
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state_data, f)
    except Exception:
        pass

def main():
    # Read stdin with a timeout to avoid blocking forever.
    # The IDE pipes JSON to stdin but may not close it promptly,
    # so sys.stdin.read() would block until the hook timeout kills us.
    import threading
    
    payload_str = ""
    
    def _read_stdin():
        nonlocal payload_str
        try:
            payload_str = sys.stdin.read()
        except Exception:
            pass
    
    reader = threading.Thread(target=_read_stdin, daemon=True)
    reader.start()
    reader.join(timeout=1.0)  # Wait at most 1 second for stdin
        
    try:
        # 1. Determine internal event type
        event_type = get_internal_event(payload_str, sys.argv)
        
        # 2. If valid event, check config and play sound
        if event_type:
            write_state(event_type)
            config = load_config()
            
            # Check master switch
            if config.get("enabled", False):
                events_config = config.get("events", {})
                event_config = events_config.get(event_type, {})
                
                # Check specific event switch
                if event_config.get("enabled", False):
                    sound_path = event_config.get("sound")
                    volume = config.get("volume", 1.0)
                    
                    if sound_path and os.path.exists(sound_path):
                        # Play the sound synchronously (block) so the script doesn't exit prematurely
                        play_sound(sound_path, volume=volume, wait=True)
                        
    except Exception:
        # Never crash the agent due to a notification error
        pass
        
    finally:
        # ALWAYS print {"decision": "allow"} to satisfy PreToolUse and avoid blocking the agent
        print('{"decision": "allow"}')
        sys.exit(0)

if __name__ == "__main__":
    main()
