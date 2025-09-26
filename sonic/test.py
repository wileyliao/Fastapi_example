# smoke_test.py
import base64
import requests
from pathlib import Path

URL = "https://test/url/sonic_entrance"   # 換成你的 API endpoint
AUDIO_PATH = Path("sample.wav")            # 換成你的測試音檔路徑

def test_base64():
    print("=== Testing JSON base64 upload ===")
    audio_bytes = AUDIO_PATH.read_bytes()
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    payload = {"base64": audio_b64}
    resp = requests.post(URL, json=payload)
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except Exception:
        print("Raw response:", resp.text)

def test_file_upload():
    print("\n=== Testing multipart/form-data upload ===")
    with open(AUDIO_PATH, "rb") as f:
        files = {"audio": f}
        resp = requests.post(URL, files=files)
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except Exception:
        print("Raw response:", resp.text)

if __name__ == "__main__":
    if not AUDIO_PATH.exists():
        print(f"❌ 找不到測試音檔: {AUDIO_PATH}")
    else:
        test_base64()
        test_file_upload()
