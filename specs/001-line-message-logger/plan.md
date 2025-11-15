# Implementation Plan: LINE 訊息記錄器

**Branch**: `001-line-message-logger` | **Date**: 2025-11-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-line-message-logger/spec.md`

## Summary

實作 LINE Bot 訊息記錄器，接收使用者的文字和圖片訊息，自動記錄到 Google Sheets 中。系統以月份建立子表單，以週（週日為起始日）進行分界標記，並將圖片內嵌到儲存格中確保長期可存取。所有時間戳記使用台灣時區（UTC+8）。

**技術方法**：
- 使用 Flask 建立 LINE Webhook 接收端點
- 使用 LINE Messaging API SDK 處理訊息事件
- 使用 Google Sheets API 寫入資料和內嵌圖片
- 使用 Pillow 處理圖片壓縮（符合 Google Sheets 限制）
- 使用 pytz 處理時區轉換

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- Flask 3.0+ (Web 框架)
- line-bot-sdk 3.5+ (LINE Messaging API)
- gspread 5.12+ (Google Sheets API wrapper)
- google-auth 2.25+ (Google API 認證)
- Pillow 10.1+ (圖片處理)
- pytz 2023.3+ (時區處理)

**Storage**: Google Sheets (雲端試算表)
**Testing**: pytest 7.4+ (整合測試優先)
**Target Platform**: Linux server (Docker 容器化部署)
**Project Type**: Single (單一後端服務)
**Performance Goals**:
- LINE Webhook 回應時間 < 3 秒（平台要求）
- 95% 訊息在 2 秒內完成記錄
- 支援每日 1000+ 訊息記錄量

**Constraints**:
- Google Sheets 單一儲存格限制 50,000 字元
- LINE 圖片下載有時效性（需在收到訊息後盡快下載）
- 環境變數儲存敏感憑證（LINE Bot Token、Google Service Account）

**Scale/Scope**:
- 單一使用者 MVP
- 預期每日 50-200 則訊息
- 長期運作（月份子表單自動管理）

## Constitution Check

### MVP 優先開發 ✅
- **P1 功能**（MVP）：文字訊息記錄、圖片訊息記錄
- **P2 功能**（優化）：月份子表單、週分界標記
- **P3 功能**（增強）：Bot 回應確認
- 所有功能獨立可測試和部署

### 透過測試確保品質 ✅
- 整合測試覆蓋所有使用者旅程：
  - LINE Webhook → 訊息處理 → Google Sheets 寫入
  - 圖片下載 → 壓縮 → 內嵌到 Sheets
- 契約測試驗證外部 API（LINE、Google Sheets）
- 單元測試用於複雜邏輯（時區轉換、週計算）

### 簡單勝過完美 ✅
- 使用 Flask 最小化 Web 框架（避免 Django 等重量級框架）
- 直接使用 gspread 而非自建 Repository 層
- 無狀態設計，不需要資料庫
- 不使用訊息佇列（MVP 階段同步處理即可）

### 便利性和開發者體驗 ✅
- 環境變數配置（.env 檔案）
- 詳細日誌記錄（Python logging）
- Docker 容器化確保一致性開發/部署環境
- 清晰錯誤訊息便於除錯

### 可用性和使用者價值 ✅
- 自動化月份子表單建立（零手動維護）
- 圖片內嵌確保長期可存取
- 週分界標記提升可讀性
- 時區統一避免混淆

### 憲章符合性總結
✅ **無違反項目** - 所有設計決策符合憲章五大原則

## Project Structure

### Documentation (this feature)

```text
specs/001-line-message-logger/
├── spec.md              # 功能規格
├── plan.md              # 本文件 - 技術規劃
├── research.md          # 技術研究（API 調查、圖片處理方案）
├── data-model.md        # 資料模型（Google Sheets 表格結構）
├── api-contracts.md     # API 合約（LINE Webhook、Google Sheets API）
└── tasks.md             # 實作任務（待 /speckit.tasks 生成）
```

### Source Code (repository root)

```text
src/
├── webhook/
│   ├── __init__.py
│   ├── app.py              # Flask 應用程式主檔
│   └── handlers.py         # LINE 訊息事件處理器
├── services/
│   ├── __init__.py
│   ├── line_client.py      # LINE API 客戶端
│   ├── sheets_client.py    # Google Sheets API 客戶端
│   ├── image_processor.py  # 圖片下載和處理
│   └── time_utils.py       # 時區轉換工具
├── models/
│   ├── __init__.py
│   └── message.py          # 訊息資料類別
└── config.py               # 配置管理

tests/
├── integration/
│   ├── test_webhook_flow.py       # Webhook 完整流程測試
│   ├── test_sheets_integration.py # Google Sheets 整合測試
│   └── test_line_integration.py   # LINE API 整合測試
├── contract/
│   ├── test_line_api.py           # LINE API 契約測試
│   └── test_sheets_api.py         # Sheets API 契約測試
└── unit/
    ├── test_image_processor.py    # 圖片處理單元測試
    └── test_time_utils.py         # 時區工具單元測試

# 部署相關
Dockerfile
docker-compose.yml
requirements.txt
.env.example
README.md
```

**Structure Decision**:
選擇「Option 1: Single project」結構，因為這是單一後端服務，不需要前端或多專案架構。使用標準的 Python 專案結構（src/ 和 tests/ 分離），按功能劃分模組（webhook、services、models），符合簡單性原則。

## Complexity Tracking

> 本專案無憲章違反項目，此節留空。

---

## 實作階段規劃

### Phase 0: 技術研究
**產出**: `research.md`

需要研究的技術點：
1. **LINE Messaging API**
   - Webhook 事件結構
   - 圖片訊息下載方式（Message Content API）
   - 回應訊息格式

2. **Google Sheets API**
   - 使用 gspread 進行基本讀寫
   - 圖片內嵌方法（insertDimension + CellData with ImageValue）
   - 子表單（工作表）建立和管理
   - API 配額限制和最佳實踐

3. **圖片處理**
   - Pillow 圖片壓縮和格式轉換
   - Base64 編碼（Google Sheets 內嵌圖片需求）
   - 最佳壓縮參數（在品質和大小間平衡）

4. **時區處理**
   - pytz 使用方式
   - 週計算邏輯（週日為起始日）

### Phase 1: 系統設計
**產出**: `data-model.md`, `api-contracts.md`

#### Data Model (Google Sheets 表格結構)
需要定義：
- 月份子表單命名規則
- 每個子表單的欄位結構（時間、類型、內容）
- 週分界標記格式
- 圖片儲存格格式

#### API Contracts
需要定義：
- LINE Webhook 請求/回應格式
- Google Sheets API 呼叫序列
- 錯誤處理和重試策略

### Phase 2: 任務分解
**產出**: `tasks.md` (由 /speckit.tasks 生成)

預期任務優先順序：
1. **P1**: 設定專案基礎（Flask app, 環境變數）
2. **P1**: 實作 LINE Webhook 接收
3. **P1**: 實作文字訊息記錄到 Sheets
4. **P1**: 實作圖片下載和處理
5. **P1**: 實作圖片內嵌到 Sheets
6. **P2**: 實作月份子表單自動建立
7. **P2**: 實作週分界標記
8. **P3**: 實作 Bot 回應確認
9. **所有**: 整合測試和錯誤處理

---

## 技術決策記錄

### TD-001: 使用 gspread 而非 google-api-python-client
**決策**: 使用 gspread 套件
**理由**:
- gspread 提供更簡潔的 API（符合簡單性原則）
- 內建 Service Account 認證支援
- 社群活躍，文件完整
**替代方案**: google-api-python-client（過於低階，需要更多樣板程式碼）

### TD-002: 圖片內嵌而非 URL 連結
**決策**: 將圖片下載並內嵌到 Google Sheets
**理由**:
- LINE 圖片 URL 有時效性（約 30 天）
- 內嵌確保長期可存取
- 符合使用者需求（需求釐清結果）
**替代方案**:
- 僅儲存 URL（會失效）❌
- 上傳到 Google Drive（增加複雜度）❌

### TD-003: 同步處理訊息（MVP 階段）
**決策**: 在 Webhook 處理函式中同步處理訊息記錄
**理由**:
- MVP 階段預期訊息量低（每日 50-200 則）
- 簡化架構，不需要訊息佇列
- 符合 3 秒 Webhook 回應限制
**替代方案**: 使用 Celery 或 RQ 非同步處理（過度工程，待 MVP 驗證後再考慮）

### TD-004: 無資料庫設計
**決策**: 不使用資料庫，所有資料直接寫入 Google Sheets
**理由**:
- Google Sheets 本身就是儲存目標
- 減少系統複雜度
- 無需資料同步邏輯
**替代方案**: 使用 SQLite/PostgreSQL 暫存（增加複雜度和維護成本）❌

### TD-005: 錯誤處理策略
**決策**: 記錄詳細錯誤日誌，不自動重試
**理由**:
- MVP 階段保持簡單
- 詳細日誌便於手動排查和修復
- 符合需求釐清結果
**替代方案**: 自動重試機制（增加複雜度，可在 P2/P3 加入）

---

## 風險和緩解措施

### R-001: Google Sheets API 配額限制
**風險**: 達到 API 呼叫配額（每分鐘 60 次讀取，每分鐘 60 次寫入）
**影響**: 高流量時無法記錄訊息
**緩解**:
- MVP 階段單一使用者unlikely達到限制
- 實作批次寫入（一次寫入多筆記錄）
- 監控 API 使用量，必要時申請配額提升

### R-002: LINE 圖片下載失敗
**風險**: 網路問題或 LINE API 錯誤導致圖片下載失敗
**影響**: 無法記錄圖片訊息
**緩解**:
- 實作錯誤處理，記錄失敗原因
- 在 Sheets 中標記為「圖片下載失敗」
- 記錄 Message ID 供後續手動處理

### R-003: 圖片過大超過 Google Sheets 限制
**風險**: 壓縮後圖片仍超過 50,000 字元限制
**影響**: 無法內嵌圖片
**緩解**:
- 實作多層級壓縮（降低解析度直到符合限制）
- 如仍超過限制，記錄「圖片過大」訊息
- 記錄原始圖片資訊供參考

### R-004: Webhook 處理超過 3 秒
**風險**: 圖片處理或 Sheets API 呼叫耗時過長
**影響**: LINE 平台判定 Webhook 失敗
**緩解**:
- 優化圖片處理流程（使用高效壓縮參數）
- 監控處理時間，超過 2 秒發出警告
- 必要時改用非同步處理（Phase 2 優化）

---

## 下一步行動

1. ✅ 完成技術規劃（本文件）
2. ⏭️ 進行技術研究（產出 `research.md`）
3. ⏭️ 定義資料模型（產出 `data-model.md`）
4. ⏭️ 定義 API 合約（產出 `api-contracts.md`）
5. ⏭️ 生成實作任務（執行 `/speckit.tasks`）
6. ⏭️ 開始實作（執行 `/speckit.implement`）

---

**版本**: 1.0.0 | **最後更新**: 2025-11-15
