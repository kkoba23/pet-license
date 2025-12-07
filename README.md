# ペット健康免許証生成サービス

ペットの画像をアップロードすると、AIが自動的に犬・猫・品種を判別し、情報が入力された免許証画像を生成するサービスです。

## 機能

- ペット画像のアップロード
- Clarifai AIによる自動判別
  - 動物種別（犬/猫）
  - 品種の識別
- ペット健康免許証画像の自動生成
- AWS S3への画像保存

## 技術スタック

### Backend
- FastAPI
- Python 3.9+
- Clarifai API
- boto3 (AWS S3)
- Pillow (画像処理)

### Frontend
- Vue 3
- TypeScript
- Vite

### インフラ
- AWS S3 (画像ストレージ)
- AWS EC2 / ECS (将来の本番環境)

## プロジェクト構造

```
pet_license/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   └── utils/
│   └── requirements.txt
├── frontend/         # Vue 3 frontend
│   ├── src/
│   └── package.json
└── image/           # デザインリソース
```

## クイックスタート

詳細なセットアップ手順は [SETUP.md](./SETUP.md) を参照してください。

### Docker Compose を使用（推奨）

```bash
# 環境変数を設定
cp backend/.env.example backend/.env
# backend/.env を編集して API キーなどを設定

# 起動
docker-compose up --build
```

- Backend API: http://localhost:8000
- Frontend: http://localhost:5173
- API ドキュメント: http://localhost:8000/docs

### 手動セットアップ

#### Backend

```bash
cd backend
cp .env.example .env
# .env を編集して API キーなどを設定

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## ドキュメント

- [セットアップガイド](./SETUP.md) - ローカル開発環境のセットアップ
- [デプロイメントガイド](./DEPLOYMENT.md) - AWS本番環境へのデプロイ

## API エンドポイント

### `POST /api/analyze-pet`
ペット画像をAIで分析

**リクエスト:**
- `file`: 画像ファイル (multipart/form-data)

**レスポンス:**
```json
{
  "animal_type": "猫",
  "breed": "ブリティッシュショートヘア",
  "confidence": 0.95
}
```

### `POST /api/generate-license`
ペット健康免許証を生成

**リクエスト:**
- `pet_image`: ペット画像
- `owner_name`: 飼い主名
- `pet_name`: ペット名
- `issue_location`: 交付場所
- `issue_date`: 交付日 (YYYY-MM-DD)
- `gender`: 性別
- `color`: 毛色（オプション）
- `favorite_word`: お好きな一言（オプション）
- `microchip_no`: マイクロチップNo（オプション）

**レスポンス:**
```json
{
  "license_image_url": "https://s3.amazonaws.com/...",
  "pet_info": {
    "animal_type": "猫",
    "breed": "ブリティッシュショートヘア",
    "confidence": 0.95
  },
  "s3_key": "licenses/..."
}
```

## 技術的な特徴

- **AI画像認識**: Clarifai APIを使用した高精度なペット品種判別
- **リアルタイム画像生成**: Pillowを使用した免許証画像の動的生成
- **クラウドストレージ**: AWS S3への安全な画像保存
- **モダンフロントエンド**: Vue 3 + TypeScript + Vite
- **高速API**: FastAPI + 非同期処理
- **コンテナ対応**: Docker & Docker Compose対応

## ライセンス

MIT License
