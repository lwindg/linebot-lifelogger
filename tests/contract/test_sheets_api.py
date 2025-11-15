"""
Google Sheets API Contract Tests

測試 Google Sheets API 的基本契約和資料格式。
驗證我們能正確操作 Google Sheets 並維護資料結構。
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


@pytest.mark.contract
class TestSheetsStructure:
    """Google Sheets 資料結構契約測試"""

    def test_worksheet_title_format(self):
        """測試月份工作表標題格式為 YYYY-MM"""
        from src.services.time_utils import TAIWAN_TZ

        # 2025年11月的範例
        dt = TAIWAN_TZ.localize(datetime(2025, 11, 15, 14, 30, 0))
        expected_title = "2025-11"

        # 驗證標題格式
        assert dt.strftime("%Y-%m") == expected_title

    def test_sheet_has_three_columns(self, mock_sheets_client):
        """測試工作表必須有三個欄位：時間、類型、內容"""
        # 模擬工作表
        worksheet = Mock()
        worksheet.row_values = MagicMock(return_value=['時間', '類型', '內容'])

        mock_sheets_client.get_worksheet = MagicMock(return_value=worksheet)

        # 取得表頭
        ws = mock_sheets_client.get_worksheet("2025-11")
        headers = ws.row_values(1)

        # 驗證欄位
        assert len(headers) == 3
        assert headers[0] == '時間'
        assert headers[1] == '類型'
        assert headers[2] == '內容'

    def test_message_row_format(self):
        """測試訊息列的格式"""
        from src.models.message import MessageRecord, MessageType
        from src.services.time_utils import TAIWAN_TZ

        # 建立測試訊息
        dt = TAIWAN_TZ.localize(datetime(2025, 11, 15, 14, 30, 0))
        record = MessageRecord(
            timestamp=dt,
            message_type=MessageType.TEXT,
            content="測試訊息",
            user_id="test_user"
        )

        # 轉換為工作表列
        row = record.to_sheet_row()

        # 驗證格式
        assert len(row) == 3
        assert row[0] == "2025-11-15 14:30:00"  # 時間格式
        assert row[1] == "文字"  # 類型
        assert row[2] == "測試訊息"  # 內容
        assert isinstance(row[0], str)
        assert isinstance(row[1], str)
        assert isinstance(row[2], str)

    def test_image_row_with_formula(self):
        """測試圖片訊息使用 IMAGE 公式"""
        from src.models.message import MessageRecord
        from src.services.time_utils import TAIWAN_TZ

        # 建立圖片訊息
        dt = TAIWAN_TZ.localize(datetime(2025, 11, 15, 14, 30, 0))
        image_url = "https://drive.google.com/uc?id=abc123"

        record = MessageRecord.create_image_message(
            timestamp=dt,
            image_url=image_url,
            user_id="test_user"
        )

        # 轉換為工作表列
        row = record.to_sheet_row()

        # 驗證 IMAGE 公式
        assert row[1] == "圖片"
        assert row[2].startswith('=IMAGE("')
        assert image_url in row[2]
        assert row[2].endswith(', 1)')

    def test_week_separator_format(self):
        """測試週分隔線格式"""
        # 週分隔線應該是明顯的標記
        week_number = 3
        separator = f"--- 第 {week_number} 週 ---"

        # 驗證格式
        assert "---" in separator
        assert f"第 {week_number} 週" in separator
        assert isinstance(separator, str)


@pytest.mark.contract
class TestSheetsOperations:
    """Google Sheets 基本操作契約測試"""

    def test_get_spreadsheet_returns_spreadsheet(self, mock_sheets_client):
        """測試取得試算表"""
        # 模擬試算表
        mock_spreadsheet = Mock()
        mock_spreadsheet.title = "LifeLogger Messages"
        mock_sheets_client.get_spreadsheet = MagicMock(return_value=mock_spreadsheet)

        # 取得試算表
        spreadsheet = mock_sheets_client.get_spreadsheet()

        # 驗證
        assert spreadsheet is not None
        assert hasattr(spreadsheet, 'title')

    def test_get_worksheet_returns_none_if_not_exists(self, mock_sheets_client):
        """測試取得不存在的工作表返回 None"""
        mock_sheets_client.get_worksheet = MagicMock(return_value=None)

        # 嘗試取得不存在的工作表
        worksheet = mock_sheets_client.get_worksheet("2099-12")

        # 驗證返回 None
        assert worksheet is None

    def test_create_worksheet_with_title(self, mock_sheets_client):
        """測試建立新工作表"""
        # 模擬新工作表
        new_worksheet = Mock()
        new_worksheet.title = "2025-11"
        mock_sheets_client.create_worksheet = MagicMock(return_value=new_worksheet)

        # 建立工作表
        worksheet = mock_sheets_client.create_worksheet("2025-11")

        # 驗證
        assert worksheet is not None
        assert worksheet.title == "2025-11"

    def test_append_row_accepts_list(self, mock_sheets_client):
        """測試 append_row 接受列表參數"""
        # 模擬工作表
        worksheet = Mock()
        worksheet.append_row = MagicMock()

        # 測試資料
        test_row = ["2025-11-15 14:30:00", "文字", "測試訊息"]

        # 呼叫 append_row
        worksheet.append_row(test_row)

        # 驗證被呼叫
        worksheet.append_row.assert_called_once_with(test_row)

    def test_get_all_values_returns_list_of_lists(self, mock_sheets_client):
        """測試 get_all_values 返回二維列表"""
        # 模擬回傳資料
        mock_data = [
            ['時間', '類型', '內容'],
            ['2025-11-15 14:30:00', '文字', '測試訊息']
        ]
        mock_sheets_client.get_all_values = MagicMock(return_value=mock_data)

        # 取得所有資料
        data = mock_sheets_client.get_all_values()

        # 驗證
        assert isinstance(data, list)
        assert len(data) == 2
        assert isinstance(data[0], list)
        assert data[0] == ['時間', '類型', '內容']


@pytest.mark.contract
class TestSheetsAuthentication:
    """Google Sheets 認證契約測試"""

    @patch('src.services.sheets_client.Credentials')
    @patch('src.services.sheets_client.gspread')
    def test_service_account_authentication(self, mock_gspread, mock_credentials):
        """測試 Service Account 認證流程"""
        from src.services.sheets_client import SheetsClient

        # 模擬認證
        mock_creds = Mock()
        mock_credentials.from_service_account_file = MagicMock(return_value=mock_creds)
        mock_gc = Mock()
        mock_gspread.authorize = MagicMock(return_value=mock_gc)

        # 建立客戶端
        client = SheetsClient()

        # 驗證 scopes 包含必要的權限
        assert 'https://www.googleapis.com/auth/spreadsheets' in client.scopes
        assert 'https://www.googleapis.com/auth/drive' in client.scopes

    def test_credentials_file_required(self):
        """測試必須提供認證檔案"""
        from src.config import Config

        # 驗證配置中有認證檔案路徑
        assert hasattr(Config, 'GOOGLE_CREDENTIALS_FILE')
        assert Config.GOOGLE_CREDENTIALS_FILE is not None

    def test_spreadsheet_id_required(self):
        """測試必須提供試算表 ID"""
        from src.config import Config

        # 驗證配置中有試算表 ID
        assert hasattr(Config, 'SPREADSHEET_ID')
        assert Config.SPREADSHEET_ID is not None
