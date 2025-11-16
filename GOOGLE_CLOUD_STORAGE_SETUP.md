# Google Cloud Storage 設定指南

## 為什麼使用 Google Cloud Storage？

Google Cloud Storage (GCS) 比 Google Drive 更適合 Service Account 使用：

- ✅ **Service Account 原生支援**：不需要分享或授權
- ✅ **與 Cloud Run 無縫整合**：同一個 GCP 專案
- ✅ **成本極低**：每月前 5GB 免費，之後每 GB 約 $0.02/月
- ✅ **速度更快**：專為程式存取設計
- ✅ **更穩定可靠**：99.999999999% 耐用性

---

## 📋 設定步驟

### 步驟 1：建立 Cloud Storage Bucket

#### 方法 A：使用 GCP Console（網頁介面）

1. 開啟 [Google Cloud Console - Cloud Storage](https://console.cloud.google.com/storage/browser)
2. 選擇你的專案（與 Cloud Run 同一個專案）
3. 點選「建立值區」(Create Bucket)
4. 設定值區：
   - **名稱**：`linebot-images-<your-project-id>`（全球唯一，建議加上專案 ID）
   - **位置類型**：Region
   - **位置**：`asia-east1`（台灣）或 `asia-northeast1`（日本，更近）
   - **儲存空間類別**：Standard
   - **存取權控制**：精細（Fine-grained）
   - **公開存取權**：不強制執行公開存取權防護（稍後設定個別檔案公開）
5. 點選「建立」

#### 方法 B：使用 gcloud 命令（推薦，更快）

```bash
# 設定變數
PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME="linebot-images-${PROJECT_ID}"
REGION="asia-east1"  # 台灣

# 建立 bucket
gsutil mb -p ${PROJECT_ID} -c STANDARD -l ${REGION} gs://${BUCKET_NAME}/

# 顯示 bucket 名稱（複製此名稱到 .env）
echo "✅ Bucket 建立完成："
echo "STORAGE_BUCKET_NAME=${BUCKET_NAME}"
```

### 步驟 2：設定 Bucket 權限（公開讀取）

圖片需要公開存取，讓 Google Sheets 可以顯示：

```bash
# 設定預設公開讀取權限（所有上傳的檔案自動公開）
gsutil iam ch allUsers:objectViewer gs://${BUCKET_NAME}
```

或者手動設定：
1. 在 GCP Console 中開啟 bucket
2. 切換到「權限」(Permissions) 分頁
3. 點選「授予存取權」
4. 新增主體：`allUsers`
5. 角色：「Storage Object Viewer」
6. 儲存

### 步驟 3：驗證 Service Account 權限

你的 Service Account 應該已經有存取權限（因為在同一個專案），驗證方式：

```bash
# 取得 Service Account email
SA_EMAIL=$(cat service_account.json | grep client_email | cut -d'"' -f4)

# 驗證權限
gsutil iam get gs://${BUCKET_NAME} | grep ${SA_EMAIL}
```

如果沒有權限，手動加入：

```bash
gsutil iam ch serviceAccount:${SA_EMAIL}:objectAdmin gs://${BUCKET_NAME}
```

### 步驟 4：設定環境變數

#### 本地開發（.env）

編輯 `.env` 檔案，**移除或註解** `DRIVE_FOLDER_ID`，改用：

```bash
# Google Cloud Storage 設定（Phase 4 圖片訊息）
STORAGE_BUCKET_NAME=linebot-images-your-project-id
```

#### 生產環境（.env.production）

編輯 `.env.production` 檔案：

```bash
# Google Cloud Storage 設定（Phase 4 圖片訊息）
STORAGE_BUCKET_NAME=linebot-images-your-project-id
```

---

## ✅ 驗證設定

### 測試上傳

執行本地測試：

```bash
python test_local_image_message.py
```

成功的話應該看到：

```
✅ StorageClient 初始化完成，Bucket: linebot-images-xxx
✅ 圖片上傳成功！
✅ 圖片 URL: https://storage.googleapis.com/linebot-images-xxx/test_linebot_20251116_123456.jpg
```

### 驗證公開存取

複製圖片 URL，在瀏覽器開啟，應該可以直接看到圖片（不需要登入 Google）。

如果看不到，檢查 bucket 權限設定（步驟 2）。

---

## 🔧 常見問題

### Q1: Bucket 名稱已存在怎麼辦？

**A**: Bucket 名稱必須全球唯一。建議加上你的專案 ID 或隨機字串：
```bash
linebot-images-my-project-123
linebot-images-prod-abc123
```

### Q2: 成本會很高嗎？

**A**: 非常便宜！估算：
- **儲存空間**：$0.02/GB/月
  - 1000 張圖片（每張 500KB）≈ 500MB ≈ $0.01/月
  - 10000 張圖片 ≈ 5GB ≈ $0.10/月
- **網路傳輸**：前 1GB 免費，之後 $0.12/GB
  - 每張圖片載入一次，10000 次 ≈ 5GB ≈ $0.60
- **API 操作**：Class A（寫入）$0.05/10000 次，Class B（讀取）$0.004/10000 次

**總計**：每月約 $1-2 美元（假設 10000 張圖片）

### Q3: 圖片會永久儲存嗎？

**A**: 是的，除非你手動刪除。建議設定生命週期規則自動刪除舊圖片：

```bash
# 建立生命週期規則檔案
cat > lifecycle.json << 'EOF'
{
  "rule": [{
    "action": {"type": "Delete"},
    "condition": {"age": 365}
  }]
}
EOF

# 套用規則（365 天後自動刪除）
gsutil lifecycle set lifecycle.json gs://${BUCKET_NAME}
```

### Q4: 可以改用 CDN 加速嗎？

**A**: 可以！GCS 支援 Cloud CDN，但需要額外設定：
1. 建立 Load Balancer
2. 啟用 Cloud CDN
3. 成本會稍微增加（但速度更快）

對於 LINE Bot 訊息記錄，直接用 GCS 已經足夠快。

### Q5: 如何查看已用空間和費用？

**A**:
```bash
# 查看 bucket 使用量
gsutil du -sh gs://${BUCKET_NAME}

# 查看詳細費用（GCP Console）
# https://console.cloud.google.com/billing
```

---

## 🔒 安全性建議

### 建議 1：限制上傳檔案類型

在程式中驗證檔案類型，只允許圖片：

```python
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
```

（已在 `storage_client.py` 中實作）

### 建議 2：定期檢查公開檔案

```bash
# 列出所有公開檔案
gsutil ls -L gs://${BUCKET_NAME}/** | grep -A 5 "ACL"
```

### 建議 3：啟用 Audit Logs

在 GCP Console → IAM & Admin → Audit Logs 中啟用 Cloud Storage 稽核日誌，追蹤所有存取記錄。

---

## 📚 相關文件

- [Google Cloud Storage 文件](https://cloud.google.com/storage/docs)
- [GCS 定價說明](https://cloud.google.com/storage/pricing)
- [gsutil 工具指南](https://cloud.google.com/storage/docs/gsutil)
- [專案部署指南](./CLOUD_RUN_DEPLOYMENT.md)

---

## 🚀 下一步

設定完成後：
1. 執行本地測試驗證上傳功能
2. 部署到 Cloud Run
3. 在 LINE 中傳送圖片測試
4. 檢查 Google Sheets 是否正確顯示圖片

Good luck! 🎉
