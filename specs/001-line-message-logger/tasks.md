# Tasks: LINE 訊息記錄器

**Input**: Design documents from `/specs/001-line-message-logger/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅

**Tests**: 包含整合測試任務（符合憲章：透過測試確保品質）

**Organization**: 任務按使用者故事分組，確保每個故事可獨立實作和測試

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可平行執行（不同檔案，無依賴）
- **[Story]**: 任務所屬的使用者故事（US1, US2, US3, US4, US5）
- 包含明確的檔案路徑

---

## Phase 1: Setup（專案初始化）

**Purpose**: 建立專案結構和基礎配置

- [ ] T001 建立專案目錄結構（src/, tests/, specs/）
- [ ] T002 [P] 初始化 Python 專案，建立 requirements.txt
- [ ] T003 [P] 建立 .env.example 環境變數範本檔案
- [ ] T004 [P] 建立 .gitignore（排除 .env, __pycache__, *.pyc）
- [ ] T005 [P] 建立 README.md 基礎說明文件
- [ ] T006 安裝核心依賴套件（Flask, line-bot-sdk, gspread, google-auth, Pillow, pytz）

**Checkpoint**: 專案結構完成，可以開始開發

---

## Phase 2: Foundational（核心基礎設施）

**Purpose**: 核心基礎設施，所有使用者故事都依賴這些元件

**⚠️ CRITICAL**: 此階段必須完成後才能開始任何使用者故事

- [ ] T007 [P] 建立 src/config.py 配置管理模組（讀取環境變數）
- [ ] T008 [P] 建立 src/services/time_utils.py 時區轉換工具（台灣時區 UTC+8）
- [ ] T009 [P] 建立 src/models/message.py 訊息資料類別
- [ ] T010 建立 src/services/sheets_client.py Google Sheets 客戶端（gspread 初始化）
- [ ] T011 建立 src/services/line_client.py LINE API 客戶端（LineBotApi 初始化）
- [ ] T012 建立 src/webhook/app.py Flask 應用程式主檔（基本路由設定）
- [ ] T013 建立 src/webhook/handlers.py LINE Webhook 處理器框架
- [ ] T014 實作簽章驗證（src/webhook/app.py 中的 webhook 端點）
- [ ] T015 設定 Python logging 日誌系統（src/config.py）
- [ ] T016 建立錯誤處理機制（src/webhook/app.py 錯誤處理器）

**測試基礎設施**:
- [ ] T017 [P] 設定 pytest 配置檔（pytest.ini 或 pyproject.toml）
- [ ] T018 [P] 建立測試固件（tests/conftest.py）

**Checkpoint**: 基礎設施完成，使用者故事實作可以開始平行進行

---

## Phase 3: User Story 1 - 記錄 LINE 文字訊息 (Priority: P1) 🎯 MVP

**Goal**: 接收 LINE 文字訊息，記錄時間和內容到 Google Sheets

**Independent Test**: 傳送文字訊息給 LINE Bot，檢查 Google Sheets 是否正確記錄時間和內容

### 測試（寫在實作之前，確保測試先失敗）

- [ ] T019 [P] [US1] 建立 LINE Webhook 契約測試（tests/contract/test_line_webhook.py）
- [ ] T020 [P] [US1] 建立 Google Sheets 契約測試（tests/contract/test_sheets_api.py）
- [ ] T021 [US1] 建立文字訊息記錄整合測試（tests/integration/test_text_message_flow.py）

### 實作

- [ ] T022 [P] [US1] 實作時間戳記轉換函式（src/services/time_utils.py）
  - 從 LINE timestamp (ms) 轉為台灣時區 datetime
  - 格式化為 "YYYY-MM-DD HH:MM:SS"
- [ ] T023 [P] [US1] 實作 Sheets 基本操作（src/services/sheets_client.py）
  - 開啟試算表
  - 取得工作表
  - 新增列
- [ ] T024 [US1] 實作文字訊息處理器（src/webhook/handlers.py）
  - handle_text_message() 函式
  - 提取訊息文字和時間
  - 呼叫 Sheets 客戶端記錄
- [ ] T025 [US1] 整合文字訊息處理到 Webhook（src/webhook/app.py）
  - 註冊 TextMessage 處理器
  - 確保 3 秒內回應
- [ ] T026 [US1] 實作空訊息過濾邏輯（src/webhook/handlers.py）
  - 忽略空白或僅含空格的訊息
- [ ] T027 [US1] 實作錯誤日誌記錄（src/webhook/handlers.py）
  - 記錄處理失敗的訊息
  - 包含時間、內容、錯誤原因

**Checkpoint**: 此時文字訊息記錄功能應完整可用並可獨立測試

---

## Phase 4: User Story 2 - 記錄 LINE 圖片/照片訊息 (Priority: P1) 🎯 MVP

**Goal**: 接收 LINE 圖片訊息，下載、壓縮、上傳到 Drive，並內嵌到 Google Sheets

**Independent Test**: 上傳圖片給 LINE Bot，檢查 Google Sheets 是否顯示內嵌圖片

### 測試（寫在實作之前）

- [ ] T028 [P] [US2] 建立 Google Drive 契約測試（tests/contract/test_drive_api.py）
- [ ] T029 [US2] 建立圖片訊息記錄整合測試（tests/integration/test_image_message_flow.py）
- [ ] T030 [P] [US2] 建立圖片處理單元測試（tests/unit/test_image_processor.py）

### 實作

- [ ] T031 [P] [US2] 建立 src/services/image_processor.py 圖片處理模組
  - compress_image() 多層級壓縮函式
  - 支援 JPEG, PNG 格式轉換
  - 處理透明度（PNG → JPEG 白底）
- [ ] T032 [P] [US2] 建立 src/services/drive_client.py Google Drive 客戶端
  - 初始化 Drive API
  - 建立/取得圖片儲存資料夾
  - upload_image() 上傳圖片函式
  - 設定檔案公開權限
  - 取得可存取的 URL
- [ ] T033 [US2] 實作圖片下載函式（src/services/line_client.py）
  - download_image_content() 使用 Message Content API
  - 錯誤處理（下載失敗）
- [ ] T034 [US2] 實作圖片訊息處理器（src/webhook/handlers.py）
  - handle_image_message() 函式
  - 下載圖片 → 壓縮 → 上傳 Drive → 取得 URL
  - 建立 IMAGE 公式
  - 呼叫 Sheets 客戶端記錄
- [ ] T035 [US2] 整合圖片訊息處理到 Webhook（src/webhook/app.py）
  - 註冊 ImageMessage 處理器
- [ ] T036 [US2] 實作圖片錯誤處理（src/webhook/handlers.py）
  - 下載失敗 → 記錄 "[圖片下載失敗]"
  - 壓縮後仍過大 → 記錄 "[圖片過大，無法嵌入]"
  - 詳細錯誤日誌
- [ ] T037 [US2] 實作不支援訊息類型處理（src/webhook/handlers.py）
  - handle_unsupported_message() 函式
  - 貼圖、影片、音訊等 → 記錄 "[不支援的訊息類型]"

**Checkpoint**: 此時文字和圖片訊息記錄功能都應完整可用

---

## Phase 5: User Story 3 - 月份子表單自動建立 (Priority: P2)

**Goal**: 自動依照月份建立 Google Sheets 子表單

**Independent Test**: 在不同月份傳送訊息，檢查是否自動建立新的月份子表單

### 測試

- [ ] T038 [US3] 建立月份子表單管理整合測試（tests/integration/test_monthly_sheets.py）
  - 測試跨月份記錄
  - 測試子表單自動建立

### 實作

- [ ] T039 [US3] 實作月份識別函式（src/services/time_utils.py）
  - get_month_key() 從 datetime 取得 "YYYY-MM" 格式
- [ ] T040 [US3] 實作工作表管理（src/services/sheets_client.py）
  - get_or_create_worksheet() 取得或建立月份工作表
  - 檢查工作表是否存在
  - 建立新工作表時寫入表頭（時間、類型、內容）
- [ ] T041 [US3] 實作表頭格式化（src/services/sheets_client.py）
  - 設定表頭粗體、背景色 (#F3F3F3)
  - 凍結第一列
- [ ] T042 [US3] 整合月份子表單到訊息處理（src/webhook/handlers.py）
  - 在記錄前先取得/建立對應月份工作表
  - 更新 handle_text_message() 和 handle_image_message()
- [ ] T043 [US3] 實作月份表單命名衝突檢查（src/services/sheets_client.py）
  - 確保不會建立重複的子表單

**Checkpoint**: 此時系統應能自動管理月份子表單

---

## Phase 6: User Story 4 - 週分界標記 (Priority: P2)

**Goal**: 在月份子表單中自動插入週分界標記（週日為起始日）

**Independent Test**: 跨週傳送訊息，檢查週日前是否有週分界標記

### 測試

- [ ] T044 [P] [US4] 建立週計算單元測試（tests/unit/test_time_utils.py）
  - 測試週次計算（週日為起始日）
  - 測試跨週判斷
- [ ] T045 [US4] 建立週分界標記整合測試（tests/integration/test_week_separators.py）

### 實作

- [ ] T046 [P] [US4] 實作週計算函式（src/services/time_utils.py）
  - get_week_number() 計算週次（週日為起始日）
  - is_new_week() 判斷是否跨週
- [ ] T047 [US4] 實作週分界標記插入（src/services/sheets_client.py）
  - should_insert_week_separator() 判斷邏輯
  - insert_week_separator() 插入週分界列
  - 格式化週分界列（合併儲存格、背景色 #E3F2FD、粗體）
- [ ] T048 [US4] 整合週分界標記到訊息記錄（src/webhook/handlers.py）
  - 記錄訊息前檢查是否需要插入週分界
  - 更新 handle_text_message() 和 handle_image_message()
- [ ] T049 [US4] 實作週分界標記格式化（src/services/sheets_client.py）
  - 使用 Google Sheets API 設定格式
  - 背景色、粗體、置中對齊

**Checkpoint**: 此時系統應能自動插入週分界標記

---

## Phase 7: User Story 5 - LINE Bot 回應確認 (Priority: P3)

**Goal**: Bot 回覆確認訊息，讓使用者知道訊息已記錄

**Independent Test**: 傳送訊息，檢查是否收到「已記錄 ✓」回覆

### 測試

- [ ] T050 [US5] 建立 Bot 回應整合測試（tests/integration/test_bot_replies.py）
  - 測試成功記錄回應
  - 測試錯誤回應

### 實作

- [ ] T051 [P] [US5] 實作成功回應（src/webhook/handlers.py）
  - 文字訊息記錄成功後回覆「已記錄 ✓」
  - 圖片訊息記錄成功後回覆「已記錄 ✓」
- [ ] T052 [P] [US5] 實作錯誤回應（src/webhook/handlers.py）
  - 記錄失敗時回覆「記錄失敗，請稍後再試」
- [ ] T053 [US5] 確保回應時間在 3 秒內（src/webhook/handlers.py）
  - 在處理完成後立即回應
  - 監控處理時間

**Checkpoint**: 所有使用者故事都已完成且可獨立運作

---

## Phase 8: Polish & Cross-Cutting Concerns（優化和跨功能關注點）

**Purpose**: 影響多個使用者故事的改進

- [ ] T054 [P] 建立 Dockerfile 容器化配置
- [ ] T055 [P] 建立 docker-compose.yml（包含環境變數設定）
- [ ] T056 [P] 更新 README.md 完整說明文件
  - 環境變數設定說明
  - Google Service Account 憑證設定
  - LINE Bot 設定步驟
  - 本地開發指南
  - 部署指南
- [ ] T057 [P] 建立環境變數檢查腳本（檢查必要配置是否完整）
- [ ] T058 實作效能監控（記錄處理時間，超過 2.5 秒發出警告）
- [ ] T059 [P] 程式碼重構和清理
  - 移除重複程式碼
  - 改善命名
  - 新增註解
- [ ] T060 [P] 安全性加固
  - 確認無硬編碼憑證
  - 檢查敏感資訊不在日誌中
- [ ] T061 整合測試端到端驗證
  - 執行所有整合測試
  - 確認所有使用者故事功能正常

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 無依賴 - 可立即開始
- **Foundational (Phase 2)**: 依賴 Setup 完成 - **阻塞所有使用者故事**
- **User Stories (Phase 3-7)**: 都依賴 Foundational 完成
  - US1 和 US2 是 P1（MVP）- 優先完成
  - US3 和 US4 是 P2 - 在 MVP 驗證後進行
  - US5 是 P3 - 最後完成
- **Polish (Phase 8)**: 依賴所有需要的使用者故事完成

### User Story Dependencies

- **US1 (P1)**: Foundational 完成後可開始 - 無其他故事依賴
- **US2 (P1)**: Foundational 完成後可開始 - 無其他故事依賴
- **US3 (P2)**: 依賴 US1 和 US2 - 需要整合月份子表單管理
- **US4 (P2)**: 依賴 US3 - 需要在月份子表單中插入週分界
- **US5 (P3)**: 可獨立開發 - 但建議在所有核心功能完成後再加入

### Within Each User Story

- 測試必須先寫並確認失敗
- Models → Services → Handlers → Integration
- 核心實作完成後再加入錯誤處理
- 故事完成後再進入下一優先級

### Parallel Opportunities

- Phase 1: T002, T003, T004, T005 可平行執行
- Phase 2: T007, T008, T009 可平行執行；T017, T018 可平行執行
- US1 測試: T019, T020 可平行執行
- US1 實作: T022, T023 可平行執行
- US2 測試: T028, T030 可平行執行
- US2 實作: T031, T032 可平行執行
- US4 測試: T044 可平行執行
- US5 實作: T051, T052 可平行執行
- Phase 8: T054, T055, T056, T057, T059, T060 可平行執行

---

## Implementation Strategy

### MVP First（只實作 US1 和 US2）

1. ✅ 完成 Phase 1: Setup
2. ✅ 完成 Phase 2: Foundational（關鍵 - 阻塞所有故事）
3. ✅ 完成 Phase 3: User Story 1（文字訊息）
4. ✅ 完成 Phase 4: User Story 2（圖片訊息）
5. **STOP and VALIDATE**: 獨立測試 US1 和 US2
6. 部署/展示 MVP

### Incremental Delivery（漸進式交付）

1. Setup + Foundational → 基礎就緒
2. 加入 US1 → 獨立測試 → 部署/展示（MVP 部分功能！）
3. 加入 US2 → 獨立測試 → 部署/展示（MVP 完整！）
4. 加入 US3 → 獨立測試 → 部署/展示（月份管理優化）
5. 加入 US4 → 獨立測試 → 部署/展示（週分界優化）
6. 加入 US5 → 獨立測試 → 部署/展示（Bot 回應確認）
7. 每個故事都增加價值而不破壞先前功能

### Parallel Team Strategy（團隊平行策略）

如果有多個開發者：

1. 團隊一起完成 Setup + Foundational
2. Foundational 完成後：
   - 開發者 A: US1（文字訊息）
   - 開發者 B: US2（圖片訊息）
   - 開發者 C: US3（月份子表單）- 等待 A, B 完成
3. 故事獨立完成並整合

---

## Task Count Summary

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 12 tasks
- **Phase 3 (US1 - P1 MVP)**: 9 tasks（3 測試 + 6 實作）
- **Phase 4 (US2 - P1 MVP)**: 10 tasks（3 測試 + 7 實作）
- **Phase 5 (US3 - P2)**: 6 tasks（1 測試 + 5 實作）
- **Phase 6 (US4 - P2)**: 6 tasks（2 測試 + 4 實作）
- **Phase 7 (US5 - P3)**: 4 tasks（1 測試 + 3 實作）
- **Phase 8 (Polish)**: 8 tasks

**Total**: 61 tasks

**MVP Minimum**: Phase 1 + Phase 2 + Phase 3 + Phase 4 = **37 tasks**

---

## Notes

- `[P]` 任務 = 不同檔案，無依賴，可平行執行
- `[Story]` 標籤將任務映射到特定使用者故事，便於追蹤
- 每個使用者故事都應可獨立完成和測試
- 在實作前確認測試失敗
- 每個任務或邏輯群組完成後提交
- 在任何檢查點停下來獨立驗證故事
- 避免：模糊任務、相同檔案衝突、破壞獨立性的跨故事依賴

---

**版本**: 1.0.0
**建立日期**: 2025-11-15
**下一步**: 執行 `/speckit.implement` 開始實作
