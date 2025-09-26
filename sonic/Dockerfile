# 使用 PyTorch 官方映像作為基礎映像
FROM python:3.10

# 設置工作目錄
WORKDIR /app
RUN ln -snf /usr/share/zoneinfo/Asia/Taipei /etc/localtime && echo "Asia/Taipei" > /etc/timezone

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    cmake \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 啟動應用
CMD ["uvicorn", "--workers", "1", "app:app", "--host", "0.0.0.0", "--port", "3001", "--log-level", "debug"]

# docker run -d --name container_name --net ai --gpus all --restart always -v pc_path:container_path --log-driver=json-file --log-opt max-size=10m --log-opt max-file=3 image:version
# docker run -d --name pill_counter --net ai --gpus all --restart always -v C:\Projects\hsai_hos_pill_counter:/app --log-driver=json-file --log-opt max-size=10m --log-opt max-file=3 wjcl3gj94/toolkitpc:latest