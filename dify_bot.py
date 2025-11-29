#!/usr/bin/env python3
"""
Dify API連携ボットクラス
ターミナルとLINE Webhookの両方で使用可能
"""

import os
import requests
import json
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()


class DifyBot:
    """Dify APIと連携するボットクラス"""
    
    def __init__(self):
        """初期化：環境変数から設定を読み込む"""
        self.api_key = os.getenv('DIFY_API_KEY')
        self.base_url = os.getenv('DIFY_BASE_URL', 'https://api.dify.ai/v1')
        self.app_id = os.getenv('DIFY_APP_ID')  # オプション（通常はAPIキーに紐づいている）
        
        if not self.api_key:
            raise ValueError("DIFY_API_KEYが設定されていません。.envファイルにDIFY_API_KEYを設定してください。")
        
        # APIエンドポイント
        self.chat_endpoint = f"{self.base_url}/chat-messages"
        
        # ヘッダー情報
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def send_message(self, message, user_id='user', conversation_id=None):
        """
        Dify APIにメッセージを送信して応答を取得
        
        Args:
            message (str): ユーザーのメッセージ
            user_id (str): ユーザーID（デフォルト: 'user'）
            conversation_id (str): 会話ID（オプション）
        
        Returns:
            tuple: (応答テキスト, 新しい会話ID) または (None, None) エラーの場合
        """
        # リクエストボディ
        data = {
            'inputs': {},
            'query': message,
            'response_mode': 'blocking',
            'user': user_id
        }
        
        # 会話IDがある場合は追加
        if conversation_id:
            data['conversation_id'] = conversation_id
        
        try:
            # POSTリクエストを送信
            response = requests.post(
                self.chat_endpoint,
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            # ステータスコードを確認
            if response.status_code == 200:
                response_data = response.json()
                
                # 会話IDを取得
                new_conversation_id = response_data.get('conversation_id')
                
                # 応答を取得
                answer = response_data.get('answer', '応答がありませんでした。')
                return answer, new_conversation_id
            else:
                error_msg = f"エラーが発生しました。ステータスコード: {response.status_code}"
                try:
                    error_detail = response.json()
                    if 'message' in error_detail:
                        error_msg += f"\n詳細: {error_detail['message']}"
                except:
                    error_msg += f"\n応答: {response.text}"
                print(f"Dify API エラー: {error_msg}")
                return None, None
                
        except requests.exceptions.Timeout:
            print("エラー: リクエストがタイムアウトしました。")
            return None, None
        except requests.exceptions.ConnectionError:
            print("エラー: サーバーに接続できませんでした。")
            return None, None
        except requests.exceptions.RequestException as e:
            print(f"エラー: リクエスト中にエラーが発生しました: {e}")
            return None, None
        except json.JSONDecodeError:
            print("エラー: サーバーからの応答を解析できませんでした。")
            return None, None

