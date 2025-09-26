# smoke_test.py
import base64
import requests
from pathlib import Path

URL = "https://kutech.tw:3000/vision_entrance"  # 換成你的 Vision API endpoint
IMAGE_PATH = Path("sample.jpg")           # 換成你的測試圖片路徑

def test_base64():
    print("=== Testing JSON base64 upload ===")
    img_bytes = IMAGE_PATH.read_bytes()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    payload = {"base64": img_b64}  # 若後端 key 不是 base64，改這裡
    resp = requests.post(URL, json=payload)
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except Exception:
        print("Raw response:", resp.text)

def test_file_upload():
    print("\n=== Testing multipart/form-data upload ===")
    with open(IMAGE_PATH, "rb") as f:
        files = {"file": f}
        resp = requests.post(URL, files=files)
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except Exception:
        print("Raw response:", resp.text)

if __name__ == "__main__":
    if not IMAGE_PATH.exists():
        print(f"❌ 找不到測試圖片: {IMAGE_PATH}")
    else:
        test_base64()
        test_file_upload()
