いいテーマなので、いったん「実務でそのまま使える最小クイックスタート」として組み立ててみるね。
流れは公式の 3 ページとほぼ同じ構造にしてあるけど、中身は **Vue + Vite + Functions(Python)** 前提に差し替えています。

---

## 0. 前提

* Node.js: 18 以上（あなたは 20 なのでOK）
* Python: 3.10 前後推奨（Functions 用）
* GitHub アカウント（リポジトリ作成権限）
* Azure アカウント（既存リソースグループに SWA を作れる権限）
* VS Code + 以下の拡張機能

  * Azure Static Web Apps
  * Azure Functions
  * Python 拡張

---

## 1. Vue + Vite フロントエンドを作る（旧クイックスタート1本目に対応）

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

> この `my-app` がそのまま Static Web Apps の「フロントエンド」になります。

---

## 2. Python Azure Functions API を追加（旧「add API」ページに対応）

### 2-1. Functions プロジェクト作成

```bash
cd my-app

# apiフォルダにPython Functionsを作成
func init api --python

cd api
func new --template "HTTP trigger" --name hello
```

これで `function_app.py` に `hello` 関数が作成される。

### 2-2. ローカルで API をテスト

```bash
cd api
func start
```

ログに `http://localhost:7071/api/hello` が出るので、ブラウザや curl で叩いてレスポンスが返るか確認。

> これが Static Web Apps にデプロイされたときは `/api/hello` というパスになるイメージ。

---

## 3. Vue から API を呼ぶ簡単サンプル

`my-app/src/App.vue` を最小限こんな感じに書き換えるイメージ：

```vue
<script setup>
import { ref, onMounted } from 'vue'

const message = ref('loading...')

onMounted(async () => {
  const res = await fetch('/api/hello')
  const data = await res.json()
  message.value = data  // 実際の戻り値形に合わせて調整(※１)
})
</script>

<template>
  <h1>Static Web Apps + Vue + Functions</h1>
  <p>API says: {{ message }}</p>
</template>
```

### ※１の調整方法
今のままだと **フロントの書き方と、Python 関数の戻り値の形式がズレている** 可能性が高い。
今の Python のテンプレは「文字列を返している」はず

`function_app.py` がテンプレのままだと、だいたいこうなってるはず：

```python
import azure.functions as func

app = func.FunctionApp()

@app.function_name(name="hello")
@app.route(route="hello", auth_level=func.AuthLevel.ANONYMOUS)
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        "This HTTP triggered function executed successfully.",
        status_code=200
    )
```

つまり、**返ってくるのは JSON じゃなくて「ただの文字列」**。

この場合、フロント側はこう書くべき：

```vue
onMounted(async () => {
  const res = await fetch('/api/hello')
  const text = await res.text()   // ← json() じゃなくて text()
  message.value = text
})
```


ローカルで SPA と Functions を一緒に動かしたい場合は、
後で SWA CLI を使うと「本番と同じ /api 経由」の挙動が再現しやすいです（今回は簡略化）。

---

## 4. GitHub に push → Static Web Apps を作成（旧クイックスタートの本体）

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

### 4-2. Azure Portal から Static Web Apps 作成

1. 「Static Web Apps」→「作成」
2. GitHub を接続し、先ほどのリポジトリとブランチ `main` を選択
3. フレームワーク設定：

   * **App location:** `/`
   * **Api location:** `api`
   * **Output location:** `dist`
4. 既存のリソースグループを選ぶ（新規作成はしない）

作成すると GitHub Actions ワークフロー（yml）が自動生成され、
`npm install` → `npm run build` → `dist` デプロイ → `api` デプロイまでやってくれます。

---

## 5. アプリケーション設定（環境変数）の扱い（旧3本目に対応）

### 5-1. ローカル（Functions 側）

`my-app/api/local.settings.json` を編集：

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

Python Functions からは：

```python
import os

def main(req):
    key = os.environ.get("MY_API_KEY")
    ...
```

### 5-2. 本番（Static Web Apps 側）

* Azure Portal → 対象 Static Web Apps → 「構成」または「アプリケーション設定」
* `MY_API_KEY` を追加

Functions 側からは、ローカルと同じ `os.environ.get("MY_API_KEY")` で取れます。

> ポイント：**シークレット（APIキーや接続文字列）はコードに直書きせず、
> local.settings.json（ローカル）と Azure のアプリ設定（本番）に逃がす。**

---

## ざっくり流れのまとめ

1. `npm create vite@latest` で Vue+Vite プロジェクト作成
2. `api/` に Python Functions を `func init` / `func new` で追加
3. Vue から `/api/hello` を fetch して疎通確認
4. GitHub に push → Azure Portal から Static Web Apps 作成

   * App location `/` / Api location `api` / Output `dist`
5. local.settings.json + Azure 構成で環境変数を管理

これで、元の公式 3 ページの流れを **2025 年の現実に合わせて焼き直したクイックスタート**になっています。

ここから先は、このひな形に「社内業務の要件」を一つずつ載せていく感じで育てていくといい。
