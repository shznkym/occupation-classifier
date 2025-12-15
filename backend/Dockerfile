# Backend Dockerfile for Occupation Classification API
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY app ./app
COPY data ./data

# ポート8000を公開
EXPOSE 8000

# Uvicornでアプリケーションを起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
