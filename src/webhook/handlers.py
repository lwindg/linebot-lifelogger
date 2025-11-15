"""
LINE Webhook Event Handlers

處理來自 LINE 的各種事件（訊息、加入好友等）。
"""

import logging
from linebot.models import MessageEvent, TextMessage, ImageMessage, StickerMessage, VideoMessage, AudioMessage

from src.services.line_client import get_line_client

logger = logging.getLogger(__name__)

# 取得 LINE 客戶端和 handler
line_client = get_line_client()
handler = line_client.get_handler()


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """
    處理文字訊息

    Args:
        event: LINE MessageEvent 物件
    """
    logger.info("收到文字訊息")
    logger.debug(f"訊息內容: {event.message.text}")
    logger.debug(f"使用者 ID: {event.source.user_id}")
    logger.debug(f"時間戳記: {event.timestamp}")

    # TODO: 實作文字訊息記錄邏輯（Phase 3）
    # 1. 轉換時間為台灣時區
    # 2. 建立 MessageRecord
    # 3. 寫入 Google Sheets

    logger.info("文字訊息處理完成（暫未實作記錄邏輯）")


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """
    處理圖片訊息

    Args:
        event: LINE MessageEvent 物件
    """
    logger.info("收到圖片訊息")
    logger.debug(f"訊息 ID: {event.message.id}")
    logger.debug(f"使用者 ID: {event.source.user_id}")
    logger.debug(f"時間戳記: {event.timestamp}")

    # TODO: 實作圖片訊息記錄邏輯（Phase 4）
    # 1. 下載圖片
    # 2. 壓縮圖片
    # 3. 上傳到 Google Drive
    # 4. 建立 IMAGE 公式
    # 5. 寫入 Google Sheets

    logger.info("圖片訊息處理完成（暫未實作記錄邏輯）")


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    """
    處理貼圖訊息（不支援類型）

    Args:
        event: LINE MessageEvent 物件
    """
    logger.info("收到貼圖訊息")
    logger.debug(f"Package ID: {event.message.package_id}")
    logger.debug(f"Sticker ID: {event.message.sticker_id}")

    # TODO: 實作不支援訊息類型記錄（Phase 4）
    # 記錄為 "[不支援的訊息類型: 貼圖]"

    logger.info("貼圖訊息處理完成（記錄為不支援類型）")


@handler.add(MessageEvent, message=VideoMessage)
def handle_video_message(event):
    """
    處理影片訊息（不支援類型）

    Args:
        event: LINE MessageEvent 物件
    """
    logger.info("收到影片訊息（不支援類型）")

    # TODO: 實作不支援訊息類型記錄（Phase 4）
    # 記錄為 "[不支援的訊息類型: 影片]"

    logger.info("影片訊息處理完成（記錄為不支援類型）")


@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    """
    處理音訊訊息（不支援類型）

    Args:
        event: LINE MessageEvent 物件
    """
    logger.info("收到音訊訊息（不支援類型）")

    # TODO: 實作不支援訊息類型記錄（Phase 4）
    # 記錄為 "[不支援的訊息類型: 音訊]"

    logger.info("音訊訊息處理完成（記錄為不支援類型）")
