# Release Notes

## 2026-06-18

### 專案整理

- 精簡專案，只保留 LINE 必要功能、`銀河`、`抽`、`rolltest`、OpenAI API 相關指令與 Render 部署設定。
- 移除匯率、股票、YouTube、班表、Twitch 與其他未保留功能模組。
- 清理未使用 static 資源，保留 `static/roll/` 與 `static/boyvfv_is_dog.jpg`。
- 新增 `.gitignore`，忽略 `.env`、虛擬環境、快取、產生圖片與本機設定。

### LINE 圖片路徑

- `銀河`、`抽`、`rolltest` 改用部署服務的 `/static/...` 絕對 URL。
- 支援 `APP_BASE_URL`、`PUBLIC_BASE_URL`、`RENDER_EXTERNAL_URL`、`RENDER_EXTERNAL_HOSTNAME` 與 request host fallback。

### OpenAI 調整

- `@GG人` 改用 OpenAI Responses API 的 message list，不再將聊天歷史串成單一文字。
- 預設聊天模型改成 `gpt-5.5`，可透過 `OPENAI_CHAT_MODEL` 覆蓋。
- 系統提示改成繁體中文、自然、簡潔、友善，適合 LINE 群組聊天。
- OpenAI client 改成 lazy initialization，服務啟動不依賴 OpenAI key 立即存在。
- `@GG人畫圖` 改用 GPT Image，預設 `gpt-image-1`。
- 生成圖片會寫入 `static/generated/`，再用 static URL 回傳給 LINE。

### Render 與依賴

- 簡化 `requirements.txt`，保留 Flask、gunicorn、LINE SDK、OpenAI SDK、dotenv、requests。
- 簡化 `gunicorn_config.py`，用環境變數控制 workers、threads、timeout。
- 保留 `build.sh` 作為 Render build command。

### 測試紀錄

- 使用 `.env` 執行本機 smoke test。
- `/index` 回傳 `200` 與 `Hello World!!`。
- LINE token/secret、OpenAI key 均可由 `.env` 載入。
- 預設聊天模型確認為 `gpt-5.5`。
- 預設圖像模型確認為 `gpt-image-1`。
- `OPENAI_HISTORY_LIMIT` 預設確認為 `20`。
- `static/generated` 目錄存在。
- `ggopenai.openai_client()` 可成功初始化 OpenAI client。
- `_image_bytes()` 的 base64 圖片解析邏輯測試通過。
- `app.py`、`ggopenai.py`、`gunicorn_config.py` 語法編譯通過。
