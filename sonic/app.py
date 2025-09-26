# app.py
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import logging, time, uvicorn

from app_utils import b64_to_bytes, load_audio, FMT, attach_log_buffer, detach_log_buffer

# ----------------- Logger -----------------
logging.basicConfig(level=logging.INFO, format=FMT, force=True)
logger = logging.getLogger("audio_app")

# ----------------- FastAPI -----------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Payload(BaseModel):
    base64: Optional[str] = None
    file_stream: Optional[List[int]] = None
    GUID: Optional[str] = None

@app.get("/sonic_entrance")
def health_check():
    logger.info("Audio API alive!!")
    return {"status": "ok"}

@app.post("/sonic_entrance")
async def audio_receiver(request: Request, file: UploadFile | None = File(None)):
    logger.info("Request received")
    t_start = time.perf_counter()
    buf, h, targets = attach_log_buffer()
    raw, mode = None, None

    try:
        if file is not None:
            raw = await file.read()
            mode = "file"
        else:
            data = await request.json()
            p = Payload(**data)
            if p.base64:
                raw = b64_to_bytes(p.base64)
                mode = "base64"
            elif p.file_stream:
                raw = bytes(p.file_stream)
                mode = "file_stream"

        if raw is None:
            raise HTTPException(400, "no valid input")

        waveform = load_audio(raw)
        logger.info(f"INPUT TYPE: {mode} | LENGTH: {len(waveform)} samples")

        # ---- replace with your core audio function ----
        t_inference_start = time.perf_counter()
        result = "Sonic endpoint: this is a test message"
        t_inference_end = time.perf_counter()
        logger.info(f'    Waveform decode time:{t_inference_start - t_start:.2f}sec')
        logger.info(f'    Model inference time:{t_inference_end - t_inference_start:.2f}sec')
        logger.info(f'-----------------Total time:{t_inference_end - t_start:.2f}sec-----------------')
        logs = detach_log_buffer(buf, h, targets)

        response_data = {
            'Result': result,
            "logs": logs,
            'TimeTaken': f"{time.perf_counter() - t_start:.2f}秒"
        }
        return response_data

    except Exception as e:
        logger.exception("Unhandled error")
        logs = detach_log_buffer(buf, h, targets)
        error_response = {
            'Result': 'exception occur',
            "logs": logs,
            'TimeTaken': f"{time.perf_counter() - t_start:.2f}秒"
        }
        return error_response

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)