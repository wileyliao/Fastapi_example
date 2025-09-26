# audio_utils.py
import io, base64, logging
import numpy as np
import soundfile as sf

FMT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

# ---------------- Log Utilities ----------------
def attach_log_buffer(target_loggers=None):
    buf = io.StringIO()
    h = logging.StreamHandler(buf)
    h.setFormatter(logging.Formatter(FMT))
    targets = target_loggers or [
        logging.getLogger(),
        logging.getLogger("app")
    ]
    for lg in targets:
        lg.addHandler(h)
    return buf, h, targets

def detach_log_buffer(buf, h, targets):
    for lg in targets:
        lg.removeHandler(h)
    logs = buf.getvalue()
    buf.close()
    return logs

def b64_to_bytes(b64: str) -> bytes:
    """Decode base64 string to bytes"""
    s = b64.split(",", 1)[-1].strip()
    return base64.b64decode(s)

def load_audio(raw: bytes, sr: int = 16000) -> np.ndarray:
    """Decode audio bytes into waveform"""
    buf = io.BytesIO(raw)
    data, fs = sf.read(buf, dtype="float32")
    if fs != sr:
        import librosa
        data = librosa.resample(data, orig_sr=fs, target_sr=sr)
    return data
