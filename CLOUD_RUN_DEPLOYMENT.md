# Google Cloud Run 部署指南

完整的 LINE Bot 部署到 Google Cloud Run 的步驟指南。

---

## 📋 目錄

1. [前置準備](#前置準備)
2. [快速部署（使用自動化腳本）](#快速部署)
3. [手動部署步驟](#手動部署步驟)
4. [設定 LINE Webhook](#設定-line-webhook)
5. [驗證部署](#驗證部署)
6. [管理與監控](#管理與監控)
7. [疑難排解](#疑難排解)

---

## 前置準備

### ✅ 檢查清單

在開始之前，確保您已完成：

- [x] Google Cloud Project 已建立
- [x] Google Sheets API 已啟用
- [x] Google Drive API 已啟用
- [x] Service Account 已建立
- [x] Google Sheets 已分享給 Service Account
- [x] LINE Bot Channel 已建立
- [x] 已取得 LINE Channel Access Token
- [x] 已取得 LINE Channel Secret

### 🛠️ 必要工具

確保已安裝以下工具：

1. **Google Cloud SDK (gcloud CLI)**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk

   # Ubuntu/Debian
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL

   # 初始化
   gcloud init
   ```

2. **Docker**
   ```bash
   # macOS
   brew install --cask docker

   # Ubuntu/Debian
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

3. **驗證安裝**
   ```bash
   gcloud --version
   docker --version
   ```

---

## 快速部署

使用自動化部署腳本，一鍵完成所有步驟。

### 步驟 1: 設定環境變數

```bash
# 設定 GCP Project ID
export GCP_PROJECT_ID="your-project-id"

# (選用) 自訂服務名稱和區域
export CLOUD_RUN_SERVICE="linebot-lifelogger"
export CLOUD_RUN_REGION="asia-east1"
```

### 步驟 2: 建立生產環境變數檔案

```bash
# 複製範本
cp .env.production.example .env.production

# 編輯檔案，填入實際值
nano .env.production
```

填入以下內容：
```bash
SPREADSHEET_ID=你的試算表ID
LINE_CHANNEL_ACCESS_TOKEN=你的LINE_Access_Token
LINE_CHANNEL_SECRET=你的LINE_Channel_Secret
```

### 步驟 3: 啟用必要的 GCP API

```bash
gcloud services enable \
    run.googleapis.com \
    containerregistry.googleapis.com \
    cloudbuild.googleapis.com
```

### 步驟 4: 執行部署腳本

```bash
./deploy.sh
```

部署腳本會自動：
1. ✅ 檢查必要工具
2. ✅ 建置 Docker image
3. ✅ 推送到 Google Container Registry
4. ✅ 部署到 Cloud Run
5. ✅ 顯示服務 URL 和 Webhook URL

### 步驟 5: 記下 Webhook URL

部署完成後，您會看到：
```
========================================
部署完成！
========================================
服務名稱: linebot-lifelogger
區域: asia-east1
服務 URL: https://linebot-lifelogger-xxxxx-de.a.run.app

Webhook URL: https://linebot-lifelogger-xxxxx-de.a.run.app/webhook
```

**記下這個 Webhook URL**，下一步會用到。

---

## 手動部署步驟

如果您不想使用自動化腳本，可以手動執行以下步驟。

### 步驟 1: 設定 GCP 專案

```bash
# 設定專案 ID
gcloud config set project YOUR_PROJECT_ID

# 啟用必要 API
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 步驟 2: 建置 Docker Image

```bash
# 設定變數
PROJECT_ID=$(gcloud config get-value project)
IMAGE_NAME="gcr.io/${PROJECT_ID}/linebot-lifelogger"

# 建置 image
docker build -t ${IMAGE_NAME}:latest .
```

### 步驟 3: 推送到 Container Registry

```bash
# 配置 Docker 認證
gcloud auth configure-docker

# 推送 image
docker push ${IMAGE_NAME}:latest
```

### 步驟 4: 部署到 Cloud Run

```bash
gcloud run deploy linebot-lifelogger \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region asia-east1 \
    --allow-unauthenticated \
    --set-env-vars "SPREADSHEET_ID=你的試算表ID" \
    --set-env-vars "LINE_CHANNEL_ACCESS_TOKEN=你的Token" \
    --set-env-vars "LINE_CHANNEL_SECRET=你的Secret" \
    --max-instances 10 \
    --memory 512Mi \
    --timeout 300
```

**重要參數說明**：
- `--allow-unauthenticated`: 允許 LINE 平台訪問（必須）
- `--max-instances 10`: 最多 10 個實例（控制成本）
- `--memory 512Mi`: 512MB 記憶體（足夠使用）
- `--timeout 300`: 5 分鐘超時（圖片處理需要）

### 步驟 5: 取得服務 URL

```bash
gcloud run services describe linebot-lifelogger \
    --platform managed \
    --region asia-east1 \
    --format 'value(status.url)'
```

---

## 設定 LINE Webhook

### 步驟 1: 前往 LINE Developers Console

1. 訪問 https://developers.line.biz/console/
2. 選擇您的 Channel
3. 切換到 **Messaging API** 分頁

### 步驟 2: 設定 Webhook URL

1. 找到 **Webhook settings** 區域
2. 點擊 **Edit**
3. 輸入您的 Cloud Run Webhook URL：
   ```
   https://your-service-xxxxx-de.a.run.app/webhook
   ```
4. 點擊 **Update**

### 步驟 3: 啟用 Webhook

1. 在 **Webhook settings** 區域
2. 將 **Use webhook** 切換為 **Enabled**

### 步驟 4: 驗證 Webhook

1. 點擊 **Verify** 按鈕
2. 應該會顯示 **Success** ✅

如果驗證失敗，請檢查：
- URL 是否正確（包含 `/webhook` 路徑）
- Cloud Run 服務是否正在運行
- 是否設定為 `--allow-unauthenticated`

---

## 驗證部署

### 測試 1: 檢查服務狀態

```bash
curl https://your-service-xxxxx-de.a.run.app/
```

應該返回：
```
LINE Bot LifeLogger is running!
```

### 測試 2: 發送 LINE 訊息

1. 用手機 LINE 加入 Bot 為好友
2. 發送測試訊息：
   ```
   Hello Cloud Run!
   ```
3. Bot 應該回覆：
   ```
   ✅ 已記錄
   ```
4. 檢查 Google Sheets 確認訊息已記錄

### 測試 3: 查看日誌

```bash
gcloud run logs read linebot-lifelogger \
    --platform managed \
    --region asia-east1 \
    --limit 50
```

應該會看到：
```
收到 Webhook 請求
收到文字訊息
成功寫入訊息到 Google Sheets: 2025-11
已回覆確認訊息: ✅ 已記錄
```

---

## 管理與監控

### 查看服務資訊

```bash
gcloud run services describe linebot-lifelogger \
    --platform managed \
    --region asia-east1
```

### 查看即時日誌

```bash
gcloud run logs tail linebot-lifelogger \
    --platform managed \
    --region asia-east1
```

### 更新環境變數

```bash
gcloud run services update linebot-lifelogger \
    --platform managed \
    --region asia-east1 \
    --set-env-vars "NEW_VAR=value"
```

### 更新服務（重新部署）

如果修改了程式碼：

```bash
# 使用自動化腳本
./deploy.sh

# 或手動執行
docker build -t ${IMAGE_NAME}:latest .
docker push ${IMAGE_NAME}:latest
gcloud run deploy linebot-lifelogger --image ${IMAGE_NAME}:latest
```

### Cloud Console 監控

訪問 https://console.cloud.google.com/run

可以查看：
- 📊 請求數量和延遲
- 💰 成本估算
- 📝 日誌瀏覽
- 🔧 配置修改

---

## 疑難排解

### 問題 1: 部署失敗 - Permission Denied

**錯誤訊息**：
```
ERROR: (gcloud.run.deploy) PERMISSION_DENIED
```

**解決方法**：
```bash
# 確保已登入正確的帳號
gcloud auth login

# 確保專案 ID 正確
gcloud config set project YOUR_PROJECT_ID

# 確保有權限
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:your-email@gmail.com" \
    --role="roles/run.admin"
```

### 問題 2: Webhook 驗證失敗

**可能原因**：
1. URL 不正確
2. 服務未允許未經驗證的訪問
3. 環境變數未正確設定

**解決方法**：
```bash
# 1. 確認服務允許公開訪問
gcloud run services add-iam-policy-binding linebot-lifelogger \
    --region=asia-east1 \
    --member="allUsers" \
    --role="roles/run.invoker"

# 2. 測試首頁
curl https://your-service-url/

# 3. 查看日誌
gcloud run logs tail linebot-lifelogger --region=asia-east1
```

### 問題 3: Google Sheets 寫入失敗

**錯誤訊息**：
```
Permission denied
```

**解決方法**：

**方式 A: 使用 Service Account JSON（推薦用於測試）**

```bash
# 1. 將 service_account.json 轉換為 base64
base64 service_account.json > service_account_base64.txt

# 2. 部署時設定環境變數
gcloud run deploy linebot-lifelogger \
    --set-env-vars "GOOGLE_APPLICATION_CREDENTIALS_JSON=$(cat service_account_base64.txt)"

# 3. 修改 config.py 從環境變數讀取
```

**方式 B: 使用 Cloud Run Service Account（推薦用於生產）**

```bash
# 1. 建立專用的 Service Account
gcloud iam service-accounts create linebot-service-account

# 2. 授予 Sheets 和 Drive 權限
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:linebot-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/editor"

# 3. 部署時指定 Service Account
gcloud run deploy linebot-lifelogger \
    --service-account linebot-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com

# 4. 將 Google Sheets 分享給這個 Service Account
```

### 問題 4: 記憶體不足

**錯誤訊息**：
```
Memory limit exceeded
```

**解決方法**：
```bash
# 增加記憶體配置
gcloud run services update linebot-lifelogger \
    --memory 1Gi \
    --region asia-east1
```

### 問題 5: 冷啟動過慢

**現象**：首次請求很慢

**解決方法**：
```bash
# 設定最小實例數（會增加成本）
gcloud run services update linebot-lifelogger \
    --min-instances 1 \
    --region asia-east1
```

---

## 成本估算

### 免費額度（每月）

Cloud Run 免費額度：
- ✅ 2,000,000 次請求
- ✅ 360,000 GB-秒（運算時間）
- ✅ 180,000 vCPU-秒（CPU 時間）
- ✅ 1 GB 出站流量

### 實際使用估算

假設每天 100 條訊息：
- 每月請求：~3,000 次
- 每次處理時間：~2 秒
- 記憶體使用：512 MB
- **預估成本：$0/月（在免費額度內）**

即使每天 1,000 條訊息也在免費額度內！

---

## 下一步

部署成功後，您可以：

1. ✅ **監控運行狀況**
   - 查看 Cloud Console 的監控儀表板
   - 設定告警通知

2. ✅ **繼續開發 Phase 4**
   - 實作圖片訊息記錄功能
   - 測試後再次部署

3. ✅ **優化效能**
   - 調整記憶體和 CPU 配置
   - 設定自動擴展策略

4. ✅ **備份和復原**
   - 定期備份 Google Sheets
   - 設定錯誤通知

---

## 參考資源

- [Cloud Run 官方文檔](https://cloud.google.com/run/docs)
- [LINE Messaging API 文檔](https://developers.line.biz/en/docs/messaging-api/)
- [Google Sheets API 文檔](https://developers.google.com/sheets/api)

---

**祝部署順利！** 🚀

如有問題，請查看日誌或參考疑難排解章節。
