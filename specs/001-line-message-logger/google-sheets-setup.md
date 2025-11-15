# Google Sheets 串接準備指南

**Date**: 2025-11-15 | **Plan**: [plan.md](./plan.md)

本文件說明如何準備 Google Sheets API 串接，這是實作 LINE 訊息記錄器的必要前置作業。

---

## 📋 總覽

本專案需要使用以下 Google 服務：
- **Google Sheets API**: 讀寫試算表資料
- **Google Drive API**: 上傳並儲存圖片

我們使用 **Service Account**（服務帳戶）方式進行認證，讓程式可以自動存取 Google 服務而不需要手動登入。

---

## 🚀 快速準備檢查清單

完成後你應該擁有：
- [ ] Google Cloud 專案已建立
- [ ] Google Sheets API 已啟用
- [ ] Google Drive API 已啟用
- [ ] Service Account 已建立
- [ ] Service Account JSON 金鑰已下載（`service_account.json`）
- [ ] Google Sheets 試算表已建立並取得 ID
- [ ] 試算表已分享給 Service Account（編輯者權限）
- [ ] Google Drive 資料夾已建立並取得 ID（選用）
- [ ] 資料夾已分享給 Service Account（編輯者權限）

---

## 步驟 1: 建立 Google Cloud 專案

### 1.1 前往 Google Cloud Console

網址: https://console.cloud.google.com/

### 1.2 建立新專案

1. 點擊上方「選取專案」下拉選單
2. 點擊「新增專案」
3. 填寫專案資訊：
   - **專案名稱**: `linebot-lifelogger`（或任意名稱）
   - **組織**: 保留預設（無組織）
4. 點擊「建立」
5. 等待專案建立完成（約 10-30 秒）

---

## 步驟 2: 啟用必要的 API

### 2.1 啟用 Google Sheets API

1. 確認已選擇剛建立的專案（左上角專案名稱）
2. 左側選單 → 「API 和服務」→「已啟用的 API 和服務」
3. 點擊「+ 啟用 API 和服務」
4. 搜尋「**Google Sheets API**」
5. 點擊進入 Google Sheets API 頁面
6. 點擊「**啟用**」按鈕
7. 等待啟用完成

### 2.2 啟用 Google Drive API

1. 返回「啟用 API 和服務」頁面
2. 搜尋「**Google Drive API**」
3. 點擊進入 Google Drive API 頁面
4. 點擊「**啟用**」按鈕
5. 等待啟用完成

**驗證**: 在「已啟用的 API 和服務」頁面應該看到兩個 API。

---

## 步驟 3: 建立 Service Account

### 3.1 前往服務帳戶頁面

1. 左側選單 → 「IAM 與管理」→「**服務帳戶**」
2. 點擊「**+ 建立服務帳戶**」

### 3.2 填寫服務帳戶詳細資訊

**步驟 1: 服務帳戶詳細資料**
- **服務帳戶名稱**: `linebot-sheets-writer`
- **服務帳戶 ID**: 自動產生（例如：`linebot-sheets-writer`）
- **服務帳戶說明**: `LINE Bot 訊息記錄器用於寫入 Google Sheets`
- 點擊「**建立並繼續**」

**步驟 2: 將此服務帳戶存取權授予專案**
- 此步驟可選，直接點擊「**繼續**」

**步驟 3: 授予使用者存取此服務帳戶的權限**
- 此步驟可選，直接點擊「**完成**」

### 3.3 記錄 Service Account Email

建立完成後，你會看到服務帳戶列表。

**重要**: 複製並記錄 Service Account 的 Email 地址，格式類似：
```
linebot-sheets-writer@your-project-id.iam.gserviceaccount.com
```

**這個 Email 稍後要用來分享 Google Sheets 試算表！**

---

## 步驟 4: 下載 Service Account 金鑰

### 4.1 進入服務帳戶詳細資訊

1. 在服務帳戶列表中，點擊剛建立的 `linebot-sheets-writer@...`
2. 切換到「**金鑰**」分頁

### 4.2 建立並下載 JSON 金鑰

1. 點擊「**新增金鑰**」
2. 選擇「**建立新的金鑰**」
3. 金鑰類型選擇「**JSON**」
4. 點擊「**建立**」

### 4.3 儲存金鑰檔案

- JSON 檔案會自動下載到你的電腦
- 檔名格式類似：`your-project-id-xxxxxxxxxxxxx.json`
- **建議**: 重新命名為 `service_account.json`
- **儲存位置**: 稍後放到專案根目錄

**⚠️ 安全警告**:
- 此檔案包含私密金鑰，**絕對不要**上傳到 Git 或公開分享
- 如果不慎洩漏，請立即刪除此金鑰並建立新的

---

## 步驟 5: 建立 Google Sheets 試算表

### 5.1 建立新試算表

1. 前往 Google Sheets: https://sheets.google.com/
2. 點擊「**空白**」建立新的試算表
3. 將試算表命名為：`LINE Bot LifeLogger`（或任意名稱）

### 5.2 取得試算表 ID

試算表的 URL 格式如下：
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0
                                        ^^^^^^^^^^^^^^^^
```

**SPREADSHEET_ID** 是一長串英數字，例如：
```
1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3
```

**複製並儲存這個 ID**，稍後會用到。

---

## 步驟 6: 分享試算表給 Service Account ⭐ 重要

這是**最關鍵的步驟**！如果沒有完成，程式將無法寫入試算表。

### 6.1 開啟共用設定

1. 在試算表右上角，點擊「**共用**」按鈕

### 6.2 新增 Service Account

1. 在「新增使用者和群組」欄位中，**貼上 Service Account Email**
   ```
   linebot-sheets-writer@your-project-id.iam.gserviceaccount.com
   ```

2. 確認權限設定：
   - 角色選擇：**編輯者**（Editor）
   - **取消勾選**「通知使用者」（Service Account 不需要通知）

3. 點擊「**完成**」或「**傳送**」

### 6.3 驗證分享成功

在試算表的「共用」設定中，應該可以看到 Service Account Email 出現在協作者列表中。

---

## 步驟 7: 建立 Google Drive 資料夾（用於儲存圖片）

### 7.1 建立資料夾

1. 前往 Google Drive: https://drive.google.com/
2. 點擊左上角「**+ 新增**」
3. 選擇「**資料夾**」
4. 命名為：`LINE Bot Images`
5. 點擊「建立」

### 7.2 取得資料夾 ID

1. 開啟剛建立的資料夾
2. 查看 URL，格式如下：
   ```
   https://drive.google.com/drive/folders/FOLDER_ID
                                           ^^^^^^^^^
   ```

3. **複製並儲存 FOLDER_ID**

### 7.3 分享資料夾給 Service Account

1. 右鍵點擊資料夾 → 「**共用**」
2. 新增 Service Account Email（同上）
3. 角色選擇：**編輯者**
4. **取消勾選**「通知使用者」
5. 點擊「**完成**」

---

## 📝 完成後的檢查清單

確認你已經取得以下資訊：

### Google Cloud 專案
- [x] 專案名稱：`linebot-lifelogger`
- [x] Google Sheets API 已啟用
- [x] Google Drive API 已啟用

### Service Account
- [x] 服務帳戶名稱：`linebot-sheets-writer`
- [x] Service Account Email：`linebot-sheets-writer@your-project-id.iam.gserviceaccount.com`
- [x] JSON 金鑰檔案已下載：`service_account.json`

### Google Sheets
- [x] 試算表名稱：`LINE Bot LifeLogger`
- [x] 試算表 ID：`1a2b3c4d5e6f...`
- [x] 已分享給 Service Account（編輯者權限）

### Google Drive（圖片儲存）
- [x] 資料夾名稱：`LINE Bot Images`
- [x] 資料夾 ID：`1xyz...`
- [x] 已分享給 Service Account（編輯者權限）

---

## 🔧 環境變數設定

將以下資訊加入專案的 `.env` 檔案：

```bash
# Google API 設定
GOOGLE_CREDENTIALS_FILE=service_account.json
SPREADSHEET_ID=你的試算表ID
DRIVE_FOLDER_ID=你的Drive資料夾ID

# LINE Bot 設定（你應該已經有）
LINE_CHANNEL_ACCESS_TOKEN=你的LINE_Token
LINE_CHANNEL_SECRET=你的LINE_Secret
```

**重要**:
- 將 `service_account.json` 放在專案根目錄
- 將 `.env` 和 `service_account.json` 加入 `.gitignore`

---

## ✅ 驗證設定

完成所有步驟後，可以用以下 Python 程式碼測試：

```python
import gspread
from google.oauth2.service_account import Credentials

# 設定權限範圍
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# 載入憑證
creds = Credentials.from_service_account_file(
    'service_account.json',
    scopes=scopes
)

# 建立 gspread 客戶端
gc = gspread.authorize(creds)

# 開啟試算表（替換成你的試算表 ID）
spreadsheet = gc.open_by_key('你的試算表ID')

# 測試寫入
worksheet = spreadsheet.sheet1
worksheet.update('A1', 'Hello from Python!')

print("✅ 成功！Google Sheets 設定完成！")
```

**執行測試**:
```bash
pip install gspread google-auth
python test_sheets.py
```

如果沒有錯誤訊息，並且在試算表的 A1 儲存格看到「Hello from Python!」，代表設定成功！

---

## 🔒 安全性最佳實踐

### 1. 絕對不要將憑證提交到 Git

在 `.gitignore` 中加入：
```
# Google Credentials
service_account.json
*.json

# Environment variables
.env
.env.local

# Python
__pycache__/
*.pyc
*.pyo
```

### 2. 使用環境變數

不要在程式碼中硬編碼任何憑證或 ID。

### 3. 定期輪換金鑰

建議每 90 天輪換一次 Service Account 金鑰：
1. 建立新金鑰
2. 更新應用程式使用新金鑰
3. 刪除舊金鑰

### 4. 最小權限原則

Service Account 只需要：
- Google Sheets: 編輯者權限（僅針對特定試算表）
- Google Drive: 編輯者權限（僅針對特定資料夾）

不需要給予專案層級或組織層級的權限。

---

## ❓ 常見問題排解

### Q1: 程式執行時出現 "Permission denied" 錯誤

**原因**: 試算表沒有分享給 Service Account

**解決方法**:
1. 確認 Service Account Email 正確
2. 重新分享試算表給 Service Account
3. 確認權限是「編輯者」而非「檢視者」

### Q2: 找不到試算表（"Spreadsheet not found"）

**原因**: 試算表 ID 錯誤或 API 未啟用

**解決方法**:
1. 重新複製試算表 ID（從 URL）
2. 確認 Google Sheets API 已啟用
3. 等待幾分鐘讓 API 啟用生效

### Q3: JSON 金鑰無效（"Invalid credentials"）

**原因**: 金鑰檔案損壞或過期

**解決方法**:
1. 重新下載 JSON 金鑰
2. 確認檔案內容完整（是有效的 JSON 格式）
3. 如果金鑰被刪除，需要建立新的金鑰

### Q4: API 配額超過限制

**原因**: 呼叫 API 次數過多

**解決方法**:
1. 使用批次操作減少 API 呼叫
2. 實作快取機制
3. 申請提高配額（Google Cloud Console）

---

## 📚 相關資源

- [Google Sheets API 官方文件](https://developers.google.com/sheets/api)
- [Google Drive API 官方文件](https://developers.google.com/drive)
- [gspread 函式庫文件](https://docs.gspread.org/)
- [Service Account 說明](https://cloud.google.com/iam/docs/service-accounts)

---

**版本**: 1.0.0
**建立日期**: 2025-11-15
**下一步**: 開始 Phase 1 專案設定
