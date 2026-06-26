# LINE Bot

這是一個部署在 Render 的 LINE Bot 專案，保留必要 LINE webhook、抽圖、指定抽圖、銀河圖、LINE 圖片上傳、OpenAI 聊天與 GPT 圖像生成功能。

## 功能

- `銀河`：隨機回傳 `static/boyvfv/` 目錄中的圖片
- `抽`：隨機回傳 `static/roll/{1..134}_line.png`
- `rolltest <編號>`：回傳指定 `static/roll/<編號>_line.png`
- `上傳圖片`：開啟 1 分鐘上傳窗口，下一張圖片會存到 `static/line_uploads/`
- `@GG人 <內容>`：使用 Grok Responses API 回覆聊天內容
- `@GG人畫圖 <內容>`：使用 GPT Image 生成圖片，儲存在 `static/generated/` 後回傳圖片 URL
- `@GG人改圖 <指令>`：開啟 1 分鐘改圖窗口，下一張圖片會依指令修改，結果存到 `static/改圖/` 並同步 GitHub

## 環境變數

請在本機 `.env` 或 Render Environment 中設定：

| 名稱 | 用途 |
| --- | --- |
| `line_token` 或 `LINE_CHANNEL_ACCESS_TOKEN` | LINE channel access token |
| `line_secret` 或 `LINE_CHANNEL_SECRET` | LINE channel secret |
| `GROK_API_KEY` 或 `XAI_API_KEY` | Grok API key，用於 `@GG人` |
| `GROK_MODEL` | Grok 聊天模型，預設 `grok-4.3` |
| `GROK_WEB_SEARCH_ENABLED` | 是否啟用 Grok Web Search，預設 `true` |
| `OPENAI_API_KEY` 或 `chatgpt_api_key` | OpenAI API key |
| `OPENAI_IMAGE_MODEL` | 圖像模型，預設 `gpt-image-1` |
| `OPENAI_IMAGE_SIZE` | 圖像尺寸，預設 `1024x1024` |
| `OPENAI_IMAGE_QUALITY` | 圖像品質，預設 `auto` |
| `OPENAI_REASONING_EFFORT` | 聊天推理強度，預設 `low` |
| `OPENAI_TEXT_VERBOSITY` | 回覆詳細程度，預設 `medium` |
| `OPENAI_HISTORY_LIMIT` | 保留聊天歷史訊息數，預設 `20` |
| `GOOGLE_PROMPT_CACHE_SECONDS` | Google 文件提示詞快取秒數，預設 `300` |
| `GOOGLE_PROMPT_FETCH_TIMEOUT_SECONDS` | Google 文件提示詞讀取 timeout，預設 `10` |
| `LINE_IMAGE_UPLOAD_COMMAND` | 圖片上傳指令，預設 `上傳圖片` |
| `LINE_IMAGE_UPLOAD_WINDOW_SECONDS` | 圖片上傳等待秒數，預設 `60` |
| `GITHUB_TOKEN` | GitHub API token，用於圖片回寫 |
| `GITHUB_REPOSITORY` | GitHub repository，格式 `owner/repo` |
| `GITHUB_OWNER` / `GITHUB_REPO` | 可替代 `GITHUB_REPOSITORY` 的分開設定 |
| `GITHUB_BRANCH` | 回寫分支，預設 `main` |
| `GITHUB_API_BASE_URL` | GitHub API base URL，預設 `https://api.github.com` |
| `GITHUB_COMMITTER_NAME` / `GITHUB_COMMITTER_EMAIL` | 選填，指定 commit 作者 |

## 本機執行

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run
```

LINE webhook endpoint：

```text
https://<your-domain>/callback
```

健康檢查 endpoint：

```text
https://<your-domain>/index
```

## Render 部署

Build command：

```bash
./build.sh
```

Start command：

```bash
gunicorn -c gunicorn_config.py app:app
```

目前公開服務網址直接寫在 `app.py` 的 `APP_BASE_URL` 常數，讓 LINE 能正確讀取 `/static/...` 圖片。

Keep-alive 參數直接寫在 `app.py`，預設每 5 分鐘 GET 一次公開 `/callback`。`/callback` 的 GET 只回傳 `OK`，LINE webhook 的 POST 驗簽流程不受影響。

`@GG人` 的 system prompt 會從 Google 文件文字匯出讀取，預設快取 5 分鐘：

```text
https://docs.google.com/document/d/1eqIA-itJ7MvGSu0hF_8BAgnVqBq--81S9SMsHi5SLII/export?format=txt
```

`上傳圖片` 會先把圖片寫入目前執行環境的專案目錄 `static/line_uploads/`。若 `GITHUB_TOKEN` 與 repository 設定完整，Bot 會再透過 GitHub Contents API 將圖片 commit 回 GitHub。

`@GG人改圖 <指令>` 會等待同一聊天室 1 分鐘內的下一張圖片，使用 GPT Image 編輯圖片，將結果存到 `static/改圖/`，回覆改好的圖片，並在 GitHub 設定完整時 commit 回 GitHub。

GitHub token 權限建議：

- Fine-grained token：此 repository 的 `Contents` 設為 `Read and write`
- Classic token：需可寫入 repo 內容

## 測試

語法檢查：

```powershell
.\.venv\Scripts\python.exe -m compileall app.py ggopenai.py gunicorn_config.py
```

`.env` smoke test 會檢查 Flask route、LINE/OpenAI 環境變數是否載入、OpenAI 模組預設值與 `static/generated` 是否存在。測試時不要輸出 secret 值。

## 檔案說明

- `app.py`：Flask app、LINE webhook、LINE 指令處理
- `ggopenai.py`：OpenAI 聊天與圖像生成
- `github_api.py`：GitHub Contents API 圖片回寫
- `static/boyvfv/`：銀河圖片素材
- `static/roll/`：抽圖素材
- `static/line_uploads/`：LINE 指令上傳的圖片
- `static/改圖/`：GPT Image 改圖結果
- `static/generated/`：GPT 圖像生成結果，內容不提交 git
- `gunicorn_config.py`：Render/gunicorn 設定
- `requirements.txt`：部署依賴
