# Feature Specification: LINE 訊息記錄器

**Feature Branch**: `001-line-message-logger`
**Created**: 2025-11-15
**Status**: Draft
**Input**: 透過 LINE 記錄每條訊息，貼圖時記下時間及圖；文字則記下時間及文字；以月為單位放在 Google Sheet 中，每個月個子表單，子表單中以週為單位做劃分

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 記錄 LINE 文字訊息 (Priority: P1)

使用者透過 LINE 傳送文字訊息給 Bot，系統自動將訊息內容和時間記錄到 Google Sheets。

**Why this priority**: 這是核心功能的基礎，提供最基本的訊息記錄能力，能夠讓使用者立即開始記錄生活日誌。

**Independent Test**: 可以透過傳送一則 LINE 文字訊息，然後檢查 Google Sheets 是否正確記錄時間和文字內容來獨立測試此功能。

**Acceptance Scenarios**:

1. **Given** 使用者已加入 LINE Bot 好友，**When** 使用者傳送文字訊息「今天天氣很好」，**Then** Google Sheets 中會新增一筆記錄，包含當前時間和訊息內容「今天天氣很好」
2. **Given** 使用者已加入 LINE Bot 好友，**When** 使用者在同一天傳送多則文字訊息，**Then** Google Sheets 中會依序記錄每則訊息及其對應時間
3. **Given** 使用者已加入 LINE Bot 好友，**When** 使用者傳送包含特殊字元（emoji、標點符號）的文字訊息，**Then** Google Sheets 正確記錄所有字元而不發生錯誤

---

### User Story 2 - 記錄 LINE 貼圖訊息 (Priority: P1)

使用者透過 LINE 傳送貼圖給 Bot，系統自動將貼圖資訊和時間記錄到 Google Sheets。

**Why this priority**: 貼圖是 LINE 的重要溝通方式，記錄貼圖能更完整地捕捉使用者的生活記錄和情緒狀態。

**Independent Test**: 可以透過傳送一個 LINE 貼圖，然後檢查 Google Sheets 是否正確記錄時間和貼圖資訊（如貼圖 ID 或描述）來獨立測試此功能。

**Acceptance Scenarios**:

1. **Given** 使用者已加入 LINE Bot 好友，**When** 使用者傳送一個貼圖，**Then** Google Sheets 中會新增一筆記錄，包含當前時間和貼圖識別資訊
2. **Given** 使用者已加入 LINE Bot 好友，**When** 使用者連續傳送多個不同貼圖，**Then** Google Sheets 中會依序記錄每個貼圖及其對應時間
3. **Given** 使用者已加入 LINE Bot 好友，**When** 使用者傳送官方貼圖或自訂貼圖，**Then** 系統都能正確識別並記錄

---

### User Story 3 - 月份子表單自動建立 (Priority: P2)

系統自動依照月份建立對應的 Google Sheets 子表單，將該月份的訊息記錄到對應的子表單中。

**Why this priority**: 以月份分類可以讓使用者更容易查找和管理歷史記錄，但不影響基本的記錄功能，因此為 P2 優先級。

**Independent Test**: 可以透過在不同月份傳送訊息，檢查是否自動建立新的月份子表單，並將訊息記錄到正確的月份表單來測試。

**Acceptance Scenarios**:

1. **Given** 使用者首次使用系統，**When** 使用者在 2025 年 11 月傳送第一則訊息，**Then** 系統自動建立名為「2025-11」的子表單並記錄訊息
2. **Given** 使用者在 11 月已有記錄，**When** 時間進入 12 月並傳送新訊息，**Then** 系統自動建立名為「2025-12」的新子表單並記錄 12 月的訊息
3. **Given** 某月份子表單已存在，**When** 使用者在該月份傳送新訊息，**Then** 系統將訊息新增到現有的月份子表單中，而不是建立重複表單

---

### User Story 4 - 週分界標記 (Priority: P2)

在月份子表單中，系統自動以視覺化方式標記週的分界，讓使用者能清楚區分不同週的記錄。

**Why this priority**: 週分界標記提升可讀性和使用體驗，但不影響核心記錄功能，屬於優化項目。

**Independent Test**: 可以透過檢視 Google Sheets 中跨越多週的記錄，確認是否有明顯的週分界標記（如空行、分隔線或週標題）來測試。

**Acceptance Scenarios**:

1. **Given** 使用者在同一個月內持續記錄，**When** 記錄跨越週界（週日到週一），**Then** Google Sheets 中會顯示明顯的週分界標記
2. **Given** 月份子表單中有多週記錄，**When** 使用者查看表單，**Then** 能夠清楚識別每一週的起始位置
3. **Given** 新的一週開始，**When** 使用者傳送該週的第一則訊息，**Then** 系統在記錄前自動插入週分界標記（如「第 N 週」或「Week N」）

---

### User Story 5 - LINE Bot 回應確認 (Priority: P3)

當使用者傳送訊息後，LINE Bot 回覆簡短確認訊息，讓使用者知道訊息已成功記錄。

**Why this priority**: 提供即時回饋改善使用者體驗，但對核心記錄功能非必要，可以在 MVP 驗證後再加入。

**Independent Test**: 可以透過傳送訊息並檢查是否收到 Bot 的確認回覆來測試。

**Acceptance Scenarios**:

1. **Given** 使用者已加入 LINE Bot 好友，**When** 使用者傳送文字訊息，**Then** Bot 在 3 秒內回覆「已記錄 ✓」
2. **Given** 使用者已加入 LINE Bot 好友，**When** 使用者傳送貼圖，**Then** Bot 在 3 秒內回覆「已記錄 ✓」
3. **Given** 系統發生錯誤無法記錄，**When** 使用者傳送訊息，**Then** Bot 回覆錯誤訊息如「記錄失敗，請稍後再試」

---

### Edge Cases

- **空訊息處理**: 當 LINE 傳送空白或僅包含空格的訊息時，系統如何處理？
- **訊息類型未支援**: 當使用者傳送圖片、影片、音訊等其他類型訊息時，系統如何處理？
- **Google Sheets API 限制**: 當達到 Google Sheets API 配額限制時，系統如何處理？
- **時區問題**: 系統記錄的時間是使用哪個時區？如何處理跨時區使用情境？
- **月份表單命名衝突**: 如何確保月份表單名稱不會與現有表單名稱衝突？
- **大量訊息湧入**: 當使用者短時間內傳送大量訊息時，系統能否正確依序記錄？
- **斷線重試**: 當與 Google Sheets 連線失敗時，系統是否有重試機制？

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統必須能接收並處理 LINE 文字訊息
- **FR-002**: 系統必須能接收並處理 LINE 貼圖訊息
- **FR-003**: 系統必須記錄每則訊息的接收時間（精確到秒）
- **FR-004**: 系統必須將文字訊息的完整內容儲存到 Google Sheets
- **FR-005**: 系統必須將貼圖的識別資訊（Package ID、Sticker ID）儲存到 Google Sheets
- **FR-006**: 系統必須能存取並寫入指定的 Google Sheets 試算表
- **FR-007**: 系統必須依照月份（YYYY-MM 格式）建立或選擇對應的子表單
- **FR-008**: 系統必須在子表單中以週為單位插入分界標記
- **FR-009**: 系統必須處理 LINE Webhook 事件並在 3 秒內回應（LINE 平台要求）
- **FR-010**: 系統必須安全地儲存 LINE Bot Token 和 Google Sheets 憑證（不可硬編碼）
- **FR-011**: 系統必須記錄所有錯誤和重要操作到日誌系統
- **FR-012**: 系統必須在訊息記錄失敗時保留訊息，以便後續重試 [NEEDS CLARIFICATION: 重試機制的具體實作方式]

### Key Entities

- **Message Record（訊息記錄）**:
  - 時間戳記（timestamp）：訊息接收的日期時間
  - 訊息類型（message_type）：文字或貼圖
  - 內容（content）：文字訊息的內容或貼圖的識別資訊
  - 使用者 ID（user_id）：LINE 使用者的唯一識別碼
  - 記錄狀態（status）：成功、失敗、待重試

- **Sheet Tab（子表單）**:
  - 月份標識（month_key）：YYYY-MM 格式
  - 建立時間（created_at）：子表單建立的時間
  - 記錄數量（record_count）：該月份的總記錄數

- **Week Separator（週分界）**:
  - 週次（week_number）：該年度的第幾週
  - 週起始日（week_start_date）：該週的第一天日期
  - 顯示文字（display_text）：在表單中顯示的週標記文字

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 使用者傳送訊息後，95% 的訊息能在 2 秒內成功記錄到 Google Sheets
- **SC-002**: 系統能正確識別並記錄至少 100 種不同的 LINE 貼圖
- **SC-003**: 月份子表單能自動建立，無需手動介入
- **SC-004**: 使用者能在 Google Sheets 中清楚辨識不同週的記錄，週分界標記清晰可見
- **SC-005**: 系統在連續 30 天運作期間，記錄準確率達到 99% 以上
- **SC-006**: LINE Webhook 回應時間保持在 3 秒以內，符合 LINE 平台要求
- **SC-007**: 系統能處理每日至少 1000 則訊息的記錄量，不發生遺失或錯誤
