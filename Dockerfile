# 使用官方 Python 3.11 slim 映像作為基礎
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY . .

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Cloud Run 會自動設定 PORT 環境變數
# 預設使用 8080，但會被 Cloud Run 覆寫
ENV PORT=8080

# 暴露 port（僅作為文檔，Cloud Run 會使用 PORT 環境變數）
EXPOSE 8080

# 啟動應用程式
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 src.webhook.app:app
