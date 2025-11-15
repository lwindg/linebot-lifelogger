"""
Pytest Fixtures and Configuration

提供測試固件（fixtures）供所有測試使用。
"""

import pytest
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock

# 設定測試環境變數
os.environ['FLASK_ENV'] = 'testing'
os.environ['LOG_LEVEL'] = 'DEBUG'


@pytest.fixture
def mock_line_event():
    """
    模擬 LINE MessageEvent 的 fixture

    Returns:
        Mock: 模擬的 LINE event 物件
    """
    event = Mock()
    event.message = Mock()
    event.message.id = 'test_message_id_12345'
    event.message.text = '測試訊息'
    event.source = Mock()
    event.source.user_id = 'test_user_id'
    event.timestamp = 1700000000000  # 2023-11-14 22:13:20 UTC
    event.reply_token = 'test_reply_token'

    return event


@pytest.fixture
def mock_text_message_event(mock_line_event):
    """
    模擬文字訊息事件的 fixture

    Returns:
        Mock: 模擬的文字訊息 event
    """
    mock_line_event.message.type = 'text'
    mock_line_event.message.text = 'Hello, 測試訊息！'
    return mock_line_event


@pytest.fixture
def mock_image_message_event(mock_line_event):
    """
    模擬圖片訊息事件的 fixture

    Returns:
        Mock: 模擬的圖片訊息 event
    """
    mock_line_event.message.type = 'image'
    mock_line_event.message.id = 'test_image_message_id'
    delattr(mock_line_event.message, 'text')  # 圖片訊息沒有 text 屬性
    return mock_line_event


@pytest.fixture
def sample_taiwan_datetime():
    """
    範例台灣時區 datetime 的 fixture

    Returns:
        datetime: 台灣時區的 datetime 物件
    """
    import pytz
    from datetime import datetime

    taiwan_tz = pytz.timezone('Asia/Taipei')
    return taiwan_tz.localize(datetime(2025, 11, 15, 14, 30, 0))


@pytest.fixture
def mock_sheets_client():
    """
    模擬 Google Sheets 客戶端的 fixture

    Returns:
        Mock: 模擬的 SheetsClient
    """
    client = MagicMock()
    client.get_spreadsheet = MagicMock()
    client.get_worksheet = MagicMock()
    client.create_worksheet = MagicMock()
    client.append_row = MagicMock()
    client.get_all_values = MagicMock(return_value=[])

    return client


@pytest.fixture
def mock_line_bot_api():
    """
    模擬 LINE Bot API 的 fixture

    Returns:
        Mock: 模擬的 LineBotApi
    """
    api = MagicMock()
    api.get_message_content = MagicMock()
    api.reply_message = MagicMock()

    return api


@pytest.fixture
def sample_image_bytes():
    """
    範例圖片二進位資料的 fixture

    Returns:
        bytes: 簡單的測試圖片資料
    """
    # 這是一個 1x1 的紅色 PNG 圖片
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'


@pytest.fixture
def clean_test_env(monkeypatch):
    """
    清理測試環境變數的 fixture

    Args:
        monkeypatch: pytest 的 monkeypatch fixture
    """
    # 設定測試用的環境變數
    monkeypatch.setenv('SPREADSHEET_ID', 'test_spreadsheet_id')
    monkeypatch.setenv('DRIVE_FOLDER_ID', 'test_drive_folder_id')
    monkeypatch.setenv('LINE_CHANNEL_ACCESS_TOKEN', 'test_access_token')
    monkeypatch.setenv('LINE_CHANNEL_SECRET', 'test_channel_secret')
    monkeypatch.setenv('GOOGLE_CREDENTIALS_FILE', 'test_service_account.json')

    yield

    # 測試後清理（pytest 會自動處理）
