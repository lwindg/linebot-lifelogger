# LINE Bot 實際部署測試指南

本指南說明如何將 LINE Bot 部署到可接收真實訊息的環境進行測試。

---

## 📋 前置準備檢查

在開始之前，確認以下項目已完成：

- [x] ✅ Google Sheets 已設定並測試成功
- [x] ✅ `service_account.json` 已放置在專案根目錄
- [x] ✅ `.env` 檔案已建立並設定
- [ ] ⚠️  LINE Bot Channel 已建立
- [ ] ⚠️  已取得 LINE Channel Access Token
- [ ] ⚠️  已取得 LINE Channel Secret
- [ ] ⚠️  已安裝 ngrok

---

## 🔧 步驟 1: 準備 LINE Bot 憑證

### 1.1 建立 LINE Bot Channel（如果尚未建立）

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 登入您的 LINE 帳號
3. 建立 Provider（如果還沒有）
4. 建立新的 Messaging API Channel：
   - Channel type: **Messaging API**
   - Channel name: `LifeLogger Bot`（或任意名稱）
   - Channel description: 記錄訊息到 Google Sheets
   - Category: 選擇適當分類
   - Subcategory: 選擇適當子分類

### 1.2 取得 Channel Access Token

1. 進入您的 Channel 設定頁面
2. 切換到 **Messaging API** 分頁
3. 在 **Channel access token** 區域：
   - 點擊 **Issue** 按鈕產生 token
   - 複製產生的 token（很長的字串）

### 1.3 取得 Channel Secret

1. 在 Channel 設定頁面
2. 切換到 **Basic settings** 分頁
3. 找到 **Channel secret**
4. 複製 Channel Secret

### 1.4 更新 .env 檔案

編輯 `.env` 檔案，更新以下兩行：

```bash
LINE_CHANNEL_ACCESS_TOKEN=你的_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_Channel_Secret
```

---

## 🌐 步驟 2: 安裝並設定 ngrok

### 2.1 安裝 ngrok

**macOS (Homebrew)**:
```bash
brew install ngrok
```

**Ubuntu/Debian**:
```bash
# 下載 ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update && sudo apt install ngrok
```

**手動下載**:
1. 前往 https://ngrok.com/download
2. 下載對應您系統的版本
3. 解壓縮到 PATH 目錄

### 2.2 註冊 ngrok 帳號（建議）

1. 前往 https://dashboard.ngrok.com/signup
2. 註冊免費帳號
3. 取得 authtoken
4. 設定 authtoken：
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

---

## 🚀 步驟 3: 啟動 Webhook Server

### 3.1 開啟第一個終端機：啟動 Flask Server

```bash
# 確保在專案根目錄
cd /home/user/linebot-lifelogger

# 啟動 webhook server
python start_webhook.py
```

您應該會看到：
```
🚀 啟動 LINE Bot Webhook Server
🔍 檢查環境設定
✅ 環境變數檢查通過
✅ Google Sheets 連線成功
🌐 啟動 Flask Server
Server 將在以下位址運行：
  - Local:   http://127.0.0.1:5000
  - Webhook: http://127.0.0.1:5000/webhook
```

**保持這個終端機運行，不要關閉！**

### 3.2 開啟第二個終端機：啟動 ngrok

```bash
ngrok http 5000
```

您會看到類似以下輸出：
```
ngrok

Session Status                online
Account                       your@email.com (Plan: Free)
Version                       3.x.x
Region                        Asia Pacific (ap)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**重要**：複製 **Forwarding** 的 HTTPS URL（例如：`https://abc123.ngrok-free.app`）

**保持這個終端機運行，不要關閉！**

---

## 🔗 步驟 4: 設定 LINE Webhook URL

### 4.1 設定 Webhook URL

1. 回到 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇您的 Channel
3. 切換到 **Messaging API** 分頁
4. 找到 **Webhook settings**
5. 點擊 **Edit** 編輯 Webhook URL
6. 輸入您的 ngrok URL + `/webhook`：
   ```
   https://abc123.ngrok-free.app/webhook
   ```
   （記得加上 `/webhook` 路徑！）
7. 點擊 **Update** 儲存

### 4.2 啟用 Webhook

1. 在同一頁面，找到 **Use webhook** 開關
2. 將開關切換到 **Enabled**（啟用）

### 4.3 測試 Webhook 連線

1. 在 **Webhook URL** 欄位旁邊，點擊 **Verify** 按鈕
2. 如果設定正確，應該會顯示 **Success**
3. 同時檢查 Flask server 終端機，應該會看到收到 webhook 請求的日誌

### 4.4 關閉自動回覆訊息（重要）

1. 切換到 **Messaging API** 分頁
2. 找到 **Auto-reply messages**
3. 點擊 **Edit** 進入 LINE Official Account Manager
4. 關閉自動回覆功能（避免與我們的 bot 衝突）

---

## 📱 步驟 5: 加入 Bot 好友並測試

### 5.1 加入 Bot 為好友

1. 在 LINE Developers Console 的 **Messaging API** 分頁
2. 找到 **Bot basic ID** 或 **QR code**
3. 使用手機 LINE 掃描 QR code，或搜尋 Bot ID
4. 加入 Bot 為好友

### 5.2 發送測試訊息

在 LINE 對話視窗中，發送以下測試訊息：

1. **測試 1：基本文字訊息**
   ```
   Hello, LifeLogger!
   ```

2. **測試 2：中文訊息**
   ```
   這是一條測試訊息 📝
   ```

3. **測試 3：多行訊息**
   ```
   第一行
   第二行
   第三行
   ```

4. **測試 4：特殊字元**
   ```
   測試 @#$%^&*() !@#$
   ```

### 5.3 驗證結果

#### 在 Flask Server 終端機檢查日誌

您應該會看到類似以下日誌：
```
2025-11-15 16:00:00 [INFO] 收到 Webhook 請求
2025-11-15 16:00:00 [INFO] 收到文字訊息
2025-11-15 16:00:00 [DEBUG] 訊息內容: Hello, LifeLogger!
2025-11-15 16:00:00 [DEBUG] 使用者 ID: U1234567890abcdef
2025-11-15 16:00:00 [DEBUG] 台灣時間: 2025-11-15 16:00:00
2025-11-15 16:00:00 [INFO] 成功寫入訊息到 Google Sheets: 2025-11
2025-11-15 16:00:00 [INFO] 文字訊息處理完成
```

#### 在 Google Sheets 檢查資料

1. 開啟您的 Google Sheets 試算表
2. 檢查是否有當前月份的工作表（例如：`2025-11`）
3. 確認訊息已寫入，格式如下：

| 時間 | 類型 | 內容 |
|------|------|------|
| 2025-11-15 16:00:00 | 文字 | Hello, LifeLogger! |
| 2025-11-15 16:00:15 | 文字 | 這是一條測試訊息 📝 |

---

## 🐛 疑難排解

### 問題 1: Webhook Verify 失敗

**可能原因**：
- ngrok URL 不正確
- Flask server 未運行
- Webhook URL 未加上 `/webhook` 路徑

**解決方法**：
1. 確認 Flask server 正在運行（終端機 1）
2. 確認 ngrok 正在運行（終端機 2）
3. 檢查 Webhook URL 格式：`https://xxx.ngrok-free.app/webhook`
4. 重新驗證

### 問題 2: 發送訊息後沒有反應

**檢查步驟**：
1. 檢查 Flask server 終端機是否有日誌輸出
2. 檢查是否已關閉 LINE 的自動回覆功能
3. 檢查 ngrok 的 Web Interface（http://127.0.0.1:4040）查看請求記錄

### 問題 3: Google Sheets 沒有寫入資料

**檢查步驟**：
1. 檢查 Flask server 終端機的錯誤訊息
2. 確認 `.env` 中的 `SPREADSHEET_ID` 正確
3. 確認試算表已分享給 Service Account
4. 重新測試 Google Sheets 連線：
   ```bash
   python test_sheets.py
   ```

### 問題 4: ngrok 免費版限制

ngrok 免費版限制：
- 每次啟動 URL 會改變（需要重新設定 LINE Webhook URL）
- 每分鐘 40 個請求限制

**建議**：
- 測試完成後可以考慮使用固定網域服務（需付費）
- 或部署到雲端平台（Google Cloud Run, Heroku, AWS Lambda 等）

---

## ✅ 測試完成檢查清單

完成所有測試後，確認：

- [ ] ✅ Flask server 正常啟動
- [ ] ✅ ngrok 隧道已建立
- [ ] ✅ LINE Webhook URL 設定成功
- [ ] ✅ Webhook 驗證通過
- [ ] ✅ 成功發送測試訊息
- [ ] ✅ Flask server 日誌顯示訊息處理成功
- [ ] ✅ Google Sheets 正確記錄訊息
- [ ] ✅ 時間戳記為台灣時區
- [ ] ✅ 訊息格式正確（時間 | 類型 | 內容）

---

## 🎉 下一步

測試成功後，您可以：

1. **繼續開發 Phase 4**：實作圖片訊息記錄
2. **部署到生產環境**：使用雲端平台進行正式部署
3. **監控和優化**：加入監控和性能優化

---

**祝測試順利！** 🚀

如有問題，請檢查 Flask server 和 ngrok 的終端機輸出日誌。
