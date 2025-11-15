# Technical Research: LINE 訊息記錄器

**Date**: 2025-11-15 | **Plan**: [plan.md](./plan.md)

本文件記錄實作 LINE 訊息記錄器所需的技術研究成果。

---

## 1. LINE Messaging API

### 1.1 Webhook 事件結構

LINE Messaging API 透過 Webhook 傳送事件到我們的伺服器。

**文字訊息事件範例**:
```json
{
  "events": [
    {
      "type": "message",
      "message": {
        "type": "text",
        "id": "325708",
        "text": "Hello, world"
      },
      "timestamp": 1462629479859,
      "source": {
        "type": "user",
        "userId": "U4af4980629..."
      },
      "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA"
    }
  ]
}
```

**圖片訊息事件範例**:
```json
{
  "events": [
    {
      "type": "message",
      "message": {
        "type": "image",
        "id": "325709",
        "contentProvider": {
          "type": "line"
        }
      },
      "timestamp": 1462629479859,
      "source": {
        "type": "user",
        "userId": "U4af4980629..."
      },
      "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA"
    }
  ]
}
```

**其他訊息類型**（貼圖、影片、音訊）:
```json
{
  "message": {
    "type": "sticker",  // 或 "video", "audio", "file"
    "id": "325710",
    "packageId": "1",
    "stickerId": "1"
  }
}
```

### 1.2 圖片內容下載

使用 **Message Content API** 下載圖片：

**API 端點**:
```
GET https://api-data.line.me/v2/bot/message/{messageId}/content
```

**Headers**:
```
Authorization: Bearer {channel access token}
```

**回應**: 圖片的二進位資料（JPEG 或 PNG 格式）

**Python SDK 使用方式**:
```python
from linebot import LineBotApi

line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
message_content = line_bot_api.get_message_content(message_id)

# message_content.content 是圖片的二進位資料
with open('image.jpg', 'wb') as f:
    for chunk in message_content.iter_content():
        f.write(chunk)
```

### 1.3 回應訊息

**Reply API** 用於回應使用者:
```python
from linebot.models import TextSendMessage

line_bot_api.reply_message(
    reply_token,
    TextSendMessage(text='已記錄 ✓')
)
```

**限制**:
- Reply token 只能使用一次
- Webhook 必須在 3 秒內回應 HTTP 200

### 1.4 Python SDK 設定

**安裝**:
```bash
pip install line-bot-sdk
```

**基本設定**:
```python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage

# 初始化
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

# Webhook 處理
@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 訊息處理器
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    # 處理文字訊息
    pass

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    # 處理圖片訊息
    pass
```

---

## 2. Google Sheets API

### 2.1 gspread 基本使用

**安裝**:
```bash
pip install gspread google-auth
```

**Service Account 認證**:
```python
import gspread
from google.oauth2.service_account import Credentials

# 載入 Service Account 憑證
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = Credentials.from_service_account_file(
    'service_account.json',
    scopes=scopes
)

# 初始化 gspread 客戶端
gc = gspread.authorize(creds)

# 開啟試算表
spreadsheet = gc.open_by_key('SPREADSHEET_ID')

# 開啟或建立工作表
try:
    worksheet = spreadsheet.worksheet('2025-11')
except gspread.exceptions.WorksheetNotFound:
    worksheet = spreadsheet.add_worksheet(
        title='2025-11',
        rows=1000,
        cols=10
    )
```

### 2.2 基本讀寫操作

**寫入資料**:
```python
# 單一儲存格
worksheet.update('A1', 'Hello')

# 多個儲存格（更高效）
data = [
    ['2025-11-15 10:30:00', '文字', '今天天氣很好'],
    ['2025-11-15 10:31:00', '文字', '準備出門']
]
worksheet.append_rows(data)

# 指定範圍
worksheet.update('A1:C2', data)
```

**讀取資料**:
```python
# 所有資料
all_values = worksheet.get_all_values()

# 特定範圍
range_values = worksheet.get('A1:C10')

# 特定儲存格
cell_value = worksheet.acell('A1').value
```

### 2.3 圖片內嵌方法

**重要發現**: gspread 本身**不直接支援**圖片內嵌，需要使用底層的 `google-api-python-client`。

**方法 1: 使用 google-api-python-client** (建議)
```python
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import base64

# 建立 Sheets API 服務
creds = Credentials.from_service_account_file('service_account.json')
service = build('sheets', 'v4', credentials=creds)

# 讀取圖片並轉為 base64
with open('image.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# 準備請求
requests = [
    {
        'updateCells': {
            'rows': [
                {
                    'values': [
                        {
                            'userEnteredValue': {
                                'formulaValue': f'=IMAGE("{image_url}")'
                            }
                        }
                    ]
                }
            ],
            'fields': 'userEnteredValue',
            'start': {
                'sheetId': worksheet.id,
                'rowIndex': 0,
                'columnIndex': 0
            }
        }
    }
]

# 執行批次更新
body = {'requests': requests}
service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body=body
).execute()
```

**方法 2: 使用 IMAGE 函式** (更簡單但需要圖片 URL)
```python
# 如果圖片已上傳到可公開存取的 URL
image_formula = f'=IMAGE("{image_url}")'
worksheet.update('C1', image_formula)
```

**研究結論**:
- 由於 LINE 圖片 URL 有時效性，無法使用 IMAGE 函式
- 需要使用 **Drive API 上傳圖片** + **IMAGE 函式引用**
- 或使用 **Apps Script 自訂函式**內嵌圖片

**推薦方案**: 上傳圖片到 Google Drive，然後在 Sheets 中使用 IMAGE 函式

### 2.4 圖片內嵌實作步驟

```python
from googleapiclient.discovery import build
import io

# 1. 初始化 Drive API
drive_service = build('drive', 'v3', credentials=creds)

# 2. 建立專用資料夾（一次性操作）
folder_metadata = {
    'name': 'LINE Bot Images',
    'mimeType': 'application/vnd.google-apps.folder'
}
folder = drive_service.files().create(
    body=folder_metadata,
    fields='id'
).execute()
folder_id = folder.get('id')

# 3. 上傳圖片到 Drive
file_metadata = {
    'name': f'image_{timestamp}.jpg',
    'parents': [folder_id]
}
media = MediaIoBaseUpload(
    io.BytesIO(image_binary_data),
    mimetype='image/jpeg'
)
file = drive_service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id, webViewLink, webContentLink'
).execute()

# 4. 設定檔案為公開（可選，或使用共享連結）
drive_service.permissions().create(
    fileId=file.get('id'),
    body={'type': 'anyone', 'role': 'reader'}
).execute()

# 5. 取得可公開存取的 URL
file_id = file.get('id')
image_url = f"https://drive.google.com/uc?id={file_id}"

# 6. 在 Sheets 中使用 IMAGE 函式
worksheet.update('C1', f'=IMAGE("{image_url}")')
```

### 2.5 API 配額和限制

**Google Sheets API 配額** (免費):
- 每 100 秒 100 次請求
- 每分鐘 60 次讀取請求
- 每分鐘 60 次寫入請求

**Google Drive API 配額** (免費):
- 每 100 秒 1,000 次請求
- 每使用者每 100 秒 1,000 次請求

**儲存限制**:
- 每個 Google 帳戶 15 GB 免費儲存空間（Drive + Gmail + Photos 共用）
- 單一試算表最多 500 萬個儲存格

**最佳實踐**:
- 使用批次操作（batchUpdate）減少 API 呼叫次數
- 快取工作表 ID 避免重複查詢
- 實作指數退避重試機制處理配額錯誤

---

## 3. 圖片處理

### 3.1 Pillow 基本使用

**安裝**:
```bash
pip install Pillow
```

**圖片壓縮**:
```python
from PIL import Image
import io

# 載入圖片
image = Image.open(io.BytesIO(image_binary_data))

# 檢查圖片大小
width, height = image.size
print(f"Original size: {width}x{height}")

# 壓縮圖片（降低品質）
output = io.BytesIO()
image.save(output, format='JPEG', quality=85, optimize=True)
compressed_data = output.getvalue()
compressed_size = len(compressed_data)

# 調整尺寸
max_width = 800
if width > max_width:
    ratio = max_width / width
    new_height = int(height * ratio)
    resized_image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

    output = io.BytesIO()
    resized_image.save(output, format='JPEG', quality=85, optimize=True)
    compressed_data = output.getvalue()
```

### 3.2 壓縮策略

為符合 Google Sheets 和提升效能，需要智慧壓縮：

```python
def compress_image(image_data, max_size_kb=500):
    """
    壓縮圖片直到符合大小限制
    """
    image = Image.open(io.BytesIO(image_data))

    # 轉換為 RGB（如果是 RGBA）
    if image.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background

    # 嘗試不同的壓縮級別
    quality_levels = [85, 75, 65, 55, 45]
    resize_ratios = [1.0, 0.8, 0.6, 0.4]

    for ratio in resize_ratios:
        if ratio < 1.0:
            new_size = (int(image.width * ratio), int(image.height * ratio))
            resized = image.resize(new_size, Image.Resampling.LANCZOS)
        else:
            resized = image

        for quality in quality_levels:
            output = io.BytesIO()
            resized.save(output, format='JPEG', quality=quality, optimize=True)
            data = output.getvalue()
            size_kb = len(data) / 1024

            if size_kb <= max_size_kb:
                return data

    # 如果仍然過大，返回最小版本並記錄警告
    return data
```

### 3.3 格式支援

**LINE 支援的圖片格式**:
- JPEG
- PNG

**Pillow 處理建議**:
- 統一轉換為 JPEG（更小的檔案大小）
- PNG 轉 JPEG 時處理透明度（轉為白底）

---

## 4. 時區處理

### 4.1 pytz 使用

**安裝**:
```bash
pip install pytz
```

**基本使用**:
```python
import pytz
from datetime import datetime

# 定義台灣時區
taiwan_tz = pytz.timezone('Asia/Taipei')

# LINE timestamp 是 UTC 毫秒時間戳記
line_timestamp_ms = 1462629479859
utc_dt = datetime.utcfromtimestamp(line_timestamp_ms / 1000)

# 轉換為台灣時區
utc_dt = pytz.utc.localize(utc_dt)
taiwan_dt = utc_dt.astimezone(taiwan_tz)

# 格式化輸出
formatted_time = taiwan_dt.strftime('%Y-%m-%d %H:%M:%S')
# 輸出: '2016-05-07 18:31:19'
```

### 4.2 週計算（週日為起始日）

```python
from datetime import datetime, timedelta
import calendar

def get_week_number_sunday_start(dt):
    """
    計算週次（週日為一週起始日）
    """
    # 取得該年第一天
    year_start = datetime(dt.year, 1, 1)

    # 計算該年第一個週日
    days_to_sunday = (6 - year_start.weekday()) % 7
    first_sunday = year_start + timedelta(days=days_to_sunday)

    # 如果日期在第一個週日之前，算作第 0 週或上一年最後一週
    if dt < first_sunday:
        return 0

    # 計算週數
    delta = dt - first_sunday
    week_number = (delta.days // 7) + 1

    return week_number

def is_new_week(current_dt, previous_dt):
    """
    判斷是否跨越週界（週六到週日）
    """
    # weekday(): 週一=0, 週日=6
    # 如果前一則訊息不是週日，而當前訊息是週日，則跨週
    return previous_dt.weekday() != 6 and current_dt.weekday() == 6

# 使用範例
taiwan_dt = datetime(2025, 11, 16)  # 週日
week_num = get_week_number_sunday_start(taiwan_dt)
print(f"Week number: {week_num}")
```

**Python weekday() 對照**:
- 0 = Monday (週一)
- 1 = Tuesday (週二)
- 2 = Wednesday (週三)
- 3 = Thursday (週四)
- 4 = Friday (週五)
- 5 = Saturday (週六)
- 6 = Sunday (週日)

---

## 5. 實作建議整合

### 5.1 完整流程

```
1. 接收 LINE Webhook 事件
   ↓
2. 驗證簽章
   ↓
3. 解析訊息類型
   ├─ 文字訊息 → 提取文字內容
   ├─ 圖片訊息 → 下載圖片 → 壓縮 → 上傳到 Drive → 取得 URL
   └─ 其他類型 → 標記為「[不支援的訊息類型]」
   ↓
4. 轉換時間到台灣時區
   ↓
5. 判斷月份，建立或開啟對應工作表
   ↓
6. 判斷是否需要插入週分界標記
   ↓
7. 寫入資料到 Google Sheets
   ↓
8. 回應 LINE Bot「已記錄 ✓」（P3 功能）
   ↓
9. 返回 HTTP 200（必須在 3 秒內）
```

### 5.2 錯誤處理點

需要實作錯誤處理的地方：
1. LINE 簽章驗證失敗 → 返回 400
2. 圖片下載失敗 → 記錄「圖片下載失敗」+ 錯誤日誌
3. 圖片壓縮後仍過大 → 記錄「圖片過大」+ 錯誤日誌
4. Drive API 上傳失敗 → 記錄錯誤 + 重試一次
5. Sheets API 寫入失敗 → 記錄詳細錯誤日誌
6. 處理時間超過 2.5 秒 → 記錄警告

### 5.3 效能優化建議

1. **快取工作表 ID**: 避免每次都查詢工作表
2. **批次寫入**: 累積多筆訊息後一次寫入（考慮 P2）
3. **非同步上傳圖片**: 圖片上傳到 Drive 可以非同步處理（考慮 P2）
4. **連線池**: 重用 HTTP 連線減少建立時間

---

## 6. 依賴套件清單

**requirements.txt**:
```
# LINE Messaging API
line-bot-sdk==3.5.0

# Google APIs
gspread==5.12.0
google-auth==2.25.2
google-api-python-client==2.110.0

# 圖片處理
Pillow==10.1.0

# 時區處理
pytz==2023.3

# Web 框架
Flask==3.0.0

# 環境變數管理
python-dotenv==1.0.0

# 測試
pytest==7.4.3
pytest-cov==4.1.0
requests-mock==1.11.0
```

---

## 7. 研究結論

### 關鍵技術可行性評估

| 技術需求 | 可行性 | 實作方案 | 風險 |
|---------|--------|---------|------|
| LINE Webhook 接收 | ✅ 高 | Flask + line-bot-sdk | 低 |
| 文字訊息記錄 | ✅ 高 | gspread.append_rows | 低 |
| 圖片下載 | ✅ 高 | LINE Message Content API | 中（網路失敗） |
| 圖片壓縮 | ✅ 高 | Pillow 多級壓縮 | 低 |
| 圖片內嵌 Sheets | ⚠️ 中 | Drive upload + IMAGE 函式 | 中（API 複雜度） |
| 月份子表單管理 | ✅ 高 | gspread worksheet 操作 | 低 |
| 週分界標記 | ✅ 高 | 時間計算 + 條件插入 | 低 |
| 時區處理 | ✅ 高 | pytz | 低 |
| 3 秒回應限制 | ⚠️ 中 | 優化流程或非同步處理 | 中（效能） |

### 待確認事項

1. ✅ Google Service Account 憑證取得方式
2. ✅ Google Drive 資料夾權限設定
3. ✅ 圖片壓縮的最佳參數（需實測）
4. ✅ API 配額在預期使用量下是否足夠

### 建議調整

1. **圖片內嵌方案**: 使用 Drive + IMAGE 函式（可行但增加複雜度）
2. **非同步處理**: 如果同步處理超過 3 秒，Phase 2 改用 Celery
3. **批次寫入**: 考慮累積 5-10 則訊息後批次寫入（提升效能）

---

**研究完成日期**: 2025-11-15
**下一步**: 定義資料模型 (`data-model.md`)
