#!/usr/bin/env python3
"""
Dify API連携ボット
ターミナルからDifyアプリと対話できるPythonスクリプト
"""

import sys
from dify_bot import DifyBot


def start_chat(bot):
    """対話セッションを開始"""
    print("=" * 60)
    print("Difyボットと対話を開始します")
    print("終了するには 'exit', 'quit', 'q' のいずれかを入力してください")
    print("=" * 60)
    print()
    
    conversation_id = None
    
    while True:
        try:
            # ユーザー入力を取得
            user_input = input("You: ").strip()
            
            # 終了コマンドの確認
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n対話を終了します。ありがとうございました！")
                break
            
            # 空の入力をスキップ
            if not user_input:
                continue
            
            # メッセージを送信
            print("Bot: ", end="", flush=True)
            answer, new_conversation_id = bot.send_message(
                message=user_input,
                user_id='terminal_user',
                conversation_id=conversation_id
            )
            
            # 会話IDを更新
            if new_conversation_id:
                conversation_id = new_conversation_id
            
            if answer:
                print(answer)
            print()  # 空行を追加
            
        except KeyboardInterrupt:
            print("\n\n対話を中断します。")
            break
        except EOFError:
            print("\n\n対話を終了します。")
            break


def main():
    """メイン関数"""
    try:
        bot = DifyBot()
        start_chat(bot)
    except ValueError as e:
        print(f"エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

