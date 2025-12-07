# ペット健康免許証生成サービス

ペットの画像をアップロードすると、AIが自動的に犬・猫・品種を判別し、免許証画像を生成するWebアプリケーションです。イベント運営者向けの管理画面とプリント機能も備えています。

## 機能

### 一般ユーザー向け
- ペット画像のアップロード
- Clarifai AIによる自動判別（動物種別・品種・毛色・表情など）
- OpenAI APIによるペットプロフィール自動生成（名前・飼い主名・特記事項など）
- CSS + Canvas による免許証画像のリアルタイム生成
- 生成した免許証画像のダウンロード

### イベント運営者向け
- **管理画面** (`/admin`)
  - イベント作成・管理
  - 発行済み免許証の一覧表示
  - 免許証データの検索・フィルタリング
- **プリント画面** (`/print/:eventId`)
  - イベント単位での免許証一括印刷
  - 印刷用レイアウト最適化
  - リアルタイムポーリングによる新規免許証の自動取得

## 技術スタック

### Backend
- FastAPI (Python 3.9+)
- SQLite (データベース)
- Clarifai API (画像認識)
- OpenAI API (プロフィール生成)
- boto3 (AWS S3)

### Frontend
- Vue 3 + Composition API
- TypeScript
- Vite
- HTML Canvas API (免許証画像生成)

### インフラ
- AWS S3 (画像ストレージ)
- AWS ECS (本番環境)
- Docker & Docker Compose

## プロジェクト構造

```
pet_license/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/           # APIエンドポイント
│   │   │   ├── pet_license.py
│   │   │   ├── admin.py
│   │   │   ├── events.py
│   │   │   └── licenses.py
│   │   ├── services/      # ビジネスロジック
│   │   │   ├── clarifai_service.py
│   │   │   ├── openai_service.py
│   │   │   ├── s3_service.py
│   │   │   └── license_generator.py
│   │   └── models/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── HomeView.vue      # メイン画面
│   │   │   ├── EventView.vue     # イベント用入力画面
│   │   │   ├── AdminLoginView.vue
│   │   │   ├── AdminEventsView.vue
│   │   │   ├── AdminEventDetailView.vue
│   │   │   └── PrintView.vue     # 印刷画面
│   │   ├── composables/
│   │   │   └── useLicenseCanvas.ts  # Canvas描画ロジック
│   │   └── api/
│   └── package.json
└── docker-compose.yml
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

## 環境変数

`backend/.env` に以下の環境変数を設定してください：

```
# Clarifai API (画像認識)
CLARIFAI_API_KEY=your_clarifai_api_key
CLARIFAI_PAT=your_clarifai_pat
CLARIFAI_USER_ID=your_clarifai_user_id
CLARIFAI_APP_ID=your_clarifai_app_id

# OpenAI API (プロフィール生成)
OPENAI_API_KEY=your_openai_api_key

# AWS S3 (画像ストレージ)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_S3_BUCKET=your_s3_bucket_name
AWS_REGION=ap-northeast-1

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## API エンドポイント

### ペット分析・免許証生成

#### `POST /api/analyze-pet`
ペット画像をAIで分析

**リクエスト:**
- `file`: 画像ファイル (multipart/form-data)

**レスポンス:**
```json
{
  "animal_type": "猫",
  "breed": "ブリティッシュショートヘア",
  "confidence": 0.95,
  "color": "グレー",
  "extra_features": {
    "expression": "穏やか",
    "posture": "座っている",
    "fur_amount": "短毛"
  }
}
```

#### `POST /api/generate-profile`
AIでペットプロフィールを自動生成

**リクエスト:**
- `animal_type`: 動物種別
- `breed`: 品種
- `color`: 毛色（オプション）
- その他の特徴（オプション）

**レスポンス:**
```json
{
  "gender": "オス",
  "pet_name": "むぎ",
  "owner_name": "もふもふパパ",
  "special_notes": ["もふもふ", "甘えん坊", "食いしん坊", "お座り上手", "人なつこい"],
  "favorite_word": "毎日がごきげん！"
}
```

### 管理機能

- `POST /api/admin/login` - 管理者ログイン
- `GET /api/events` - イベント一覧取得
- `POST /api/events` - イベント作成
- `GET /api/licenses` - 免許証一覧取得（ページネーション対応）

## 技術的な特徴

- **AI画像認識**: Clarifai APIを使用した高精度なペット品種判別
- **AIプロフィール生成**: OpenAI APIを使用したペット情報の自動生成
- **クライアントサイド画像生成**: CSS + HTML Canvasによる免許証画像のリアルタイム生成（サーバー負荷軽減）
- **クラウドストレージ**: AWS S3への安全な画像保存
- **モダンフロントエンド**: Vue 3 + TypeScript + Vite
- **高速API**: FastAPI + 非同期処理
- **コンテナ対応**: Docker & Docker Compose対応
- **イベント運営サポート**: 管理画面とプリント機能でイベント運営を効率化

## ドキュメント

- [セットアップガイド](./SETUP.md) - ローカル開発環境のセットアップ
- [デプロイメントガイド](./DEPLOYMENT.md) - AWS本番環境へのデプロイ
- [フォントセットアップ](./FONT_SETUP.md) - 日本語フォントの設定

## ライセンス

MIT License
