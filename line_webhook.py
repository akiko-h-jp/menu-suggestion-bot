#!/usr/bin/env python3
"""
LINE Messaging API Webhookサーバー
DifyボットとLINEを連携
"""

import os
import sys
import json
import urllib3
from flask import Flask, request, abort
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage
from dotenv import load_dotenv
from dify_bot import DifyBot
import logging

# urllib3の警告を無効化
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数を読み込む
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path, override=True)

app = Flask(__name__)

# LINE Bot設定（環境変数の確認後に初期化）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# プレースホルダーの検出
PLACEHOLDERS = [
    'your_line_channel_access_token_here',
    'your_channel_access_token_here',
    'your_access_token_here',
    '実際のトークンをここに貼り付け',
    'your_line_channel_secret_here',
    'your_channel_secret_here',
    'your_secret_here',
    '実際のシークレットをここに貼り付け'
]

def is_placeholder(value, min_length=50):
    """値がプレースホルダーかどうかをチェック"""
    if not value:
        return False
    value_lower = value.lower().strip()
    # プレースホルダーの文字列が含まれているかチェック
    if any(ph.lower() in value_lower for ph in PLACEHOLDERS):
        return True
    # 長さが短すぎる場合はプレースホルダーの可能性
    if len(value.strip()) < min_length:
        return True
    return False

if not LINE_CHANNEL_ACCESS_TOKEN or is_placeholder(LINE_CHANNEL_ACCESS_TOKEN, min_length=50):
    logger.error("エラー: LINE_CHANNEL_ACCESS_TOKENが設定されていないか、プレースホルダーです")
    logger.error(".envファイルに実際のトークンを設定してください")
    sys.exit(1)

if not LINE_CHANNEL_SECRET or is_placeholder(LINE_CHANNEL_SECRET, min_length=20):
    logger.error("エラー: LINE_CHANNEL_SECRETが設定されていないか、プレースホルダーです")
    logger.error(".envファイルに実際のシークレットを設定してください")
    sys.exit(1)

# チャネルアクセストークンに非ASCII文字が含まれていないか確認
try:
    LINE_CHANNEL_ACCESS_TOKEN.encode('ascii')
except UnicodeEncodeError:
    logger.error("エラー: LINE_CHANNEL_ACCESS_TOKENに非ASCII文字が含まれています")
    logger.error("LINE Developersコンソールで新しいチャネルアクセストークンを生成してください")
    sys.exit(1)

# LINE Bot APIを初期化（署名検証用）
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Difyボットのインスタンス
dify_bot = None

# ユーザーごとの会話IDを保存（簡易的な実装）
# 本番環境では、データベースやRedisなどを使用することを推奨
conversations = {}


def get_dify_bot():
    """Difyボットのインスタンスを取得（遅延初期化）"""
    global dify_bot
    if dify_bot is None:
        try:
            dify_bot = DifyBot()
        except ValueError as e:
            logger.error(f"Difyボットの初期化に失敗: {e}")
            return None
    return dify_bot


def send_reply(reply_token, text):
    """LINE APIに返信を送信"""
    try:
        url = 'https://api.line.me/v2/bot/message/reply'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN.strip()}'
        }
        data = {
            'replyToken': reply_token,
            'messages': [{'type': 'text', 'text': text}]
        }
        http = urllib3.PoolManager()
        response = http.request(
            'POST',
            url,
            body=json.dumps(data, ensure_ascii=False).encode('utf-8'),
            headers=headers,
            timeout=10
        )
        if response.status == 200:
            logger.info(f"Replied: {text[:50]}...")
        else:
            error_body = response.data.decode('utf-8', errors='ignore')
            logger.error(f"LINE API error: {response.status} - {error_body}")
    except Exception as e:
        logger.error(f"Error sending reply: {e}", exc_info=True)


@app.route("/callback", methods=['POST'])
def callback():
    """LINE Webhookのエンドポイント"""
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        logger.error(f"Webhook処理中にエラーが発生しました: {e}", exc_info=True)
        abort(500)
    
    return 'OK', 200


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """テキストメッセージを処理"""
    user_id = event.source.user_id
    user_message = event.message.text
    
    bot = get_dify_bot()
    if bot is None:
        send_reply(event.reply_token, "申し訳ございません。現在サービスを利用できません。")
        return
    
    conversation_id = conversations.get(user_id)
    
    try:
        answer, new_conversation_id = bot.send_message(
            message=user_message,
            user_id=user_id,
            conversation_id=conversation_id
        )
        
        if new_conversation_id:
            conversations[user_id] = new_conversation_id
        
        reply_text = answer if answer else "申し訳ございません。現在応答を生成できませんでした。"
        send_reply(event.reply_token, reply_text)
        
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        send_reply(event.reply_token, "申し訳ございません。エラーが発生しました。")


@app.route("/", methods=['GET'])
def root():
    """ルートエンドポイント"""
    return {"status": "ok", "message": "LINE Webhook Server is running"}, 200


@app.route("/test", methods=['GET'])
def test():
    """テストエンドポイント - Difyボットの動作確認"""
    try:
        bot = get_dify_bot()
        if bot is None:
            return {"status": "error", "message": "Difyボットの初期化に失敗しました"}, 500
        
        # テストメッセージを送信
        answer, _ = bot.send_message("こんにちは", "test_user")
        if answer:
            return {
                "status": "ok",
                "message": "Difyボットは正常に動作しています",
                "test_response": answer[:100]  # 最初の100文字のみ
            }, 200
        else:
            return {
                "status": "error",
                "message": "Dify APIからの応答がありません"
            }, 500
    except Exception as e:
        logger.error(f"Test endpoint error: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }, 500


if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    logger.info(f"LINE Webhookサーバーを起動します (ポート: {port})")
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"エラー: ポート {port} が既に使用されています")
            logger.error("環境変数PORTで別のポート番号を指定してください（例: PORT=8000）")
            sys.exit(1)
        raise

