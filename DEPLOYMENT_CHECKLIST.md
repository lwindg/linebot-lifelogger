# Google Cloud Run 部署前檢查清單

在執行 `./deploy.sh` 之前，請按照此檢查清單完成所有前置設定。

---

## ✅ 第一步：Google Cloud 基礎設定

### 1. 檢查或建立 GCP 專案

**檢查現有專案**：
```bash
gcloud projects list
```

**建立新專案**（如果需要）：
```bash
# 建立專案（project-id 必須全域唯一，例如：linebot-lifelogger-123）
gcloud projects create YOUR-PROJECT-ID --name="LINE Bot LifeLogger"

# 設定為當前專案
gcloud config set project YOUR-PROJECT-ID
```

**記下您的 Project ID**：`____________________`

---

### 2. 啟用計費帳戶 ⚠️ **必須**

即使使用免費額度，也必須啟用計費。

**方法 A：透過 Web Console（推薦）**
1. 前往 https://console.cloud.google.com/billing
2. 建立計費帳戶（如果沒有）
3. 將計費帳戶連結到您的專案

**方法 B：檢查是否已啟用**
```bash
gcloud beta billing projects describe YOUR-PROJECT-ID
```

看到 `billingEnabled: true` 即可 ✅

---

### 3. 啟用必要的 API

```bash
# 設定專案
gcloud config set project YOUR-PROJECT-ID

# 啟用 Cloud Run 和相關 API
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

**驗證 API 已啟用**：
```bash
gcloud services list --enabled | grep -E "(run|registry|build)"
```

---

## ✅ 第二步：Google Sheets 認證設定

### 4. 設定 Service Account 認證

由於 Cloud Run 無法直接使用本地的 `service_account.json`，需要將認證資訊放入環境變數。

**執行認證設定腳本**：
```bash
./setup_credentials.sh
```

這個腳本會：
1. ✅ 讀取 `service_account.json`
2. ✅ 轉換為環境變數格式
3. ✅ 建立或更新 `.env.production`

**手動方式**（如果腳本無法使用）：
```bash
# 將 JSON 轉換為單行
cat service_account.json | tr -d '\n' | tr -d ' '

# 複製輸出，加入到 .env.production：
# GOOGLE_CREDENTIALS_JSON='複製的內容'
```

---

## ✅ 第三步：環境變數設定

### 5. 完成 .env.production 設定

編輯 `.env.production`，確保包含所有必要資訊：

```bash
# Google Sheets 認證（由 setup_credentials.sh 自動生成）
GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'

# Google Sheets 設定
SPREADSHEET_ID=你的試算表ID

# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN=你的LINE_Channel_Access_Token
LINE_CHANNEL_SECRET=你的LINE_Channel_Secret
```

**取得值的方式**：
- `SPREADSHEET_ID`: Google Sheets URL 中的 ID
  ```
  https://docs.google.com/spreadsheets/d/【這部分是ID】/edit
  ```
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Developers Console → Messaging API
- `LINE_CHANNEL_SECRET`: LINE Developers Console → Basic settings

---

## ✅ 第四步：本地測試

### 6. 測試環境變數設定

```bash
# 載入環境變數
export $(grep -v '^#' .env.production | xargs)

# 測試 Sheets 連線（使用環境變數）
python -c "
from src.services.sheets_client import get_sheets_client
client = get_sheets_client()
client.connect()
print('✅ 認證成功！')
"
```

如果成功，您應該看到：
```
從環境變數載入 Google 憑證
成功從環境變數載入憑證
✅ 認證成功！
```

---

## ✅ 第五步：設定部署環境變數

### 7. 設定 GCP Project ID

```bash
export GCP_PROJECT_ID="YOUR-PROJECT-ID"
```

或者修改 `deploy.sh` 中的預設值。

---

## 🎯 完整檢查清單

在執行部署前，確認以下項目：

- [ ] **GCP 專案已建立**
- [ ] **計費帳戶已啟用** ⚠️ 必須
- [ ] **Cloud Run API 已啟用**
- [ ] **Container Registry API 已啟用**
- [ ] **Cloud Build API 已啟用**
- [ ] **已執行 `./setup_credentials.sh`**
- [ ] **`.env.production` 包含所有必要變數**
- [ ] **本地測試認證成功**（步驟 6）
- [ ] **已設定 `GCP_PROJECT_ID` 環境變數**
- [ ] **gcloud CLI 已安裝並登入**
- [ ] **Docker 已安裝並運行**

---

## 🚀 準備部署

全部完成後，執行：

```bash
./deploy.sh
```

部署腳本會：
1. ✅ 檢查必要工具
2. ✅ 建置 Docker image
3. ✅ 推送到 Container Registry
4. ✅ 部署到 Cloud Run
5. ✅ 顯示 Webhook URL

---

## 💡 常見問題

### Q1: 如何確認計費已啟用？

```bash
gcloud beta billing projects describe YOUR-PROJECT-ID
```

### Q2: API 啟用失敗怎麼辦？

確保：
1. 計費帳戶已連結
2. 您有專案的 Owner 或 Editor 權限
3. 網路連線正常

### Q3: 認證設定失敗？

檢查：
1. `service_account.json` 是否存在
2. JSON 格式是否正確
3. Service Account 是否有效

### Q4: 我可以跳過本地測試嗎？

不建議。本地測試可以提早發現認證問題，避免部署後才發現錯誤。

---

## 📞 需要幫助？

如果遇到問題，請提供：
1. 執行的命令
2. 錯誤訊息
3. `gcloud version` 輸出

參考完整文檔：`CLOUD_RUN_DEPLOYMENT.md`
