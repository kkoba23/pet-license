# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# パッケージファイルをコピー
COPY package*.json ./

# 依存関係インストール
RUN npm install

# ソースコードをコピー
COPY . .

# 環境変数を設定（ビルド時に上書き可能）
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# ビルド（型チェックをスキップ）
RUN npx vite build

# Production stage
FROM nginx:alpine

# Nginx設定をコピー
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ビルド成果物をコピー
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
