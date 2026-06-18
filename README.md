# LINE Bot

這是一個部署在 Render 的 LINE Bot 專案，保留必要 LINE webhook、抽圖、指定抽圖、銀河圖、LINE 圖片上傳、OpenAI 聊天與 GPT 圖像生成功能。

## 功能

- `銀河`：隨機回傳 `static/boyvfv/` 目錄中的圖片
- `抽`：隨機回傳 `static/roll/{1..134}_line.png`
- `rolltest <編號>`：回傳指定 `static/roll/<編號>_line.png`
- `上傳圖片`：開啟 1 分鐘上傳窗口，下一張圖片會存到 `static/line_uploads/`
- `@GG人 <內容>`：使用 OpenAI Responses API 回覆聊天內容
- `@GG人畫圖 <內容>`：使用 GPT Image 生成圖片，儲存在 `static/generated/` 後回傳圖片 URL

## 環境變數

請在本機 `.env` 或 Render Environment 中設定：

| 名稱 | 用途 |
| --- | --- |
| `line_token` 或 `LINE_CHANNEL_ACCESS_TOKEN` | LINE channel access token |
| `line_secret` 或 `LINE_CHANNEL_SECRET` | LINE channel secret |
| `OPENAI_API_KEY` 或 `chatgpt_api_key` | OpenAI API key |
| `APP_BASE_URL` 或 `PUBLIC_BASE_URL` | 對外服務網址，建議設成 Render 網址 |
| `RENDER_EXTERNAL_URL` | Render 提供的對外服務網址 |
| `RENDER_EXTERNAL_HOSTNAME` | Render 提供的 hostname fallback |
| `OPENAI_CHAT_MODEL` | 聊天模型，預設 `gpt-5.5` |
| `OPENAI_IMAGE_MODEL` | 圖像模型，預設 `gpt-image-1` |
| `OPENAI_IMAGE_SIZE` | 圖像尺寸，預設 `1024x1024` |
| `OPENAI_IMAGE_QUALITY` | 圖像品質，預設 `auto` |
| `OPENAI_REASONING_EFFORT` | 聊天推理強度，預設 `low` |
| `OPENAI_TEXT_VERBOSITY` | 回覆詳細程度，預設 `medium` |
| `OPENAI_HISTORY_LIMIT` | 保留聊天歷史訊息數，預設 `20` |
| `OPENAI_SYSTEM_PROMPT` | 覆蓋預設系統提示 |
| `LINE_IMAGE_UPLOAD_COMMAND` | 圖片上傳指令，預設 `上傳圖片` |
| `LINE_IMAGE_UPLOAD_WINDOW_SECONDS` | 圖片上傳等待秒數，預設 `60` |

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

Render 上建議設定 `APP_BASE_URL` 或 `PUBLIC_BASE_URL` 為正式服務網址，讓 LINE 能正確讀取 `/static/...` 圖片。

`上傳圖片` 會把圖片寫入目前執行環境的專案目錄 `static/line_uploads/`。Render 的檔案系統不會自動回寫 GitHub；若要讓部署後上傳的圖片永久進入 GitHub，需要另外加入 GitHub API 或 git push 流程。

## 測試

語法檢查：

```powershell
.\.venv\Scripts\python.exe -m compileall app.py ggopenai.py gunicorn_config.py
```

`.env` smoke test 會檢查 Flask route、LINE/OpenAI 環境變數是否載入、OpenAI 模組預設值與 `static/generated` 是否存在。測試時不要輸出 secret 值。

## 檔案說明

- `app.py`：Flask app、LINE webhook、LINE 指令處理
- `ggopenai.py`：OpenAI 聊天與圖像生成
- `static/boyvfv/`：銀河圖片素材
- `static/roll/`：抽圖素材
- `static/line_uploads/`：LINE 指令上傳的圖片
- `static/generated/`：GPT 圖像生成結果，內容不提交 git
- `gunicorn_config.py`：Render/gunicorn 設定
- `requirements.txt`：部署依賴
