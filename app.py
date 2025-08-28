# app.py
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from pydantic import BaseModel
from typing import List, Optional
import base64, numpy as np, cv2, uvicorn, logging, time, sys


FMT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=FMT, force=True)  # 覆蓋框架預設

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)  # 輸出到 stdout → Docker 才收得到
    h.setFormatter(logging.Formatter(FMT))
    logger.addHandler(h)

from main import main  # 你的主處理流程
app = FastAPI()

class Payload(BaseModel):
    base64: Optional[str] = None
    file_stream: Optional[List[int]] = None

def normalize_to_bgr(img: np.ndarray) -> np.ndarray:
    """
    將 OpenCV decode 出來的影像統一成 BGR 三通道 (H, W, 3)
    - BGRA → BGR
    - 灰階 → BGR
    """
    if img is None:
        raise HTTPException(status_code=400, detail="decode failed")

    # 透明通道 → BGR
    if img.ndim == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # 灰階 → BGR
    elif img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    return img

@app.get("/your_endpoint")
def health_check():
    logger.info("I am alive!!")
    # 你可以回傳固定訊息，也可以加邏輯檢查依賴元件有無異常
    return {"status": "ok"}

@app.post("/your_endpoint")
async def image_receiver(
    request: Request,
    file: UploadFile | None = File(None),   # multipart 時才會有值
):
    time_start = time.time()
    logger.info("=====START REQUEST: %s %s", request.method, request.url.path)
    raw = None
    mode = None

    # 1) 檔案路徑（multipart/form-data）
    if file is not None:
        raw = await file.read()
        if not raw:
            logger.error("file is none")
            raise HTTPException(status_code=400, detail="empty file")
        mode = "file"

    # 2) application/json
    else:
        try:
            data = await request.json()                 # 直接讀 JSON
        except Exception:
            logger.error("JSON decode fail")
            raise HTTPException(status_code=400, detail="invalid or missing JSON body")

        p = Payload(**data)                             # 交給 Pydantic 驗證
        if p.base64:
            raw = base64.b64decode(p.base64)
            mode = "base64"
        elif p.file_stream:
            raw = bytes(p.file_stream)
            mode = "file_stream"

    if raw is None:
        logger.error("INVALID INPUT (file/base64/file_stream)")
        raise HTTPException(status_code=400, detail="no valid input (expect multipart 'file' or JSON 'base64'/'file_stream')")

    logger.info("    INPUT TYPE: %s, ORIGIN SIZE: %d bytes", mode, len(raw))

    # decode → normalize
    arr = np.frombuffer(raw, dtype=np.uint8)
    decoded = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    img = normalize_to_bgr(decoded)
    time_getimage = time.time()
    logger.info("    Start inference")
    # 呼叫你的主流程，並避免未捕捉例外讓伺服器回 500
    result = main(img)
    time_inference = time.time()

    # 除錯方便，回傳當次模式；穩定後可拿掉
    time_end = time.time()
    logger.info(f"    Total time: {time_end - time_start} sec")
    logger.info(f"        IMAGE encode: {time_getimage - time_start} sec")
    logger.info(f"        Model Inference: {time_inference - time_getimage} sec")
    logger.info(f"=====END")

    return result

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)


