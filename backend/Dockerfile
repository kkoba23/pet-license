FROM python:3.11-slim

WORKDIR /app

# 日本語フォントと必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY ./app ./app

# 本番環境変数ファイルをコピー
COPY .env.production .env

# データディレクトリを作成
RUN mkdir -p /app/data /app/storage

# ポート公開
EXPOSE 8000

# アプリケーション起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
