# Difyボット - ターミナル・LINE対話アプリ

Difyで作成したAIアプリとPythonでAPI連携し、ターミナルまたはLINEからボットと対話できるアプリケーションです。

## 📋 目次

- [機能](#機能)
- [プロジェクト構成](#プロジェクト構成)
- [必要条件](#必要条件)
- [セットアップ](#セットアップ)
  - [1. 依存関係のインストール](#1-依存関係のインストール)
  - [2. Dify APIキーの取得](#2-dify-apiキーの取得)
  - [3. 環境変数の設定](#3-環境変数の設定)
- [使用方法](#使用方法)
  - [ターミナル版の実行](#ターミナル版の実行)
  - [LINE連携のセットアップ](#line連携のセットアップ)
- [Renderへのデプロイ](#renderへのデプロイ)
- [トラブルシューティング](#トラブルシューティング)
- [参考リンク](#参考リンク)

## 機能

- ✅ **Dify APIとの連携**: Difyで作成したAIアプリとシームレスに連携
- ✅ **ターミナル対話**: コマンドラインから直接ボットと対話
- ✅ **LINE連携**: LINE Messaging APIを使用してLINE上でボットを利用
- ✅ **会話履歴管理**: ユーザーごとの会話コンテキストを保持
- ✅ **安全な設定管理**: 環境変数によるAPIキー管理

## プロジェクト構成

```
.
├── main.py                  # ターミナル版のメインスクリプト
├── line_webhook.py          # LINE Webhookサーバー
├── dify_bot.py              # Dify API連携クラス（共通モジュール）
├── requirements.txt          # Python依存パッケージ
├── env.example               # 環境変数テンプレート
├── .env                      # 実際の環境変数（.gitignore対象）
├── Procfile                  # Render/Heroku用起動設定
├── runtime.txt               # Pythonバージョン指定
├── render.yaml               # Renderデプロイ設定（オプション）
├── start_webhook.sh          # Webhookサーバー起動スクリプト（ローカル用）
├── start_cloudflared.sh      # cloudflared起動スクリプト（ローカル用）
├── .gitignore                # Git除外設定
└── README.md                 # このファイル
```

### ファイル説明

- **`dify_bot.py`**: Dify APIとの通信を担当する共通クラス。ターミナル版とLINE版の両方で使用
- **`main.py`**: ターミナルから対話するためのメインスクリプト
- **`line_webhook.py`**: LINE Messaging APIのWebhookサーバー。LINEからのメッセージを受信し、Difyに送信して返信
- **`requirements.txt`**: 必要なPythonパッケージのリスト
- **`env.example`**: 環境変数のテンプレート。`.env`ファイルを作成する際の参考

## 必要条件

- **Python 3.7以上**
- **Difyアカウントとアプリ**
- **DifyのAPIキー**
- **LINE連携を使用する場合**: LINE DevelopersアカウントとMessaging APIチャネル

## セットアップ

### 1. 依存関係のインストール

プロジェクトディレクトリで以下のコマンドを実行：

```bash
pip install -r requirements.txt
```

**必要なパッケージ:**
- `requests`: HTTPリクエスト送信
- `python-dotenv`: 環境変数管理
- `flask`: Webhookサーバー（LINE連携用）
- `line-bot-sdk`: LINE Messaging API SDK

### 2. Dify APIキーの取得

1. [Dify](https://dify.ai) にログイン
2. ダッシュボードから連携したいアプリを選択
3. 左側メニューから「**APIアクセス**」をクリック
4. 「**APIキー**」セクションで新しいAPIキーを生成（または既存のキーを使用）
5. APIキーをコピー（**安全に保管してください**）

> **注意**: APIキーは通常アプリに紐づいているため、`DIFY_APP_ID`の設定は不要な場合が多いです。

### 3. 環境変数の設定

1. **`env.example`をコピーして`.env`ファイルを作成**

   ```bash
   cp env.example .env
   ```

2. **`.env`ファイルを編集**

   テキストエディタで`.env`ファイルを開き、以下の値を設定：

   ```env
   # Dify API設定（必須）
   DIFY_API_KEY=your_actual_api_key_here
   DIFY_BASE_URL=https://api.dify.ai/v1
   
   # LINE連携設定（LINE連携を使用する場合のみ）
   # LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here
   # LINE_CHANNEL_SECRET=your_line_channel_secret_here
   # PORT=8080
   ```

   - `DIFY_API_KEY`: ステップ2で取得したAPIキーに置き換え
   - `DIFY_BASE_URL`: 通常はデフォルトのままでOK（カスタムドメイン使用時のみ変更）
   - LINE連携の設定は後述の「LINE連携のセットアップ」を参照

## 使用方法

### ターミナル版の実行

1. **アプリケーションを起動**

   ```bash
   python3 main.py
   ```

2. **ボットと対話**

   - 「You:」と表示されたらメッセージを入力してEnter
   - ボットからの応答が「Bot:」の後に表示されます

3. **対話を終了**

   - `exit`、`quit`、または `q` と入力してEnter
   - `Ctrl+C` でも中断可能

**使用例:**
```
You: こんにちは
Bot: こんにちは！何かお手伝いできることはありますか？

You: 3日分の夕飯の献立を提案してください
Bot: 以下、3日分の夕飯の献立をご提案します...

You: exit
対話を終了します。ありがとうございました！
```

### LINE連携のセットアップ

LINE上でボットを使用する場合は、以下の手順でセットアップしてください。

#### ステップ1: LINE Developersでチャネルを作成

1. [LINE Developersコンソール](https://developers.line.biz/ja/)にアクセスしてログイン
2. 初めての場合は「プロバイダーを作成」
3. 「チャネルを作成」→「Messaging API」を選択
4. チャネル名、説明、カテゴリーなどを入力して作成

#### ステップ2: LINEチャネルの設定を取得

1. **チャネルアクセストークンを取得**
   - 作成したチャネルの「Messaging API」タブを開く
   - 「チャネルアクセストークン（長期）」セクションで「発行」をクリック
   - 表示されたトークンをコピー（**安全に保管**）

2. **チャネルシークレットを取得**
   - 同じページの「基本設定」タブを開く
   - 「チャネルシークレット」をコピー（**安全に保管**）

#### ステップ3: 環境変数にLINE設定を追加

`.env`ファイルに以下の設定を追加：

```env
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here
LINE_CHANNEL_SECRET=your_line_channel_secret_here
PORT=8080
```

- `your_line_channel_access_token_here`: ステップ2で取得したチャネルアクセストークン
- `your_line_channel_secret_here`: ステップ2で取得したチャネルシークレット
- `PORT`: Webhookサーバーのポート番号（デフォルト: 8080）

#### ステップ4: Webhookサーバーを起動

**方法1: スクリプトを使用（推奨）**

```bash
./start_webhook.sh
```

**方法2: 直接実行**

```bash
python3 line_webhook.py
```

サーバーが起動すると、以下のようなメッセージが表示されます：

```
INFO:__main__:LINE Webhookサーバーを起動します (ポート: 8080)
 * Running on http://0.0.0.0:8080
```

#### ステップ5: ローカルサーバーを公開（開発・テスト用）

ローカル環境でテストする場合、以下のいずれかの方法で公開URLを取得します。

**方法1: cloudflared（推奨）**

Homebrewを使用する場合：

```bash
# Homebrewのインストール（未インストールの場合）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# cloudflaredのインストール
brew install cloudflared

# トンネルを起動
./start_cloudflared.sh
# または
cloudflared tunnel --url http://localhost:8080
```

表示されたURL（例: `https://xxxxx.trycloudflare.com`）を使用します。

**方法2: localtunnel（簡単）**

Node.jsがあれば、インストール不要で使用できます：

```bash
npx localtunnel --port 8080
```

表示されたURL（例: `https://xxxxx.loca.lt`）を使用します。

#### ステップ6: LINE DevelopersでWebhook URLを設定

1. LINE Developersコンソールで作成したチャネルの「Messaging API」タブを開く
2. 「Webhook URL」に `https://your-tunnel-url.com/callback` を設定
   - 例: `https://xxxxx.trycloudflare.com/callback`
3. 「Webhookの利用」を「利用する」に設定
4. 「検証」ボタンをクリックして接続を確認
5. 「応答設定」セクションで：
   - 「Webhook」を有効化
   - 「応答メッセージ」を無効化（Webhookで応答するため）

#### ステップ7: 動作確認

1. LINEアプリで作成した公式アカウントを友だち追加
2. 公式アカウントにメッセージを送信
3. Difyボットからの応答が返ってくることを確認

## Renderへのデプロイ

Renderを使用して本番環境にデプロイする手順です。

### 前提条件

- GitHubアカウント
- Renderアカウント（[Render](https://render.com)で無料アカウントを作成）
- GitHubリポジトリにコードがプッシュ済み

### ステップ1: GitHubにコードをプッシュ

1. **Gitリポジトリを初期化**（まだの場合）

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **GitHubリポジトリに接続**

   ```bash
   git remote add origin https://github.com/your-username/your-repo-name.git
   git branch -M main
   git push -u origin main
   ```

   > **注意**: `your-username`と`your-repo-name`を実際の値に置き換えてください

### ステップ2: RenderでWebサービスを作成

1. **Renderダッシュボードにアクセス**
   - [Render Dashboard](https://dashboard.render.com)にログイン

2. **新しいWebサービスを作成**
   - 「New +」→「Web Service」をクリック
   - GitHubリポジトリを選択（または接続）

3. **サービス設定**
   - **Name**: `dify-line-bot`（任意の名前）
   - **Region**: 最寄りのリージョンを選択
   - **Branch**: `main`（または使用しているブランチ）
   - **Root Directory**: （空白のまま）
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn line_webhook:app --bind 0.0.0.0:$PORT`

### ステップ3: 環境変数を設定

Renderダッシュボードの「Environment」セクションで以下の環境変数を設定：

| キー | 値 | 説明 |
|------|-----|------|
| `DIFY_API_KEY` | あなたのDify APIキー | DifyのAPIキー |
| `DIFY_BASE_URL` | `https://api.dify.ai/v1` | DifyのベースURL（通常はデフォルト） |
| `LINE_CHANNEL_ACCESS_TOKEN` | あなたのLINEチャネルアクセストークン | LINE Developersから取得 |
| `LINE_CHANNEL_SECRET` | あなたのLINEチャネルシークレット | LINE Developersから取得 |
| `PORT` | （自動設定） | Renderが自動的に設定します |

> **重要**: 環境変数は「Secret」として設定され、ログに表示されません

### ステップ4: デプロイ

1. **「Create Web Service」をクリック**
   - Renderが自動的にビルドとデプロイを開始します

2. **デプロイの完了を待つ**
   - ビルドログを確認して、エラーがないか確認
   - 通常、数分でデプロイが完了します

3. **サービスURLを確認**
   - デプロイが完了すると、`https://your-service-name.onrender.com`のようなURLが表示されます

### ステップ5: LINE DevelopersでWebhook URLを更新

1. **RenderのサービスURLをコピー**
   - 例: `https://dify-line-bot.onrender.com`

2. **LINE DevelopersコンソールでWebhook URLを設定**
   - LINE Developersコンソール → 作成したチャネル → 「Messaging API」タブ
   - 「Webhook URL」に `https://your-service-name.onrender.com/callback` を設定
   - 「検証」ボタンをクリックして接続を確認

3. **Webhookを有効化**
   - 「Webhookの利用」を「利用する」に設定
   - 「応答設定」で「Webhook」を有効化、「応答メッセージ」を無効化

### ステップ6: 動作確認

1. **LINEアプリで公式アカウントを友だち追加**
2. **メッセージを送信**
3. **ボットからの応答を確認**

### Renderデプロイのメリット

- ✅ **無料プランあり**: 個人利用なら無料で利用可能
- ✅ **自動デプロイ**: GitHubにプッシュすると自動的にデプロイ
- ✅ **HTTPS対応**: SSL証明書が自動的に設定される
- ✅ **環境変数管理**: セキュアな環境変数管理
- ✅ **ログ確認**: ダッシュボードからログを確認可能

### 注意事項

- **無料プランの制限**: 
  - 15分間アクセスがないとスリープします（次回アクセス時に自動復帰）
  - 本番環境では有料プランの検討をおすすめします
- **環境変数の管理**: 
  - 環境変数はRenderダッシュボードで管理し、`.env`ファイルは使用しません
- **ログの確認**: 
  - Renderダッシュボードの「Logs」タブでアプリケーションのログを確認できます

## トラブルシューティング

### Dify API関連

**エラー: DIFY_API_KEYが設定されていません**

- `.env`ファイルが存在するか確認
- `.env`ファイルに`DIFY_API_KEY`が正しく設定されているか確認
- `env.example`をコピーして`.env`を作成し、値を設定し直してください

**エラー: サーバーに接続できませんでした**

- インターネット接続を確認
- Difyのサービスステータスを確認
- `DIFY_BASE_URL`が正しいか確認

**エラー: ステータスコード 401**

- DifyのダッシュボードでAPIキーが有効か確認
- `.env`ファイルの`DIFY_API_KEY`が正しく設定されているか確認
- 新しいAPIキーを生成して設定し直してください

### LINE連携関連

**エラー: Invalid signature**

- `.env`ファイルの`LINE_CHANNEL_SECRET`が正しいか確認
- LINE DevelopersコンソールでWebhook URLが正しく設定されているか確認
- トンネルツール（cloudflared等）のURLが変更されていないか確認

**エラー: ポートが既に使用されています**

- `.env`ファイルで`PORT`を別のポート番号に変更（例: `PORT=8000`）
- または、使用中のポートを確認：
  ```bash
  lsof -i :8080
  ```

**エラー: ModuleNotFoundError**

- 必要なパッケージがインストールされているか確認：
  ```bash
  pip install -r requirements.txt
  ```
- Anacondaを使用している場合、AnacondaのPythonを使用：
  ```bash
  /opt/anaconda3/bin/python3 line_webhook.py
  ```

**ボットからの返信がない**

1. Webhookサーバーが起動しているか確認
2. トンネルツール（cloudflared等）が起動しているか確認
3. LINE Developersコンソールで：
   - 「Webhookの利用」が「利用する」になっているか確認
   - 「応答設定」でWebhookが有効になっているか確認
4. サーバーのログを確認してエラーがないか確認

### その他

**エラー: 環境変数が読み込まれない**

- `.env`ファイルがプロジェクトのルートディレクトリにあるか確認
- `.env`ファイルの書式が正しいか確認（`KEY=value`の形式、余分なスペースがないか）
- シェルの環境変数と競合していないか確認

## セキュリティに関する注意事項

- ⚠️ **`.env`ファイルは絶対にGitにコミットしないでください**
  - `.gitignore`に含まれていますが、念のため確認してください
- ⚠️ **APIキーは機密情報です**
  - 他人と共有しないでください
  - 公開リポジトリにアップロードしないでください
- ⚠️ **`env.example`には実際の値を記載しないでください**
  - テンプレートとして使用するため、プレースホルダーのみを記載してください

## 参考リンク

- [Dify公式ドキュメント](https://docs.dify.ai)
- [Dify APIドキュメント](https://docs.dify.ai/use-dify/publish/developing-with-apis)
- [LINE Developers公式サイト](https://developers.line.biz/ja/)
- [LINE Messaging APIドキュメント](https://developers.line.biz/ja/docs/messaging-api/)
- [Python公式サイト](https://www.python.org/)
- [cloudflared公式サイト](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Render公式サイト](https://render.com)
- [Renderドキュメント](https://render.com/docs)

## ライセンス

このプロジェクトは学習目的で作成されています。
