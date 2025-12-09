# **Azure Static Web Apps + Vue(Vite) + Python Functions クイックスタート（2025年版）**

## 0. 前提

- Node.js: **20.19 以上**推奨
  ※Vite 7 は Node 20+ を要求するため（Node 18 では Actions が失敗した）
- Python: 3.10 前後（Functions 用）
- GitHub アカウント（リポジトリ作成権限）
- Azure アカウント（既存リソースグループに SWA を作れる権限）
- VS Code + 必須拡張機能
  - Azure Static Web Apps
  - Azure Functions
  - Python

---

## 1. Vue + Vite フロントエンドを作る

```bash
# 作業ディレクトリへ
cd C:\Users\3783\Documents\VScodeFile

# Vite で Vue プロジェクト作成
npm create vite@latest my-app -- --template vue

cd my-app
npm install

# 動作確認
npm run dev
```

ブラウザで `http://localhost:5173` を開いて、Vite の初期画面が出ればOK。

> この `my-app` が Static Web Apps の「フロントエンド」。

---

## ★（重要）SWA の GitHub Actions で Node 18 が使われ失敗する問題への対処

SWA のビルド基盤（Oryx）は標準で **Node 18** を選択する。
しかし **Vite 7 は Node 20+ 必須** のため、Actions でビルドが落ちる。

そこで `package.json` のトップに以下を追加：

```jsonc
"engines": {
  "node": ">=20.19.0"
}
```

これにより GitHub Actions が Node 20 を使うようになり、ビルドが通る。

---

## 2. Python Azure Functions API を追加

### 2-1. Functions プロジェクト作成

```bash
cd my-app

# apiフォルダにPython Functionsを作成
func init api --python

cd api
func new --template "HTTP trigger" --name hello
```

※ここで生成されるのは旧形式の `hello/__init__.py` ではなく、
**Python Functions v2 Programming Model（新形式）** の `function_app.py` に追記される形。
→ これは「正しい」仕様。

### 2-2. ローカルで API をテスト

```bash
cd api
func start
```

`http://localhost:7071/api/hello` が動けばOK。

---

## 3. Vue から API を呼ぶ最小サンプル

`src/App.vue`：

```vue
<script setup>
import { ref, onMounted } from 'vue'

const message = ref('loading...')

onMounted(async () => {
  const res = await fetch('/api/hello')
  const text = await res.text()   // ← JSON ではなく text()（テンプレの戻り値は文字列）
  message.value = text
})
</script>

<template>
  <h1>Static Web Apps + Vue + Functions</h1>
  <p>API says: {{ message }}</p>
</template>
```

---

### ★ 補足：戻り値が JSON の場合はこう変える

Python を JSON 返す形にしたら：

```python
return func.HttpResponse(
    json.dumps({"message": "Hello!"}),
    mimetype="application/json"
)
```

Vue 側：

```vue
const data = await res.json()
message.value = data.message
```

---

## 4. GitHub に push → Static Web Apps を作成

### 4-1. GitHub リポジトリを作成して push

```bash
cd my-app
git init
git add .
git commit -m "init: vue + vite + functions"
git branch -M main
git remote add origin <GitHubリポジトリURL>
git push -u origin main
```

### 4-2. Azure Portal で SWA 作成

- App location: `/`
- Api location: `api`
- Output location: `dist`

SWA が GitHub Actions を自動作成し、

- npm install
- vite build
- dist のデプロイ
- api のデプロイ

を全部やってくれる。

---

## 5. アプリケーション設定（環境変数）

### 5-1. ローカル設定（Functions 側）

`api/local.settings.json`：

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "MY_API_KEY": "local-secret-value"
  }
}
```

### 5-2. 本番設定（SWA 側）

Azure Portal → SWA → 「構成」
`MY_API_KEY` を設定。

Functions からは：

```python
os.environ.get("MY_API_KEY")
```

で取れる。

---

## 6. まとめ（2025年版クイックスタートのポイント）

1. Vue CLI ではなく **Vite + Vue 3** を必ず使う
2. Functions は新形式の **function_app.py モデル**
3. SWA デプロイ失敗の最重要ポイント：
   → **GitHub Actions の Node が 18 のため、Vite 7 と衝突する**
4. 対策：
   → `package.json` に `engines.node: ">=20.19.0"` を追加
5. SWA では Functions App リソースは作られない
   → **Managed Functions** として SWA 内部で動作