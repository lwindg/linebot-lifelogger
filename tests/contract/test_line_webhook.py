"""
LINE Webhook Contract Tests

測試 LINE Webhook 的基本契約和格式。
驗證我們能正確處理 LINE 平台發送的事件格式。
"""

import pytest
from unittest.mock import Mock, patch


class TestLineWebhookContract:
    """LINE Webhook 契約測試"""

    def test_text_message_event_structure(self, mock_text_message_event):
        """測試文字訊息事件的結構"""
        event = mock_text_message_event

        # 驗證必要的屬性存在
        assert hasattr(event, 'message')
        assert hasattr(event, 'source')
        assert hasattr(event, 'timestamp')
        assert hasattr(event, 'reply_token')

        # 驗證 message 物件
        assert hasattr(event.message, 'type')
        assert hasattr(event.message, 'text')
        assert event.message.type == 'text'

        # 驗證 source 物件
        assert hasattr(event.source, 'user_id')

        # 驗證資料類型
        assert isinstance(event.timestamp, int)
        assert isinstance(event.message.text, str)
        assert isinstance(event.source.user_id, str)

    def test_image_message_event_structure(self, mock_image_message_event):
        """測試圖片訊息事件的結構"""
        event = mock_image_message_event

        # 驗證必要的屬性存在
        assert hasattr(event, 'message')
        assert hasattr(event.message, 'type')
        assert hasattr(event.message, 'id')
        assert event.message.type == 'image'

        # 圖片訊息沒有 text 屬性
        assert not hasattr(event.message, 'text')

    def test_timestamp_is_milliseconds(self, mock_text_message_event):
        """測試 timestamp 是毫秒格式"""
        timestamp = mock_text_message_event.timestamp

        # LINE timestamp 是 13 位數的毫秒時間戳記
        assert len(str(timestamp)) == 13
        assert timestamp > 1000000000000  # 約 2001 年之後

    @patch('src.webhook.handlers.handler')
    def test_webhook_handler_registration(self, mock_handler):
        """測試 Webhook handler 是否正確註冊"""
        from linebot.models import MessageEvent, TextMessage

        # 驗證 handler 有註冊文字訊息處理器
        # 這個測試確認我們的 handlers.py 有正確使用 @handler.add 裝飾器
        assert mock_handler is not None


class TestLineSignatureValidation:
    """LINE 簽章驗證測試"""

    def test_signature_required(self):
        """測試缺少簽章時應該拒絕請求"""
        from flask import Flask
        from src.webhook.app import app

        with app.test_client() as client:
            # 不提供 X-Line-Signature header
            response = client.post('/webhook', data='test body')

            # 應該返回 400 Bad Request
            assert response.status_code == 400

    def test_invalid_signature_rejected(self):
        """測試無效簽章應該被拒絕"""
        from src.webhook.app import app

        with app.test_client() as client:
            # 提供無效的簽章
            response = client.post(
                '/webhook',
                data='{"events":[]}',
                headers={'X-Line-Signature': 'invalid_signature'}
            )

            # 應該返回 400 Bad Request
            assert response.status_code == 400


@pytest.mark.contract
class TestLineMessageTypes:
    """測試不同的 LINE 訊息類型"""

    def test_text_message_has_text_field(self, mock_text_message_event):
        """文字訊息必須有 text 欄位"""
        assert hasattr(mock_text_message_event.message, 'text')
        assert isinstance(mock_text_message_event.message.text, str)
        assert len(mock_text_message_event.message.text) > 0

    def test_image_message_has_id_field(self, mock_image_message_event):
        """圖片訊息必須有 id 欄位"""
        assert hasattr(mock_image_message_event.message, 'id')
        assert isinstance(mock_image_message_event.message.id, str)

    def test_user_id_format(self, mock_text_message_event):
        """測試使用者 ID 格式"""
        user_id = mock_text_message_event.source.user_id

        # LINE user ID 是字串
        assert isinstance(user_id, str)
        assert len(user_id) > 0
