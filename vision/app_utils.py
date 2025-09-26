# app_utils.py
import io, logging, base64, cv2, numpy as np
from PIL import Image

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

# ---------------- Payload Utilities ----------------
def pick_payload_item(data: dict):
    if isinstance(data, dict) and "Data" in data:
        seq = data.get("Data") or []
        item = seq[0] if seq else None
    else:
        item = data
    if not isinstance(item, dict):
        raise ValueError("invalid payload: expect object or Data[0]")
    return item

def b64_to_bytes(b64: str) -> bytes:
    s = b64.split(",", 1)[-1].strip()
    try:
        return base64.b64decode(s, validate=True)
    except Exception:
        s2 = "".join(s.split())
        return base64.b64decode(s2, validate=True)

# ---------------- Image Utilities ----------------
def get_exif(raw: bytes) -> int:
    try:
        with Image.open(io.BytesIO(raw)) as im:
            exif = im.getexif()
            return int(exif.get(274, 1)) if exif else 1
    except Exception as e:
        logging.getLogger("app").warning(f"EXIF read error: {e}")
        return 1

def normalize_to_bgr(img: np.ndarray) -> np.ndarray:
    if img is None:
        raise ValueError("decode failed")
    if img.ndim == 3 and img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img
