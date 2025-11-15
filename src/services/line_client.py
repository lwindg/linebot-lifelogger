"""
LINE Bot Client

提供 LINE Messaging API 的封裝，處理訊息接收和回應。
"""

import logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import LineBotApiError

from src.config import Config

logger = logging.getLogger(__name__)


class LineClient:
    """LINE Bot 客戶端類別"""

    def __init__(self):
        """初始化 LINE Bot 客戶端"""
        self.channel_access_token = Config.LINE_CHANNEL_ACCESS_TOKEN
        self.channel_secret = Config.LINE_CHANNEL_SECRET

        if not self.channel_access_token or not self.channel_secret:
            logger.warning("LINE Bot 憑證未設定")
            self.line_bot_api = None
            self.handler = None
        else:
            self.line_bot_api = LineBotApi(self.channel_access_token)
            self.handler = WebhookHandler(self.channel_secret)
            logger.info("LINE Bot 客戶端初始化完成")

    def get_api(self) -> LineBotApi:
        """
        取得 LINE Bot API 實例

        Returns:
            LineBotApi: LINE Bot API 物件
        """
        return self.line_bot_api

    def get_handler(self) -> WebhookHandler:
        """
        取得 Webhook Handler 實例

        Returns:
            WebhookHandler: Webhook Handler 物件
        """
        return self.handler

    def download_message_content(self, message_id: str) -> bytes:
        """
        下載訊息內容（用於圖片、影片等）

        Args:
            message_id: 訊息 ID

        Returns:
            bytes: 訊息內容的二進位資料

        Raises:
            LineBotApiError: 下載失敗
        """
        try:
            logger.info(f"下載訊息內容: {message_id}")
            message_content = self.line_bot_api.get_message_content(message_id)

            # 將內容轉為 bytes
            content_bytes = b''
            for chunk in message_content.iter_content():
                content_bytes += chunk

            logger.info(f"成功下載訊息內容，大小: {len(content_bytes)} bytes")
            return content_bytes

        except LineBotApiError as e:
            logger.error(f"下載訊息內容失敗: {e}")
            raise

    def reply_message(self, reply_token: str, text: str):
        """
        回覆訊息給使用者

        Args:
            reply_token: 回覆 token
            text: 回覆的文字內容

        Raises:
            LineBotApiError: 回覆失敗
        """
        from linebot.models import TextSendMessage

        try:
            self.line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=text)
            )
            logger.info(f"成功回覆訊息: {text}")

        except LineBotApiError as e:
            logger.error(f"回覆訊息失敗: {e}")
            raise


# 建立全域的 LineClient 實例
_line_client = None


def get_line_client() -> LineClient:
    """
    取得 LINE 客戶端單例

    Returns:
        LineClient: LINE 客戶端實例
    """
    global _line_client
    if _line_client is None:
        _line_client = LineClient()
    return _line_client
