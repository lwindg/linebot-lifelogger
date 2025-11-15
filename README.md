# LINE Bot LifeLogger

LINE 訊息記錄器 - 自動將 LINE 訊息（文字和圖片）記錄到 Google Sheets

## 功能特色

- ✅ 記錄 LINE 文字訊息到 Google Sheets
- ✅ 記錄 LINE 圖片訊息（內嵌到 Google Sheets）
- ✅ 自動建立月份子表單（YYYY-MM 格式）
- ✅ 週分界標記（週日為起始日）
- ✅ 所有時間使用台灣時區（UTC+8）
- ✅ 錯誤日誌記錄

## 技術堆疊

- **Python**: 3.11+
- **Web 框架**: Flask 3.0
- **LINE API**: line-bot-sdk 3.5
- **Google API**: gspread 5.12, google-api-python-client 2.110
- **圖片處理**: Pillow 10.1
- **時區處理**: pytz 2023.3
- **測試**: pytest 7.4

## 環境準備

### 1. Google Sheets 設定

詳細步驟請參考：[Google Sheets 串接準備指南](./specs/001-line-message-logger/google-sheets-setup.md)

**快速檢查清單**:
- [ ] Google Cloud 專案已建立
- [ ] Google Sheets API 已啟用
- [ ] Google Drive API 已啟用
- [ ] Service Account 已建立並下載 JSON 金鑰
- [ ] Google Sheets 試算表已建立並分享給 Service Account
- [ ] Google Drive 資料夾已建立並分享給 Service Account

### 2. LINE Bot 設定

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立新的 Messaging API Channel
3. 取得 Channel Access Token 和 Channel Secret

### 3. 安裝依賴

```bash
# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴套件
pip install -r requirements.txt
```

### 4. 環境變數設定

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 填入實際的憑證和 ID
nano .env
```

**必要的環境變數**:
```bash
GOOGLE_CREDENTIALS_FILE=service_account.json
SPREADSHEET_ID=你的試算表ID
DRIVE_FOLDER_ID=你的Drive資料夾ID
LINE_CHANNEL_ACCESS_TOKEN=你的LINE_Token
LINE_CHANNEL_SECRET=你的LINE_Secret
```

### 5. 放置 Service Account 金鑰

將下載的 Google Service Account JSON 金鑰檔案重新命名為 `service_account.json`，並放在專案根目錄。

**⚠️ 重要**: 此檔案已在 `.gitignore` 中，不會被提交到 Git。

## 專案結構

```
linebot-lifelogger/
├── src/
│   ├── webhook/          # LINE Webhook 處理
│   ├── services/         # 業務邏輯服務
│   ├── models/           # 資料模型
│   └── config.py         # 配置管理
├── tests/
│   ├── integration/      # 整合測試
│   ├── contract/         # 契約測試
│   └── unit/             # 單元測試
├── specs/
│   └── 001-line-message-logger/
│       ├── spec.md           # 功能規格
│       ├── plan.md           # 技術規劃
│       ├── research.md       # 技術研究
│       ├── data-model.md     # 資料模型
│       ├── tasks.md          # 任務清單
│       └── google-sheets-setup.md  # Google Sheets 設定指南
├── requirements.txt      # Python 依賴
├── .env.example          # 環境變數範本
├── .gitignore
└── README.md
```

## 本地開發

### 啟動開發伺服器

```bash
# 啟動 Flask 應用
python src/webhook/app.py
```

### 執行測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/integration/

# 執行測試並顯示覆蓋率
pytest --cov=src tests/
```

## 部署

### Docker 部署（推薦）

```bash
# 建立 Docker 映像
docker build -t linebot-lifelogger .

# 執行容器
docker run -d \
  --name linebot-lifelogger \
  --env-file .env \
  -p 5000:5000 \
  linebot-lifelogger
```

### 使用 docker-compose

```bash
docker-compose up -d
```

## LINE Webhook 設定

1. 使用 ngrok 或類似工具將本地伺服器暴露到公網：
   ```bash
   ngrok http 5000
   ```

2. 在 LINE Developers Console 設定 Webhook URL：
   ```
   https://your-ngrok-url.ngrok.io/webhook
   ```

3. 啟用 Webhook

## 使用方式

1. 將 LINE Bot 加入好友
2. 傳送文字訊息或圖片
3. 系統自動記錄到 Google Sheets
4. 查看 Google Sheets 確認記錄

## Google Sheets 結構

系統會自動建立以下結構：

```
LINE Bot LifeLogger (試算表)
├── 2025-11 (子表單)
│   ├── 時間 | 類型 | 內容
│   ├── --- 第 46 週 ---
│   ├── 2025-11-15 08:30:00 | 文字 | 早安
│   ├── 2025-11-15 09:00:00 | 圖片 | [圖片]
│   └── ...
└── 2025-12 (子表單)
    └── ...
```

## 開發進度

詳細開發任務請參考：[tasks.md](./specs/001-line-message-logger/tasks.md)

- [x] Phase 1: Setup（專案初始化）
- [ ] Phase 2: Foundational（核心基礎設施）
- [ ] Phase 3: User Story 1 - 文字訊息記錄（P1 MVP）
- [ ] Phase 4: User Story 2 - 圖片訊息記錄（P1 MVP）
- [ ] Phase 5: User Story 3 - 月份子表單（P2）
- [ ] Phase 6: User Story 4 - 週分界標記（P2）
- [ ] Phase 7: User Story 5 - Bot 回應確認（P3）
- [ ] Phase 8: Polish & Cross-Cutting Concerns

## 授權

MIT License

## 作者

LINE Bot LifeLogger Development Team

---

**版本**: 0.1.0 (開發中)
**最後更新**: 2025-11-15
