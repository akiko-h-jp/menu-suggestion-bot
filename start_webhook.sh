#!/bin/bash
# LINE Webhookサーバー起動スクリプト

# 既存のプロセスを停止
echo "既存のプロセスを確認中..."
pkill -f "line_webhook.py" 2>/dev/null
sleep 1

# ポート8080が使用中か確認
if lsof -i :8080 > /dev/null 2>&1; then
    echo "警告: ポート8080がまだ使用中です。使用しているプロセスを停止してください。"
    lsof -i :8080
    exit 1
fi

echo "LINE Webhookサーバーを起動します..."
# AnacondaのPythonを使用
/opt/anaconda3/bin/python3 line_webhook.py

