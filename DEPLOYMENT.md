# デプロイメントガイド

このドキュメントでは、ペット健康免許証生成サービスをAWSにデプロイする手順を説明します。

## アーキテクチャ概要

```
┌─────────────┐
│  CloudFront │ (静的ファイル配信)
└──────┬──────┘
       │
┌──────▼──────┐
│   S3 Bucket │ (Vue3 Frontend)
└─────────────┘

┌─────────────┐
│     ALB     │ (Load Balancer)
└──────┬──────┘
       │
┌──────▼──────┐
│  ECS/Fargate│ (FastAPI Backend)
└──────┬──────┘
       │
┌──────▼──────┐
│  S3 Bucket  │ (画像ストレージ)
└─────────────┘
```

## 1. AWS準備

### S3バケット作成

#### 画像保存用バケット
```bash
aws s3 mb s3://pet-license-images --region ap-northeast-1
```

#### Frontend用バケット
```bash
aws s3 mb s3://pet-license-frontend --region ap-northeast-1
aws s3 website s3://pet-license-frontend --index-document index.html
```

### IAMユーザー作成

S3アクセス用のIAMユーザーを作成し、以下のポリシーをアタッチ:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::pet-license-images/*"
    }
  ]
}
```

## 2. Backend デプロイ (ECS/Fargate)

### Dockerfile作成

`backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 日本語フォントのインストール
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### ECRにプッシュ

```bash
# ECRリポジトリ作成
aws ecr create-repository --repository-name pet-license-api

# ログイン
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com

# ビルド
cd backend
docker build -t pet-license-api .

# タグ付け
docker tag pet-license-api:latest <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com/pet-license-api:latest

# プッシュ
docker push <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com/pet-license-api:latest
```

### ECSタスク定義

```json
{
  "family": "pet-license-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "pet-license-api",
      "image": "<account-id>.dkr.ecr.ap-northeast-1.amazonaws.com/pet-license-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "CLARIFAI_API_KEY",
          "value": "your-key"
        },
        {
          "name": "AWS_S3_BUCKET",
          "value": "pet-license-images"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/pet-license-api",
          "awslogs-region": "ap-northeast-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### ECSサービス作成

```bash
aws ecs create-service \
  --cluster pet-license-cluster \
  --service-name pet-license-api-service \
  --task-definition pet-license-api \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

## 3. Frontend デプロイ (S3 + CloudFront)

### ビルド

```bash
cd frontend
npm run build
```

### S3にアップロード

```bash
aws s3 sync dist/ s3://pet-license-frontend --delete
```

### CloudFront配信設定

```bash
aws cloudfront create-distribution \
  --origin-domain-name pet-license-frontend.s3-website-ap-northeast-1.amazonaws.com \
  --default-root-object index.html
```

## 4. 環境変数設定

### Backend (.env)

```env
CLARIFAI_API_KEY=your_clarifai_api_key
CLARIFAI_USER_ID=your_user_id
CLARIFAI_APP_ID=your_app_id
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=pet-license-images
AWS_REGION=ap-northeast-1
CORS_ORIGINS=https://your-cloudfront-domain.cloudfront.net
```

### Frontend (.env.production)

```env
VITE_API_URL=https://api.your-domain.com/api
```

## 5. セキュリティ設定

### S3バケットポリシー

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::pet-license-images/licenses/*"
    }
  ]
}
```

### セキュリティグループ

- ALB: 80, 443 ポート開放
- ECS: 8000 ポート (ALBからのみ)

## 6. モニタリング

### CloudWatch Logs

```bash
aws logs create-log-group --log-group-name /ecs/pet-license-api
```

### CloudWatch Alarms

- CPU使用率 > 80%
- メモリ使用率 > 80%
- エラーレート > 5%

## 7. CI/CD (GitHub Actions)

`.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-1
      - name: Build and push Docker image
        run: |
          cd backend
          docker build -t pet-license-api .
          docker tag pet-license-api:latest ${{ secrets.ECR_REGISTRY }}/pet-license-api:latest
          docker push ${{ secrets.ECR_REGISTRY }}/pet-license-api:latest
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster pet-license-cluster --service pet-license-api-service --force-new-deployment

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: cd frontend && npm install
      - name: Build
        run: cd frontend && npm run build
      - name: Deploy to S3
        run: |
          aws s3 sync frontend/dist/ s3://pet-license-frontend --delete
      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation --distribution-id ${{ secrets.CLOUDFRONT_ID }} --paths "/*"
```

## コスト見積もり

### 月間コスト (想定: 1000ユーザー/月)

- ECS Fargate (2タスク): $30
- S3 (ストレージ + リクエスト): $5
- CloudFront: $10
- Clarifai API: $20-50 (使用量による)
- ALB: $20

**合計: 約 $85-115/月**

## スケーリング戦略

1. **水平スケーリング**: ECSタスク数を増やす
2. **CloudFrontキャッシュ**: 静的コンテンツの配信を高速化
3. **S3転送高速化**: CloudFront経由での画像配信

## トラブルシューティング

### 画像アップロードエラー
- S3バケットポリシーを確認
- IAMロールの権限を確認

### AI分析が遅い
- Clarifai APIのレートリミットを確認
- 並列処理の実装を検討

### メモリ不足
- ECSタスクのメモリを増やす
- 画像処理の最適化
