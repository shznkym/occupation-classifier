# Kubernetes デプロイメントガイド

## 📚 概要

このガイドでは、occupation-classifierアプリケーションのKubernetesへのデプロイ・管理方法を説明します。

---

## 🗂️ ディレクトリ構成

```
k8s/
├── cleanup.sh              # 完全削除スクリプト
├── deploy.sh               # デプロイスクリプト
├── namespace.yaml          # Namespace定義
├── backend-deployment.yaml # Backendデプロイメント
├── backend-service.yaml    # BackendサービスなLoadBalancer）
├── frontend-deployment.yaml# Frontendデプロイメント
├── frontend-service.yaml   # FrontendサービスLoadBalancer）
└── ingress.yaml            # Ingress（オプション）
```

---

## 🚀 基本的な使い方

### 1️⃣ 初回デプロイ

```bash
cd /Users/snakayama/Documents/Development/other

# デプロイスクリプトを実行
./k8s/deploy.sh
```

**対話形式で進みます：**

```
========================================
Occupation Classifier - Kubernetes Deployment
========================================

Enter your Gemini API key: 
AIzaSyD_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  ← 入力

Deploying to Kubernetes...
✓ Namespace created/updated
✓ Secret created
✓ Backend deployment created
✓ Backend service created (LoadBalancer)
✓ Frontend deployment created
✓ Frontend service created (LoadBalancer)

Waiting for LoadBalancer IPs...
✓ Backend IP: 10.0.20.96
✓ Frontend IP: 10.0.20.95

========================================
Deployment completed successfully!
========================================

Access URLs:
  Frontend: http://10.0.20.95:3000
  Backend:  http://10.0.20.96:8000
  Health:   http://10.0.20.96:8000/api/health
```

### 2️⃣ 完全削除（クリーンアップ）

```bash
# すべてのリソースを削除
./k8s/cleanup.sh
```

**確認が求められます：**

```
========================================
Occupation Classifier - Cleanup
========================================

This will delete all resources in the 'occupation-classifier' namespace.
This action cannot be undone!

Are you sure you want to continue? (yes/no)
yes  ← "yes"と入力

Deleting resources in occupation-classifier namespace...
✓ Pods deleted
✓ Services deleted
✓ Deployments deleted
✓ Secrets deleted
✓ Namespace deleted

========================================
Cleanup completed successfully!
========================================
```

### 3️⃣ 再デプロイ

```bash
# cleanup後、再度デプロイ
./k8s/deploy.sh
```

---

## 📋 典型的なワークフロー

### パターン1: 完全なやり直し

```bash
# 1. 完全削除
./k8s/cleanup.sh
# → yes と入力

# 2. 再デプロイ
./k8s/deploy.sh
# → APIキーを入力

# 3. 動作確認
curl http://10.0.20.96:8000/api/health
```

### パターン2: コード更新後のデプロイ

```bash
# コード変更後

# 1. Git push（GitHub Actionsで自動ビルド）
git add .
git commit -m "update: ..."
git push origin main

# 2. 約90秒待つ（ビルド完了）
sleep 90

# 3. Podのみ再起動（イメージ更新）
kubectl delete pods -n occupation-classifier --all

# 4. 確認
kubectl get pods -n occupation-classifier
```

### パターン3: APIキーのみ変更

```bash
# APIキーだけ変更したい場合

# 1. Secretを更新
kubectl create secret generic gemini-secret \
  --from-literal=api-key='NEW_API_KEY' \
  --namespace=occupation-classifier \
  --dry-run=client -o yaml | kubectl apply -f -

# 2. Backend Podを再起動
kubectl delete pods -n occupation-classifier -l component=backend

# 3. 確認
kubectl get pods -n occupation-classifier
```

### パターン4: 設定変更（YAML編集）後

```bash
# YAMLファイル（deployment.yamlなど）を編集後

# 1. 適用
kubectl apply -f k8s/backend-deployment.yaml

# 2. ローリングアップデート確認
kubectl rollout status deployment/backend -n occupation-classifier

# 3. Pod状態確認
kubectl get pods -n occupation-classifier
```

---

## 🔍 よくある操作

### Podの状態確認

```bash
# 全Pod表示
kubectl get pods -n occupation-classifier

# 詳細情報
kubectl describe pod -n occupation-classifier <pod-name>

# ログ確認
kubectl logs -n occupation-classifier -l component=backend --tail=50

# リアルタイムログ
kubectl logs -n occupation-classifier -l component=backend -f
```

### サービスIP確認

```bash
# サービス一覧
kubectl get svc -n occupation-classifier

# LoadBalancer IPの取得
kubectl get svc -n occupation-classifier -o wide
```

### デプロイメント管理

```bash
# スケーリング（レプリカ数変更）
kubectl scale deployment/backend --replicas=3 -n occupation-classifier

# ローリングアップデート状態
kubectl rollout status deployment/backend -n occupation-classifier

# ロールバック
kubectl rollout undo deployment/backend -n occupation-classifier
```

### Podへの直接アクセス

```bash
# Podにシェル接続
kubectl exec -it deployment/backend -n occupation-classifier -- /bin/bash

# ファイル確認
kubectl exec -n occupation-classifier deployment/backend -- ls -la /app/data/

# Pythonスクリプト実行
kubectl exec -n occupation-classifier deployment/backend -- python3 -c "import numpy as np; print('OK')"
```

---

## 🛠️ トラブルシューティング

### Pod が起動しない

**症状:**
```bash
kubectl get pods -n occupation-classifier
NAME                      READY   STATUS             RESTARTS   AGE
backend-xxx-xxx           0/1     CrashLoopBackOff   5          5m
```

**確認:**
```bash
# ログでエラー確認
kubectl logs -n occupation-classifier <pod-name>

# Eventsを確認
kubectl describe pod -n occupation-classifier <pod-name> | tail -20
```

**よくある原因:**
- APIキーが無効
- イメージがpullできない
- リソース不足（メモリ・CPU）

**解決:**
```bash
# APIキー再設定
./k8s/cleanup.sh
./k8s/deploy.sh  # 正しいAPIキーを入力

# または
kubectl create secret generic gemini-secret \
  --from-literal=api-key='CORRECT_API_KEY' \
  -n occupation-classifier \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl delete pods -n occupation-classifier -l component=backend
```

### LoadBalancer IP が取得できない

**症状:**
```bash
kubectl get svc -n occupation-classifier
NAME       TYPE           EXTERNAL-IP   PORT(S)
backend    LoadBalancer   <pending>     8000:xxxxx/TCP
```

**原因:**
- クラスタがLoadBalancerをサポートしていない
- IPプールが枯渇

**解決:**
```bash
# NodePortに変更
kubectl edit svc backend -n occupation-classifier
# type: LoadBalancer → type: NodePort

# またはポートフォワーディングで一時的にアクセス
kubectl port-forward svc/backend 8000:8000 -n occupation-classifier
```

### イメージが古い

**症状:**
コード変更したのに反映されない

**解決:**
```bash
# 強制的に最新イメージを取得
kubectl delete pods -n occupation-classifier --all

# imagePullPolicyを確認
kubectl get deployment backend -n occupation-classifier -o yaml | grep imagePullPolicy
# → Always になっているか確認
```

### Embeddingキャッシュが作成されない

**症状:**
Pod起動後もキャッシュファイルがない

**確認:**
```bash
kubectl exec -n occupation-classifier deployment/backend -- ls -la /app/data/
```

**解決:**
```bash
# ログでエラー確認
kubectl logs -n occupation-classifier -l component=backend | grep -i "embedding\|error"

# Gemini APIクォータ確認
# → 24時間待つ、または新しいAPIキーを使用
```

---

## 📊 リソース設定

### 現在の設定値

**Backend:**
```yaml
resources:
  requests:
    cpu: 250m      # 0.25コア保証
    memory: 256Mi  # 256MB保証
  limits:
    cpu: 500m      # 0.5コア上限
    memory: 512Mi  # 512MB上限
```

**Frontend:**
```yaml
resources:
  requests:
    cpu: 100m      # 0.1コア保証
    memory: 128Mi  # 128MB保証
  limits:
    cpu: 200m      # 0.2コア上限
    memory: 256Mi  # 256MB上限
```

### リソース変更方法

```bash
# YAMLを編集
vi k8s/backend-deployment.yaml

# resources:
#   requests:
#     cpu: 500m      # ← 変更
#     memory: 512Mi  # ← 変更

# 適用
kubectl apply -f k8s/backend-deployment.yaml
```

---

## 🔐 セキュリティ設定

### Pod Security Standards

現在の設定は`restricted`ポリシーに準拠：

```yaml
securityContext:
  runAsNonRoot: true          # root以外で実行
  runAsUser: 1000             # UID 1000で実行
  allowPrivilegeEscalation: false  # 権限昇格禁止
  capabilities:
    drop: [ALL]               # 不要な権限削除
```

### Secret管理

```bash
# Secretの内容確認（Base64デコード）
kubectl get secret gemini-secret -n occupation-classifier -o jsonpath='{.data.api-key}' | base64 -d

# Secret削除
kubectl delete secret gemini-secret -n occupation-classifier

# Secret再作成
kubectl create secret generic gemini-secret \
  --from-literal=api-key='YOUR_API_KEY' \
  -n occupation-classifier
```

---

## 📈 モニタリング

### リソース使用状況

```bash
# Pod単位
kubectl top pods -n occupation-classifier

# Node単位
kubectl top nodes

# 詳細（metrics-server必要）
kubectl get pods -n occupation-classifier -o custom-columns=\
NAME:.metadata.name,\
CPU:.spec.containers[*].resources.requests.cpu,\
MEMORY:.spec.containers[*].resources.requests.memory
```

### ログ集約

```bash
# すべてのBackend Podのログ
kubectl logs -n occupation-classifier -l component=backend --all-containers=true

# 特定時間以降のログ
kubectl logs -n occupation-classifier -l component=backend --since=1h

# 前のPodのログ（クラッシュ時）
kubectl logs -n occupation-classifier <pod-name> --previous
```

---

## 🎯 ベストプラクティス

### 1. コード変更のデプロイフロー

```bash
# 1. ローカルテスト
cd backend
.venv/bin/python -m pytest  # テストがあれば

# 2. Git commit & push
git add .
git commit -m "feat: ..."
git push origin main

# 3. GitHub Actions完了待ち
gh run watch  # または sleep 90

# 4. Podのみ再起動（高速）
kubectl delete pods -n occupation-classifier -l component=backend

# 5. 動作確認
kubectl logs -n occupation-classifier -l component=backend --tail=50
curl http://10.0.20.96:8000/api/health
```

### 2. 定期的な確認

```bash
# 週1回程度
kubectl get all -n occupation-classifier
kubectl top pods -n occupation-classifier
kubectl get events -n occupation-classifier --sort-by='.lastTimestamp'
```

### 3. バックアップ

```bash
# 現在の設定をバックアップ
kubectl get all,secret,ingress -n occupation-classifier -o yaml > backup-$(date +%Y%m%d).yaml
```

---

## 🔄 完全なデプロイサイクル例

```bash
# === 開発サイクル ===

# 1. コード変更
vi backend/app/classifier.py

# 2. Git commit & push
git add backend/app/classifier.py
git commit -m "fix: improve classification accuracy"
git push origin main

# 3. GitHub Actions でビルド（自動）
# → 約90秒

# 4. Podを再起動（新しいイメージを取得）
kubectl delete pods -n occupation-classifier -l component=backend

# 5. 起動待機
kubectl wait --for=condition=ready pod -l component=backend \
  -n occupation-classifier --timeout=300s

# 6. ログ確認
kubectl logs -n occupation-classifier -l component=backend --tail=100

# 7. 動作テスト
curl -X POST http://10.0.20.96:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"user_input": "テスト入力"}'

# === 問題発生時 ===

# 完全リセット
./k8s/cleanup.sh
# → yes

# 再デプロイ
./k8s/deploy.sh
# → APIキー入力
```

---

## 📚 関連ドキュメント

- [システム全体ガイド](./system_guide.md)
- [classifier.py 詳細](./classifier_documentation.md)
- [README](../README.md)
- [ARCHITECTURE](../ARCHITECTURE.md)

---

## 💡 まとめ

| 操作 | コマンド | 説明 |
|------|---------|------|
| 初回デプロイ | `./k8s/deploy.sh` | すべてのリソースを作成 |
| 完全削除 | `./k8s/cleanup.sh` | すべて削除 |
| Pod再起動 | `kubectl delete pods -n occupation-classifier --all` | イメージ更新時 |
| ログ確認 | `kubectl logs -n occupation-classifier -l component=backend` | デバッグ |
| 状態確認 | `kubectl get all -n occupation-classifier` | 全体の状態 |
| APIキー変更 | Secret更新 + Pod再起動 | セキュリティ |

**基本パターン: cleanup.sh → deploy.sh で完全リセット！**
