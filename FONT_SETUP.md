# 日本語フォント設定ガイド

免許証に日本語を正しく表示するには、日本語フォントのインストールが必要です。

## 方法1: システムに日本語フォントをインストール（推奨）

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra
```

### macOS

```bash
brew install font-noto-sans-cjk-jp
```

### Windows

Windows には日本語フォントがデフォルトでインストールされています。

## 方法2: Docker を使用（最も簡単）

Dockerfileに日本語フォントのインストールが含まれているため、Docker Composeを使用すると自動的に日本語が表示されます。

```bash
docker-compose up --build
```

## 方法3: フォントファイルを手動配置

1. Noto Sans JPフォントをダウンロード:
   https://fonts.google.com/noto/specimen/Noto+Sans+JP

2. `backend/app/fonts/` ディレクトリに配置:
   ```bash
   mkdir -p backend/app/fonts
   # ダウンロードしたフォントファイルをコピー
   cp ~/Downloads/NotoSansJP-Regular.ttf backend/app/fonts/
   ```

3. サーバーを再起動

## トラブルシューティング

### 文字化けする場合

サーバーのログを確認してください:
```bash
# フォントが見つからない場合、デフォルトフォントにフォールバックします
# この場合、日本語は□□□のように表示されます
```

### フォントのパスを確認

```bash
# インストールされた日本語フォントを確認
fc-list :lang=ja

# または
find /usr/share/fonts -name "*Noto*" -o -name "*gothic*"
```

## 現在のステータス

システムに日本語フォントがインストールされていない場合、以下の動作になります:
- 日本語テキストが□（豆腐）文字で表示されます
- レイアウトは正常ですが、文字が読めません

日本語フォントをインストール後、サーバーを再起動してください。
