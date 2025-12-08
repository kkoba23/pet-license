# デプロイ手順

## バックエンド (ECS Fargate)

### 環境情報
- **クラスター**: `pet-license`
- **サービス**: `pet-license-backend`
- **リージョン**: `ap-northeast-1`
- **ECRリポジトリ**: `131800452026.dkr.ecr.ap-northeast-1.amazonaws.com/pet-license-backend`
- **タスク定義ファミリー**: `pet-license-backend`

### デプロイ手順

```bash
# 1. ECRログイン
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 131800452026.dkr.ecr.ap-northeast-1.amazonaws.com

# 2. Dockerイメージビルド
cd /home/krelations/pet_license/backend
docker build -t pet-license-backend .

# 3. ECRにプッシュ
docker tag pet-license-backend:latest 131800452026.dkr.ecr.ap-northeast-1.amazonaws.com/pet-license-backend:latest
docker push 131800452026.dkr.ecr.ap-northeast-1.amazonaws.com/pet-license-backend:latest

# 4. ECSサービス更新（新しいイメージで強制デプロイ）
aws ecs update-service --cluster pet-license --service pet-license-backend --force-new-deployment --region ap-northeast-1

# 5. デプロイ状況確認
aws ecs describe-services --cluster pet-license --services pet-license-backend --region ap-northeast-1 --query 'services[0].deployments[*].{status:status,taskDefinition:taskDefinition,runningCount:runningCount,rolloutState:rolloutState}'
```

### 注意事項
- **EC2は使用しない** - このプロジェクトはECS Fargateを使用
- タスク定義の変更が必要な場合は、最新リビジョンを取得してから更新すること
- EFSボリュームが `/app/data` にマウントされている（SQLiteデータベース永続化用）

### 環境変数について
環境変数は`backend/.env.production`ファイルに定義されており、Dockerイメージビルド時に自動的にコンテナに含まれます。
**タスク定義での環境変数設定は不要です。**

環境変数を変更する場合：
1. `backend/.env.production`を編集
2. Dockerイメージを再ビルド＆プッシュ
3. ECSサービスを更新

## フロントエンド (S3 + CloudFront)

### 環境情報
- **S3バケット**: `pet-license-frontend-131800452026`
- **CloudFront Distribution ID**: `E1EU30A83LF9H9`

### デプロイ手順

```bash
# 1. ビルド
cd /home/krelations/pet_license/frontend
VITE_API_URL="https://api.pet-license.jp/api" npm run build

# 2. S3にアップロード
aws s3 sync dist/ s3://pet-license-frontend-131800452026 --delete

# 3. CloudFrontキャッシュ無効化
aws cloudfront create-invalidation --distribution-id E1EU30A83LF9H9 --paths "/*"
```

## API エンドポイント
- **本番API**: https://api.pet-license.jp
- **本番フロントエンド**: https://pet-license.jp
