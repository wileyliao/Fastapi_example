from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np, cv2, logging, time, uvicorn

from app_utils import (
    attach_log_buffer, detach_log_buffer,
    pick_payload_item, b64_to_bytes,
    get_exif, normalize_to_bgr, FMT
)

from your_main import main

logging.basicConfig(level=logging.INFO, format=FMT, force=True)
logger = logging.getLogger("app")

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

@app.get("/your_endpoint")
def health_check():
    logger.info("I am alive!!")
    return {"status": "ok"}

@app.post("/your_endpoint")
async def image_receiver(request: Request, file: UploadFile | None = File(None)):
    logger.info(f'-----------------Request received-----------------')
    t_start = time.perf_counter()
    buf, h, targets = attach_log_buffer()

    try:
        raw, mode, guid = None, None, "none"
        if file is not None:
            raw = await file.read()
            if not raw:
                raise HTTPException(400, "empty file")
            mode = "file"
        else:
            data = await request.json()
            item = pick_payload_item(data)
            p = Payload(**item)
            guid = p.GUID or guid
            if p.base64:
                raw = b64_to_bytes(p.base64)
                mode = "base64"
            elif p.file_stream:
                raw = bytes(p.file_stream)
                mode = "file_stream"

        if raw is None:
            raise HTTPException(400, "no valid input")

        logger.info("INPUT TYPE: %s | SIZE: %d", mode, len(raw))
        logger.info("EXIF orientation: %s", get_exif(raw))

        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_UNCHANGED)
        img = normalize_to_bgr(img)

        t_inference_start = time.perf_counter()
        result = main(img, get_exif(raw))
        t_inference_end = time.perf_counter()
        logger.info(f'    Image decode time:{t_inference_start - t_start:.2f}sec')
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

