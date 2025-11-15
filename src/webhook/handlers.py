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
    from src.models.message import MessageRecord, MessageStatus
    from src.services.time_utils import convert_line_timestamp_to_taiwan, get_week_number, is_new_week
    from src.services.sheets_client import get_sheets_client

    logger.info("收到文字訊息")
    logger.debug(f"訊息內容: {event.message.text}")
    logger.debug(f"使用者 ID: {event.source.user_id}")
    logger.debug(f"時間戳記: {event.timestamp}")

    try:
        # 步驟 1: 過濾空訊息
        message_text = event.message.text.strip()
        if not message_text:
            logger.warning("收到空白訊息，已過濾")
            return

        # 步驟 2: 轉換時間為台灣時區
        taiwan_time = convert_line_timestamp_to_taiwan(event.timestamp)
        logger.debug(f"台灣時間: {taiwan_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 步驟 3: 建立 MessageRecord
        record = MessageRecord.create_text_message(
            timestamp=taiwan_time,
            text=message_text,
            user_id=event.source.user_id
        )
        logger.debug(f"建立 MessageRecord: {record}")

        # 步驟 4: 取得 Google Sheets 客戶端
        sheets_client = get_sheets_client()
        sheets_client.connect()

        # 步驟 5: 取得或建立月份工作表
        month_title = taiwan_time.strftime("%Y-%m")
        worksheet = sheets_client.get_worksheet(month_title)

        if worksheet is None:
            logger.info(f"工作表 '{month_title}' 不存在，建立新工作表")
            worksheet = sheets_client.create_worksheet(month_title, rows=1000, cols=3)

            # 寫入表頭
            worksheet.append_row(['時間', '類型', '內容'])
            logger.info(f"已建立工作表 '{month_title}' 並寫入表頭")

        # 步驟 6: 檢查是否需要插入週分隔線
        all_values = worksheet.get_all_values()
        if len(all_values) > 1:  # 有資料（不只表頭）
            # 取得最後一筆訊息的時間
            last_row = all_values[-1]
            if last_row and last_row[0]:  # 確保有時間欄位
                try:
                    from datetime import datetime
                    from src.services.time_utils import TAIWAN_TZ

                    # 解析最後一筆訊息的時間
                    last_time_str = last_row[0]
                    last_time = TAIWAN_TZ.localize(
                        datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
                    )

                    # 檢查是否跨週
                    if is_new_week(taiwan_time, last_time):
                        week_num = get_week_number(taiwan_time)
                        separator = f"--- 第 {week_num} 週 ---"
                        worksheet.append_row([separator, '', ''])
                        logger.info(f"插入週分隔線: {separator}")

                except Exception as e:
                    logger.warning(f"解析最後訊息時間時發生錯誤: {e}")

        # 步驟 7: 寫入訊息到 Google Sheets
        row = record.to_sheet_row()
        worksheet.append_row(row)
        logger.info(f"成功寫入訊息到 Google Sheets: {month_title}")

        # 更新狀態為成功
        record.status = MessageStatus.SUCCESS
        logger.info("文字訊息處理完成")

    except Exception as e:
        logger.error(f"處理文字訊息時發生錯誤: {e}", exc_info=True)
        # 不拋出異常，避免影響 LINE webhook 回應
        # LINE 期望收到 200 OK，否則會重複發送


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
