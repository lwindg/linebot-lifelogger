#!/usr/bin/env python3
"""
本地測試腳本：測試圖片訊息記錄功能

此腳本模擬 LINE 圖片訊息事件，測試完整的圖片處理流程。

使用方法：
1. 確保已建立 .env 檔案並設定環境變數
2. 準備一張測試圖片（test_image.jpg）
3. 執行：python test_local_image_message.py
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定日誌
from src.config import setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)


class MockImageMessage:
    """模擬 LINE ImageMessage 物件"""
    def __init__(self, message_id):
        self.type = 'image'
        self.id = message_id


class MockSource:
    """模擬 LINE Source 物件"""
    def __init__(self, user_id):
        self.type = 'user'
        self.user_id = user_id


class MockMessageEvent:
    """模擬 LINE MessageEvent 物件"""
    def __init__(self, message_id, user_id, timestamp=None):
        self.type = 'message'
        self.message = MockImageMessage(message_id)
        self.source = MockSource(user_id)
        self.timestamp = timestamp if timestamp else int(datetime.now().timestamp() * 1000)
        self.reply_token = 'mock_reply_token_12345'


def verify_env():
    """驗證環境變數是否已設定"""
    from src.config import Config

    logger.info("=" * 60)
    logger.info("檢查環境變數設定...")
    logger.info("=" * 60)

    is_valid, missing = Config.validate()

    if not is_valid:
        logger.error(f"❌ 缺少必要的環境變數: {', '.join(missing)}")
        return False

    logger.info("✅ 必要環境變數已設定")
    logger.info("")

    # 檢查 DRIVE_FOLDER_ID（選用）
    if Config.DRIVE_FOLDER_ID:
        logger.info(f"✅ Drive 資料夾 ID: {Config.DRIVE_FOLDER_ID}")
    else:
        logger.warning("⚠️  未設定 DRIVE_FOLDER_ID（圖片會上傳到 Drive 根目錄）")

    logger.info("")
    return True


def test_image_compression():
    """測試圖片壓縮功能"""
    logger.info("=" * 60)
    logger.info("測試圖片壓縮...")
    logger.info("=" * 60)

    # 檢查測試圖片
    test_image_path = "test_image.jpg"
    if not os.path.exists(test_image_path):
        logger.error(f"❌ 找不到測試圖片: {test_image_path}")
        logger.error("請放置一張測試圖片（test_image.jpg）在專案根目錄")
        return None

    try:
        # 讀取測試圖片
        with open(test_image_path, 'rb') as f:
            image_data = f.read()

        logger.info(f"原始圖片大小: {len(image_data) / 1024:.1f}KB")

        # 壓縮圖片
        from src.services.image_processor import ImageProcessor
        compressed_data, mime_type = ImageProcessor.compress_image(image_data)

        logger.info(f"壓縮後大小: {len(compressed_data) / 1024:.1f}KB")
        logger.info(f"MIME 類型: {mime_type}")
        logger.info("✅ 圖片壓縮成功")
        logger.info("")

        return compressed_data, mime_type

    except Exception as e:
        logger.error(f"❌ 圖片壓縮失敗: {e}", exc_info=True)
        return None


def test_drive_upload(image_data, mime_type):
    """測試 Google Drive 上傳"""
    logger.info("=" * 60)
    logger.info("測試 Google Drive 上傳...")
    logger.info("=" * 60)

    try:
        from src.services.drive_client import get_drive_client
        from src.services.time_utils import TAIWAN_TZ
        from datetime import datetime

        # 建立檔名
        now = datetime.now(TAIWAN_TZ)
        filename = f"test_linebot_{now.strftime('%Y%m%d_%H%M%S')}.jpg"

        logger.info(f"檔案名稱: {filename}")
        logger.info(f"檔案大小: {len(image_data) / 1024:.1f}KB")

        # 上傳到 Drive
        drive_client = get_drive_client()
        drive_client.connect()

        image_url = drive_client.upload_image(image_data, filename, mime_type)

        logger.info(f"✅ 上傳成功！")
        logger.info(f"圖片 URL: {image_url}")
        logger.info("")

        return image_url

    except Exception as e:
        logger.error(f"❌ Drive 上傳失敗: {e}", exc_info=True)
        return None


def test_image_message(image_url, message_id="test_image_001", user_id="test_user_001"):
    """
    測試完整的圖片訊息記錄流程

    Args:
        image_url: 圖片 URL
        message_id: 訊息 ID
        user_id: 使用者 ID
    """
    logger.info("=" * 60)
    logger.info(f"測試圖片訊息記錄")
    logger.info("=" * 60)

    try:
        from src.models.message import MessageRecord
        from src.services.time_utils import convert_line_timestamp_to_taiwan, TAIWAN_TZ
        from src.services.sheets_client import get_sheets_client
        from datetime import datetime

        # 建立模擬事件
        event = MockMessageEvent(message_id=message_id, user_id=user_id)

        # 轉換時間
        taiwan_time = convert_line_timestamp_to_taiwan(event.timestamp)
        logger.info(f"台灣時間: {taiwan_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 建立 MessageRecord（使用 IMAGE 公式）
        record = MessageRecord.create_image_message(
            timestamp=taiwan_time,
            image_url=image_url,
            user_id=user_id
        )

        logger.info(f"訊息類型: {record.message_type.value}")
        logger.info(f"IMAGE 公式: {record.content[:50]}...")

        # 取得 Sheets 客戶端
        sheets_client = get_sheets_client()
        sheets_client.connect()

        # 取得或建立月份工作表
        month_title = taiwan_time.strftime("%Y-%m")
        worksheet = sheets_client.get_worksheet(month_title)

        if worksheet is None:
            logger.info(f"建立新工作表: {month_title}")
            worksheet = sheets_client.create_worksheet(month_title, rows=1000, cols=3)
            worksheet.append_row(['時間', '類型', '內容'])

        # 寫入訊息
        row = record.to_sheet_row()
        worksheet.append_row(row)

        logger.info("✅ 成功寫入訊息到 Google Sheets")
        logger.info("")

        return True

    except Exception as e:
        logger.error(f"❌ 訊息記錄失敗: {e}", exc_info=True)
        return False


def verify_sheets_data():
    """驗證 Google Sheets 中的資料"""
    logger.info("=" * 60)
    logger.info("驗證 Google Sheets 資料...")
    logger.info("=" * 60)

    try:
        from src.services.sheets_client import get_sheets_client
        from src.services.time_utils import TAIWAN_TZ
        from datetime import datetime

        client = get_sheets_client()
        client.connect()

        # 取得當前月份的工作表
        month_title = datetime.now(TAIWAN_TZ).strftime("%Y-%m")
        worksheet = client.get_worksheet(month_title)

        if worksheet is None:
            logger.warning(f"⚠️  工作表 '{month_title}' 不存在")
            return False

        # 取得所有資料
        all_values = worksheet.get_all_values()

        logger.info(f"工作表: {month_title}")
        logger.info(f"總行數: {len(all_values)}")
        logger.info("")

        if len(all_values) > 0:
            logger.info("最近 3 筆記錄：")
            logger.info("-" * 60)
            for row in all_values[-3:]:
                if len(row) >= 3:
                    content = row[2][:60] if row[2] else ""
                    if content.startswith("=IMAGE"):
                        content = f"{content[:30]}...{content[-20:]}"
                    logger.info(f"  {row[0]} | {row[1]} | {content}")
                else:
                    logger.info(f"  {row}")
            logger.info("-" * 60)

        logger.info("")
        logger.info("✅ 請檢查 Google Sheets 確認圖片是否正確顯示")
        logger.info(f"   試算表連結: https://docs.google.com/spreadsheets/d/{os.getenv('SPREADSHEET_ID')}")
        logger.info("")
        return True

    except Exception as e:
        logger.error(f"❌ 驗證失敗: {e}", exc_info=True)
        return False


def main():
    """主函式"""
    print("\n")
    logger.info("🚀 開始本地測試：圖片訊息記錄功能")
    logger.info("")

    # 步驟 1: 驗證環境變數
    if not verify_env():
        logger.error("❌ 環境設定不完整，測試中止")
        sys.exit(1)

    # 步驟 2: 測試圖片壓縮
    result = test_image_compression()
    if result is None:
        logger.error("❌ 圖片壓縮測試失敗，測試中止")
        sys.exit(1)

    compressed_data, mime_type = result

    # 步驟 3: 測試 Drive 上傳
    image_url = test_drive_upload(compressed_data, mime_type)
    if image_url is None:
        logger.error("❌ Drive 上傳測試失敗，測試中止")
        sys.exit(1)

    # 步驟 4: 測試訊息記錄
    if not test_image_message(image_url):
        logger.error("❌ 訊息記錄測試失敗")
        sys.exit(1)

    # 步驟 5: 驗證結果
    verify_sheets_data()

    # 總結
    logger.info("=" * 60)
    logger.info("✅ 本地測試完成！")
    logger.info("=" * 60)
    logger.info("")
    logger.info("請執行以下步驟確認測試結果：")
    logger.info("1. 開啟 Google Sheets 試算表")
    logger.info("2. 檢查當前月份的工作表")
    logger.info("3. 確認圖片是否正確顯示（IMAGE 公式）")
    logger.info("4. 開啟 Google Drive 確認圖片已上傳")
    logger.info("")


if __name__ == '__main__':
    main()
