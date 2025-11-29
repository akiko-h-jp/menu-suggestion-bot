#!/bin/bash
# cloudflared起動スクリプト

# ポート番号を.envファイルから読み込む（デフォルト: 8080）
PORT=${PORT:-8080}
if [ -f .env ]; then
    PORT=$(grep "^PORT=" .env | cut -d '=' -f2 | tr -d ' ')
    if [ -z "$PORT" ]; then
        PORT=8080
    fi
fi

echo "cloudflaredを起動します..."
echo "ポート: $PORT"
echo ""
echo "表示されたURL（例: https://xxxxx.trycloudflare.com）をコピーして、"
echo "LINE DevelopersコンソールのWebhook URLに設定してください:"
echo "  https://xxxxx.trycloudflare.com/callback"
echo ""
echo "停止するには Ctrl+C を押してください"
echo ""

# cloudflaredを起動
cloudflared tunnel --url http://localhost:$PORT

