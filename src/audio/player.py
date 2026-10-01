import threading
import sounddevice as sd
import soundfile as sf
from pathlib import Path

_current_stream = None
_lock = threading.Lock()

def play_sound(file_path: str, volume: float = 1.0, wait: bool = False) -> None:
    """
    Plays a WAV file with software volume scaling.
    If wait is True, blocks until playback finishes.
    Otherwise, plays asynchronously in a background thread.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return
        
    def _play():
        global _current_stream
        try:
            data, fs = sf.read(str(path), dtype='float32')
            volume_clamped = max(0.0, min(float(volume), 1.0))
            data = data * volume_clamped
            
            with _lock:
                if _current_stream is not None:
                    _current_stream.stop()
                    _current_stream.close()
                    
                _current_stream = sd.OutputStream(samplerate=fs, channels=data.shape[1] if len(data.shape) > 1 else 1)
                _current_stream.start()
            
            # Write is blocking, so we do it outside the lock to avoid deadlocking stop_sound
            _current_stream.write(data)
            
            with _lock:
                if _current_stream is not None:
                    _current_stream.stop()
                    _current_stream.close()
                    _current_stream = None
        except Exception as e:
            print(f"Audio playback error: {e}")

    if wait:
        _play()
    else:
        t = threading.Thread(target=_play, daemon=True)
        t.start()

def stop_sound() -> None:
    """Stops the currently playing sound."""
    global _current_stream
    with _lock:
        if _current_stream is not None:
            _current_stream.stop()
            _current_stream.close()
            _current_stream = None
