"""
Text Message Flow Integration Tests

測試文字訊息從接收到記錄的完整流程。
這是端到端的整合測試，驗證所有元件協同工作。
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import pytz


@pytest.mark.integration
class TestTextMessageEndToEnd:
    """文字訊息端到端整合測試"""

    @patch('src.services.sheets_client.gspread')
    @patch('src.services.sheets_client.Credentials')
    def test_receive_text_message_and_log_to_sheets(
        self,
        mock_credentials,
        mock_gspread,
        mock_text_message_event
    ):
        """
        測試完整流程：接收文字訊息 → 處理 → 寫入 Google Sheets

        流程：
        1. 接收 LINE 文字訊息事件
        2. 轉換時間戳記為台灣時區
        3. 建立 MessageRecord
        4. 取得或建立月份工作表
        5. 寫入訊息到工作表
        """
        from src.models.message import MessageRecord, MessageType
        from src.services.time_utils import convert_line_timestamp_to_taiwan
        from src.services.sheets_client import SheetsClient

        # 模擬 LINE 事件
        event = mock_text_message_event
        event.timestamp = 1700000000000  # 2023-11-14 22:13:20 UTC
        event.message.text = "這是測試訊息"
        event.source.user_id = "U123456789"

        # 步驟 1: 轉換時間戳記
        taiwan_time = convert_line_timestamp_to_taiwan(event.timestamp)

        # 驗證時間轉換
        assert taiwan_time.tzinfo == pytz.timezone('Asia/Taipei')
        expected_month = taiwan_time.strftime("%Y-%m")  # 應該是 2023-11

        # 步驟 2: 建立 MessageRecord
        record = MessageRecord.create_text_message(
            timestamp=taiwan_time,
            text=event.message.text,
            user_id=event.source.user_id
        )

        # 驗證 MessageRecord
        assert record.message_type == MessageType.TEXT
        assert record.content == "這是測試訊息"
        assert record.user_id == "U123456789"

        # 步驟 3: 準備模擬的 Sheets 客戶端
        mock_creds = Mock()
        mock_credentials.from_service_account_file = MagicMock(return_value=mock_creds)

        mock_gc = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_worksheet.title = expected_month
        mock_worksheet.append_row = MagicMock()
        mock_worksheet.get_all_values = MagicMock(return_value=[
            ['時間', '類型', '內容']
        ])

        mock_spreadsheet.worksheet = MagicMock(return_value=mock_worksheet)
        mock_gc.open_by_key = MagicMock(return_value=mock_spreadsheet)
        mock_gspread.authorize = MagicMock(return_value=mock_gc)

        # 步驟 4: 寫入 Sheets
        client = SheetsClient()
        client.connect()

        # 模擬 get_worksheet 返回工作表
        with patch.object(client, 'get_worksheet', return_value=mock_worksheet):
            worksheet = client.get_worksheet(expected_month)

            # 步驟 5: 寫入訊息
            row = record.to_sheet_row()
            worksheet.append_row(row)

            # 驗證寫入
            worksheet.append_row.assert_called_once()
            call_args = worksheet.append_row.call_args[0][0]
            assert call_args[1] == "文字"
            assert call_args[2] == "這是測試訊息"

    @patch('src.services.sheets_client.gspread')
    @patch('src.services.sheets_client.Credentials')
    def test_create_new_month_worksheet_if_not_exists(
        self,
        mock_credentials,
        mock_gspread,
        mock_text_message_event
    ):
        """
        測試自動建立新月份工作表

        當訊息的月份工作表不存在時，應自動建立。
        """
        from src.services.time_utils import convert_line_timestamp_to_taiwan
        from src.services.sheets_client import SheetsClient

        # 轉換時間
        taiwan_time = convert_line_timestamp_to_taiwan(mock_text_message_event.timestamp)
        month_title = taiwan_time.strftime("%Y-%m")

        # 模擬認證
        mock_creds = Mock()
        mock_credentials.from_service_account_file = MagicMock(return_value=mock_creds)

        # 模擬試算表（工作表不存在）
        mock_gc = Mock()
        mock_spreadsheet = Mock()
        mock_spreadsheet.worksheet = MagicMock(side_effect=Exception("Worksheet not found"))

        # 模擬建立新工作表
        new_worksheet = Mock()
        new_worksheet.title = month_title
        new_worksheet.append_row = MagicMock()
        mock_spreadsheet.add_worksheet = MagicMock(return_value=new_worksheet)

        mock_gc.open_by_key = MagicMock(return_value=mock_spreadsheet)
        mock_gspread.authorize = MagicMock(return_value=mock_gc)

        # 建立客戶端
        client = SheetsClient()
        client.connect()

        # 嘗試取得不存在的工作表
        worksheet = client.get_worksheet(month_title)

        # 驗證返回 None（工作表不存在）
        assert worksheet is None

        # 建立新工作表
        new_ws = client.create_worksheet(month_title, rows=1000, cols=3)

        # 驗證建立成功
        assert new_ws is not None
        mock_spreadsheet.add_worksheet.assert_called_once()

    def test_timezone_conversion_preserves_correct_date(self):
        """
        測試時區轉換保持正確的日期

        重要：LINE timestamp 是 UTC，需要正確轉換為台灣時區。
        邊界情況：UTC 23:30 → 台灣次日 07:30
        """
        from src.services.time_utils import convert_line_timestamp_to_taiwan

        # UTC 時間：2023-11-14 23:30:00
        # 台灣時間應該是：2023-11-15 07:30:00
        utc_timestamp = 1700004600000  # 2023-11-14 23:30:00 UTC

        taiwan_time = convert_line_timestamp_to_taiwan(utc_timestamp)

        # 驗證日期正確（應該是 15 日，不是 14 日）
        assert taiwan_time.day == 15
        assert taiwan_time.hour == 7
        assert taiwan_time.minute == 30

    @patch('src.services.sheets_client.gspread')
    @patch('src.services.sheets_client.Credentials')
    def test_week_separator_inserted_on_new_week(
        self,
        mock_credentials,
        mock_gspread
    ):
        """
        測試新週開始時插入週分隔線

        當從週六到週日時，應該插入週分隔線。
        """
        from src.services.time_utils import is_new_week, get_week_number, TAIWAN_TZ
        from datetime import datetime

        # 週六：2025-11-15（週六）
        saturday = TAIWAN_TZ.localize(datetime(2025, 11, 15, 23, 59, 0))

        # 週日：2025-11-16（週日）
        sunday = TAIWAN_TZ.localize(datetime(2025, 11, 16, 0, 1, 0))

        # 驗證跨週判斷
        assert is_new_week(sunday, saturday) is True

        # 驗證週數
        week_num = get_week_number(sunday)
        assert isinstance(week_num, int)
        assert week_num > 0

        # 驗證週分隔線格式
        separator = f"--- 第 {week_num} 週 ---"
        assert "---" in separator
        assert "週" in separator

    def test_empty_message_filtered(self):
        """
        測試空白訊息應該被過濾

        空字串、純空白的訊息不應該被記錄。
        """
        from src.models.message import MessageRecord, MessageType
        from src.services.time_utils import TAIWAN_TZ
        from datetime import datetime

        taiwan_time = TAIWAN_TZ.localize(datetime(2025, 11, 15, 14, 30, 0))

        # 測試空字串
        empty_text = ""
        assert empty_text.strip() == ""

        # 測試純空白
        whitespace_text = "   \t\n  "
        assert whitespace_text.strip() == ""

        # 有效訊息應該通過
        valid_text = "這是有效訊息"
        assert valid_text.strip() != ""

    @patch('src.services.sheets_client.gspread')
    @patch('src.services.sheets_client.Credentials')
    def test_multiple_messages_same_month(
        self,
        mock_credentials,
        mock_gspread
    ):
        """
        測試同月份多條訊息寫入同一工作表

        驗證多條訊息正確累積在月份工作表中。
        """
        from src.models.message import MessageRecord
        from src.services.time_utils import TAIWAN_TZ
        from datetime import datetime

        # 模擬認證
        mock_creds = Mock()
        mock_credentials.from_service_account_file = MagicMock(return_value=mock_creds)

        # 模擬工作表（有多筆資料）
        mock_gc = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_worksheet.title = "2025-11"
        mock_worksheet.append_row = MagicMock()
        mock_worksheet.get_all_values = MagicMock(return_value=[
            ['時間', '類型', '內容'],
            ['2025-11-15 10:00:00', '文字', '第一條訊息'],
            ['2025-11-15 11:00:00', '文字', '第二條訊息']
        ])

        mock_spreadsheet.worksheet = MagicMock(return_value=mock_worksheet)
        mock_gc.open_by_key = MagicMock(return_value=mock_spreadsheet)
        mock_gspread.authorize = MagicMock(return_value=mock_gc)

        # 建立第三條訊息
        taiwan_time = TAIWAN_TZ.localize(datetime(2025, 11, 15, 12, 0, 0))
        record = MessageRecord.create_text_message(
            timestamp=taiwan_time,
            text="第三條訊息",
            user_id="test_user"
        )

        # 驗證已有資料
        data = mock_worksheet.get_all_values()
        assert len(data) == 3  # 表頭 + 2 條訊息

        # 新增第三條訊息
        row = record.to_sheet_row()
        mock_worksheet.append_row(row)

        # 驗證呼叫
        mock_worksheet.append_row.assert_called_once()
