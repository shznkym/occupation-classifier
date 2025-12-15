# 職業分類判定システム (RAG構成)

自由記述から適切な職業分類コードを判定するWebサービスです。OpenAI Embeddings と GPT-4o を使用したRAG (Retrieval-Augmented Generation) 構成で高精度な判定を実現します。

## 🌟 特徴

- **RAG構成**: Google Gemini Embeddings (text-embedding-004) による類似検索 + Gemini 2.0 による最終判定
- **Web UI**: Next.js による美しく使いやすいインターフェース
- **REST API**: FastAPI による高速なバックエンド API
- **Docker対応**: GitHub Actionsで自動ビルドされたイメージで簡単デプロイ

## 🏗️ アーキテクチャ

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Frontend   │─────▶│   Backend    │─────▶│   OpenAI    │
│  (Next.js)  │      │  (FastAPI)   │      │     API     │
│   Port:3000 │      │   Port:8000  │      └─────────────┘
└─────────────┘      └──────────────┘
```

## 📦 Docker イメージ

GitHub Actionsにより自動的にビルドされたDockerイメージがGitHub Container Registry (ghcr.io) で公開されています。

### イメージの取得

```bash
# バックエンドイメージ
docker pull ghcr.io/[YOUR_USERNAME]/[YOUR_REPO]/backend:latest

# フロントエンドイメージ
docker pull ghcr.io/[YOUR_USERNAME]/[YOUR_REPO]/frontend:latest
```

> **Note**: プライベートリポジトリの場合、以下のコマンドで認証が必要です:
> ```bash
> echo $GITHUB_TOKEN | docker login ghcr.io -u [YOUR_USERNAME] --password-stdin
> ```

### Docker Compose での実行

プロジェクトルートに `docker-compose.yml` を作成:

```yaml
version: '3.8'

services:
  backend:
    image: ghcr.io/[YOUR_USERNAME]/[YOUR_REPO]/backend:latest
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped

  frontend:
    image: ghcr.io/[YOUR_USERNAME]/[YOUR_REPO]/frontend:latest
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped
```

環境変数を設定して起動:

```bash
# .env ファイルを作成
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# 起動
docker-compose up -d

# ログ確認
docker-compose logs -f

# 停止
docker-compose down
```

### 個別のコンテナ実行

```bash
# バックエンド
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  --name occupation-backend \
  ghcr.io/[YOUR_USERNAME]/[YOUR_REPO]/backend:latest

# フロントエンド
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_BACKEND_URL=http://localhost:8000 \
  --name occupation-frontend \
  ghcr.io/[YOUR_USERNAME]/[YOUR_REPO]/frontend:latest
```

## ☸️ Kubernetes デプロイ

Kubernetes環境でアプリケーションをデプロイする方法です。

### 必要要件

- Kubernetes クラスタ (v1.19+)
- kubectl CLI
- Google Gemini API Key

### 自動デプロイ (推奨)

デプロイスクリプトを使用して簡単にデプロイできます:

```bash
cd k8s
./deploy.sh
```

スクリプトが以下を自動的に実行します:
1. Gemini API Key の入力プロンプト
2. Namespace の作成
3. Secret の作成
4. Backend と Frontend のデプロイ
5. Service の作成
6. (オプション) Ingress の作成

### 手動デプロイ

#### 1. Namespace の作成

```bash
kubectl apply -f k8s/namespace.yaml
```

#### 2. Secret の作成

Gemini API Key を base64 エンコードして Secret を作成:

```bash
# API Key のエンコード
echo -n "your_gemini_api_key_here" | base64

# Secret の作成 (エンコードした値を使用)
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: gemini-secret
  namespace: occupation-classifier
type: Opaque
data:
  api-key: <BASE64_ENCODED_GEMINI_API_KEY>
EOF
```

#### 3. アプリケーションのデプロイ

```bash
# Backend のデプロイ
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

# Frontend のデプロイ
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# (オプション) Ingress のデプロイ
kubectl apply -f k8s/ingress.yaml
```

#### 4. デプロイ状態の確認

```bash
# Pod の確認
kubectl get pods -n occupation-classifier

# Service の確認
kubectl get svc -n occupation-classifier

# 詳細な状態確認
kubectl describe pods -n occupation-classifier
```

### アクセス方法

#### Port-forward を使用

```bash
# Frontend にアクセス (推奨)
kubectl port-forward -n occupation-classifier svc/frontend-service 3000:3000

# Backend API にアクセス
kubectl port-forward -n occupation-classifier svc/backend-service 8000:8000
```

その後、ブラウザで以下にアクセス:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

#### Ingress を使用

Ingress を設定した場合、設定したホスト名でアクセス可能です。

### ログの確認

```bash
# Backend のログ
kubectl logs -n occupation-classifier -l component=backend -f

# Frontend のログ
kubectl logs -n occupation-classifier -l component=frontend -f

# 特定の Pod のログ
kubectl logs -n occupation-classifier <pod-name> -f
```

### クリーンアップ

すべてのリソースを削除する場合:

```bash
cd k8s
./cleanup.sh
```

または手動で:

```bash
kubectl delete namespace occupation-classifier
```

### リソース設定

デフォルトのリソース設定:

| コンポーネント | CPU Request | CPU Limit | Memory Request | Memory Limit | レプリカ数 |
|--------------|-------------|-----------|----------------|--------------|-----------|
| Backend      | 250m        | 500m      | 256Mi          | 512Mi        | 2         |
| Frontend     | 100m        | 200m      | 128Mi          | 256Mi        | 2         |

必要に応じて `k8s/*-deployment.yaml` で調整できます。

## 🚀 ローカル開発

### 必要要件

- Python 3.11+
- Node.js 20+
- OpenAI API Key

### バックエンド (FastAPI)

```bash
cd backend

# 仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp ../.env.example .env
# .env ファイルに OPENAI_API_KEY を設定

# 開発サーバーの起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

APIドキュメント: http://localhost:8000/docs

### フロントエンド (Next.js)

```bash
cd frontend

# 依存関係のインストール
npm install

# 環境変数の設定 (オプション)
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local

# 開発サーバーの起動
npm run dev
```

アプリケーション: http://localhost:3000

### スタンドアロン版

```bash
# プロジェクトルートで実行
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .env ファイルに OPENAI_API_KEY を設定

# テストケースの実行
python main.py
```

## 🔧 環境変数

### バックエンド

| 変数名 | 説明 | 必須 | デフォルト |
|--------|------|------|-----------|
| `GEMINI_API_KEY` | Google Gemini API キー | ✅ | - |

### フロントエンド

| 変数名 | 説明 | 必須 | デフォルト |
|--------|------|------|-----------|
| `NEXT_PUBLIC_BACKEND_URL` | バックエンドAPI URL | ❌ | `http://localhost:8000` |

## 📚 API エンドポイント

### `POST /api/classify`

職業分類を判定します。

**リクエスト:**
```json
{
  "user_input": "消防車に乗って火を消す仕事"
}
```

**レスポンス:**
```json
{
  "code": "32",
  "name": "保安職業従事者",
  "reason": "火災の消火活動を行う消防士に該当するため",
  "candidates": [
    {
      "code": "32",
      "name": "保安職業従事者",
      "description": "自衛官、警察官、消防隊員...",
      "similarity": 0.8523
    }
  ],
  "user_input": "消防車に乗って火を消す仕事"
}
```

### `GET /api/health`

ヘルスチェック。

**レスポンス:**
```json
{
  "status": "healthy",
  "message": "職業分類データ 16 件をロード済み"
}
```

## 🔄 GitHub Actions

このプロジェクトは GitHub Actions を使用してDockerイメージを自動ビルドします。

### ワークフロートリガー

- `main` ブランチへのプッシュ → `latest` タグでビルド
- `v*.*.*` タグのプッシュ → バージョンタグでビルド
- Pull Request → ビルドのみ (プッシュなし)
- 手動実行 → Actions タブから実行可能

### イメージタグ戦略

| タグ | 説明 | 例 |
|------|------|-----|
| `latest` | mainブランチの最新ビルド | `backend:latest` |
| `main-<sha>` | コミットSHA | `backend:main-abc1234` |
| `v*.*.*` | セマンティックバージョン | `backend:v1.0.0` |

### 必要な設定

リポジトリの **Settings > Actions > General** で以下を設定:
- ✅ **Workflow permissions**: "Read and write permissions"

## 📝 使用例

### Web UIから

1. ブラウザで http://localhost:3000 を開く
2. テキストボックスに職業の説明を入力 (例: "消防車に乗って火を消す仕事")
3. 「職業分類を判定する」ボタンをクリック
4. 判定結果と類似候補が表示されます

### APIから (curl)

```bash
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"user_input": "エクセルの集計業務"}'
```

### APIから (Python)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/classify",
    json={"user_input": "プログラミングでWebアプリを作っています"}
)

result = response.json()
print(f"[{result['code']}] {result['name']}")
print(f"理由: {result['reason']}")
```

## 🛠️ 技術スタック

- **Backend**: FastAPI, Python 3.11, Google Gemini API, scikit-learn, pandas
- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS
- **AI**: Google Gemini Embeddings (text-embedding-004), Gemini 2.0 Flash
- **Infrastructure**: Docker, GitHub Actions, GitHub Container Registry, Kubernetes

## 📄 ライセンス

このプロジェクトは自由に使用できます。

## 🤝 コントリビューション

Issue や Pull Request を歓迎します！

---

**Powered by Google Gemini API**
