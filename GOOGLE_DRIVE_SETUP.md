# Google Drive 設定指南

## 為什麼需要設定 Google Drive 資料夾？

**重要**：Service Account 沒有自己的 Google Drive 儲存空間配額，無法上傳檔案到「我的雲端硬碟」根目錄。

因此，圖片訊息功能（Phase 4）需要：
1. 建立一個 **使用者的** Google Drive 資料夾
2. 將該資料夾**分享**給 Service Account
3. 設定 `DRIVE_FOLDER_ID` 環境變數

---

## 📋 設定步驟

### 步驟 1：建立 Google Drive 資料夾

1. 開啟 [Google Drive](https://drive.google.com/)
2. 點選「新增」→「新資料夾」
3. 命名資料夾（建議：`LINE Bot Images` 或 `LINE 訊息圖片`）
4. 點選「建立」

### 步驟 2：取得資料夾 ID

1. 開啟剛建立的資料夾
2. 查看瀏覽器網址列，格式如下：
   ```
   https://drive.google.com/drive/folders/1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P
                                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                           這就是 FOLDER_ID
   ```
3. 複製 `folders/` 後面的部分（如：`1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P`）

### 步驟 3：取得 Service Account Email

1. 開啟專案根目錄的 `service_account.json`
2. 找到 `client_email` 欄位，格式如：
   ```json
   {
     "client_email": "your-service-account@your-project.iam.gserviceaccount.com"
   }
   ```
3. 複製這個 email 地址

### 步驟 4：分享資料夾給 Service Account

1. 在 Google Drive 中，對剛建立的資料夾點選右鍵
2. 選擇「共用」或「分享」
3. 在「新增使用者或群組」欄位中，貼上 Service Account email
4. 設定權限為「編輯者」（Editor）
5. **取消勾選**「通知使用者」（Service Account 不是真實使用者，不需要通知）
6. 點選「分享」或「完成」

### 步驟 5：設定環境變數

#### 本地開發（.env）

編輯專案根目錄的 `.env` 檔案，加入：

```bash
DRIVE_FOLDER_ID=1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P
```

#### 生產環境（Cloud Run）

編輯 `.env.production` 檔案，加入：

```bash
DRIVE_FOLDER_ID=1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P
```

然後重新部署：

```bash
./deploy.sh
```

---

## ✅ 驗證設定

執行本地測試確認設定正確：

```bash
python test_local_image_message.py
```

如果設定成功，你應該會看到：

```
✅ DriveClient 初始化完成，目標資料夾: 1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P
✅ 圖片上傳成功！
```

並在 Google Drive 資料夾中看到上傳的測試圖片。

---

## 🔧 常見問題

### Q1: 為什麼不能上傳到 Drive 根目錄？

**A**: Service Account 是 Google Cloud 的服務帳號，不是真實的 Google 使用者帳號，因此：
- ❌ 沒有 15GB 免費儲存空間
- ❌ 無法存取「我的雲端硬碟」
- ✅ 只能存取「與我分享」的資料夾

這是 Google 的安全機制，確保 Service Account 只能存取明確授權的資源。

### Q2: 如果不設定 DRIVE_FOLDER_ID 會怎樣？

**A**: 程式會在初始化 DriveClient 時拋出錯誤：

```
ValueError: DRIVE_FOLDER_ID is required for Service Account uploads
```

圖片訊息無法正常運作。

### Q3: 可以使用 Shared Drive（共用雲端硬碟）嗎？

**A**: 可以！Shared Drive 的資料夾 ID 設定方式相同：
1. 開啟 Shared Drive 中的資料夾
2. 從 URL 取得 FOLDER_ID
3. 確保 Service Account 有該 Shared Drive 的存取權限

### Q4: 資料夾會佔用多少空間？

**A**: 每張圖片壓縮後約 100-500KB，估算：
- 1000 張圖片 ≈ 100-500MB
- 10000 張圖片 ≈ 1-5GB

建議定期清理舊圖片，或使用 Shared Drive 取得更大空間。

---

## 📚 相關文件

- [Google Drive API - Service Accounts](https://developers.google.com/drive/api/guides/about-auth#service_accounts)
- [Google Workspace - Shared Drives](https://developers.google.com/workspace/drive/api/guides/about-shareddrives)
- [專案部署指南](./CLOUD_RUN_DEPLOYMENT.md)
