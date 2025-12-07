# セットアップガイド

このガイドでは、ローカル環境でペット健康免許証生成サービスを起動する手順を説明します。

## 前提条件

- Python 3.9以上
- Node.js 18以上
- Docker & Docker Compose (オプション)
- Clarifai APIアカウント
- AWS アカウント (S3用)

## 1. リポジトリのクローン

```bash
git clone <repository-url>
cd pet_license
```

## 2. Backend セットアップ

### 2.1 環境変数の設定

```bash
cd backend
cp .env.example .env
```

`.env` ファイルを編集して以下の値を設定:

```env
CLARIFAI_API_KEY=your_clarifai_api_key
CLARIFAI_USER_ID=your_user_id
CLARIFAI_APP_ID=your_app_id
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=pet-license-images
AWS_REGION=ap-northeast-1
CORS_ORIGINS=http://localhost:5173
```

### 2.2 Clarifai APIキーの取得

1. [Clarifai](https://clarifai.com/) にアクセス
2. アカウントを作成またはログイン
3. 設定 > Security > Personal Access Tokens からAPIキーを生成
4. User ID と App ID を確認

### 2.3 AWS S3の設定

1. AWSコンソールでS3バケットを作成: `pet-license-images`
2. バケットのパブリックアクセス設定を適切に設定
3. IAMユーザーを作成し、S3アクセス権限を付与
4. アクセスキーとシークレットキーを取得

### 2.4 依存関係のインストール

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# パッケージのインストール
pip install -r requirements.txt
```

### 2.5 サーバーの起動

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

サーバーが起動したら、ブラウザで http://localhost:8000 にアクセスして動作確認。

API ドキュメント: http://localhost:8000/docs

## 3. Frontend セットアップ

### 3.1 環境変数の設定

```bash
cd frontend
cp .env.example .env
```

`.env` ファイルを編集:

```env
VITE_API_URL=http://localhost:8000/api
```

### 3.2 依存関係のインストール

```bash
npm install
```

### 3.3 開発サーバーの起動

```bash
npm run dev
```

ブラウザで http://localhost:5173 にアクセス。

## 4. Docker Composeを使用する場合（推奨）

### 4.1 環境変数の設定

```bash
# backend/.env を設定（上記参照）
```

### 4.2 起動

```bash
docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### 4.3 停止

```bash
docker-compose down
```

## 5. 動作確認

### 5.1 Backend API テスト

```bash
curl http://localhost:8000/health
# 期待される結果: {"status":"healthy"}
```

### 5.2 Frontend テスト

1. http://localhost:5173 にアクセス
2. ペット画像をアップロード
3. 「AI分析を実行」をクリック
4. 結果が表示されることを確認
5. フォームに情報を入力
6. 「免許証を生成」をクリック
7. 生成された免許証が表示されることを確認

## 6. トラブルシューティング

### Backend起動エラー

#### `ModuleNotFoundError: No module named 'app'`
```bash
# 正しいディレクトリにいるか確認
pwd
# /path/to/pet_license/backend であることを確認

# パッケージを再インストール
pip install -r requirements.txt
```

#### `clarifai_grpc` インストールエラー
```bash
# 最新版のpipに更新
pip install --upgrade pip

# 再度インストール
pip install clarifai-grpc
```

#### 日本語フォントが見つからない

**Linux:**
```bash
sudo apt-get install fonts-noto-cjk
```

**Mac:**
```bash
brew install font-noto-sans-cjk
```

**Windows:**
- システムに日本語フォントがインストールされていることを確認

### Frontend起動エラー

#### `npm install` エラー
```bash
# node_modulesを削除して再インストール
rm -rf node_modules package-lock.json
npm install
```

#### ポート5173が使用中
```bash
# vite.config.ts でポートを変更
server: {
  port: 3000  # 別のポートに変更
}
```

### API接続エラー

#### CORS エラー
- Backend の `.env` で `CORS_ORIGINS` に Frontend のURLが含まれているか確認
- 両方のサーバーが起動しているか確認

#### Clarifai API エラー
- APIキーが正しいか確認
- Clarifai アカウントの利用制限を確認
- インターネット接続を確認

#### AWS S3 エラー
- アクセスキーとシークレットキーが正しいか確認
- バケット名が正しいか確認
- IAMユーザーに適切な権限があるか確認
- バケットのリージョンが正しいか確認

## 7. 開発Tips

### Hot Reload

- Backend: `--reload` オプションでコードの変更が自動反映
- Frontend: Vite が自動的に変更を検出して再読み込み

### デバッグ

**Backend:**
```python
import pdb; pdb.set_trace()  # ブレークポイント設定
```

**Frontend:**
```typescript
console.log('デバッグ情報:', data)
```

### APIテスト

Swagger UI を使用: http://localhost:8000/docs

または curl:
```bash
# ペット分析
curl -X POST "http://localhost:8000/api/analyze-pet" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/pet_image.jpg"

# 免許証生成
curl -X POST "http://localhost:8000/api/generate-license" \
  -F "pet_image=@/path/to/pet_image.jpg" \
  -F "owner_name=山田太郎" \
  -F "pet_name=ポチ" \
  -F "issue_location=東京都渋谷区" \
  -F "issue_date=2024-01-01" \
  -F "gender=オス"
```

## 8. 次のステップ

- [DEPLOYMENT.md](./DEPLOYMENT.md) を参照してAWSへのデプロイ方法を確認
- カスタマイズや機能追加を検討
- テストの追加

## サポート

問題が発生した場合は、GitHubのIssuesに報告してください。
