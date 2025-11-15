#!/usr/bin/env python3
"""
本地測試腳本：測試文字訊息記錄功能

此腳本模擬 LINE 文字訊息事件，不需要啟動 webhook server。
直接測試 handle_text_message 函式是否正確寫入 Google Sheets。

使用方法：
1. 確保已建立 .env 檔案並設定環境變數
2. 確保 Google Sheets 已分享給 Service Account
3. 執行：python test_local_text_message.py
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


class MockTextMessage:
    """模擬 LINE TextMessage 物件"""
    def __init__(self, text):
        self.type = 'text'
        self.id = '100001'
        self.text = text


class MockSource:
    """模擬 LINE Source 物件"""
    def __init__(self, user_id):
        self.type = 'user'
        self.user_id = user_id


class MockMessageEvent:
    """模擬 LINE MessageEvent 物件"""
    def __init__(self, text, user_id, timestamp=None):
        self.type = 'message'
        self.message = MockTextMessage(text)
        self.source = MockSource(user_id)
        # 使用當前時間的毫秒時間戳記，或使用提供的時間戳記
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
        logger.error("請先建立 .env 檔案並設定以下環境變數：")
        logger.error("  - GOOGLE_CREDENTIALS_FILE（Google Service Account JSON 檔案路徑）")
        logger.error("  - SPREADSHEET_ID（Google Sheets 試算表 ID）")
        logger.error("  - LINE_CHANNEL_ACCESS_TOKEN（LINE Bot Access Token）")
        logger.error("  - LINE_CHANNEL_SECRET（LINE Bot Channel Secret）")
        logger.error("")
        logger.error("參考 .env.example 建立您的 .env 檔案")
        return False

    logger.info("✅ 所有必要環境變數已設定")
    logger.info(f"  - Google 憑證檔案: {Config.GOOGLE_CREDENTIALS_FILE}")
    logger.info(f"  - 試算表 ID: {Config.SPREADSHEET_ID[:20]}...")
    logger.info("")
    return True


def test_google_sheets_connection():
    """測試 Google Sheets 連線"""
    logger.info("=" * 60)
    logger.info("測試 Google Sheets 連線...")
    logger.info("=" * 60)

    try:
        from src.services.sheets_client import get_sheets_client

        client = get_sheets_client()
        client.connect()

        spreadsheet = client.get_spreadsheet()
        logger.info(f"✅ 成功連線到試算表: {spreadsheet.title}")
        logger.info("")
        return True

    except Exception as e:
        logger.error(f"❌ Google Sheets 連線失敗: {e}")
        logger.error("請確認：")
        logger.error("  1. service_account.json 檔案存在且正確")
        logger.error("  2. 試算表 ID 正確")
        logger.error("  3. 試算表已分享給 Service Account 的電子郵件")
        logger.error("")
        return False


def test_text_message(text, user_id="test_user_001"):
    """
    測試單一文字訊息記錄

    Args:
        text: 訊息文字
        user_id: 使用者 ID
    """
    logger.info("=" * 60)
    logger.info(f"測試文字訊息記錄: \"{text}\"")
    logger.info("=" * 60)

    try:
        # 建立模擬事件
        event = MockMessageEvent(text=text, user_id=user_id)

        logger.info(f"訊息內容: {text}")
        logger.info(f"使用者 ID: {user_id}")
        logger.info(f"時間戳記: {event.timestamp}")
        logger.info("")

        # 呼叫處理函式
        from src.webhook.handlers import handle_text_message
        handle_text_message(event)

        logger.info("✅ 訊息處理完成")
        logger.info("")
        return True

    except Exception as e:
        logger.error(f"❌ 訊息處理失敗: {e}", exc_info=True)
        logger.error("")
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
            logger.info("最近 5 筆記錄：")
            logger.info("-" * 60)
            for row in all_values[-5:]:
                if len(row) >= 3:
                    logger.info(f"  {row[0]} | {row[1]} | {row[2][:50]}...")
                else:
                    logger.info(f"  {row}")
            logger.info("-" * 60)

        logger.info("")
        logger.info("✅ 請檢查 Google Sheets 確認資料是否正確寫入")
        logger.info(f"   試算表連結: https://docs.google.com/spreadsheets/d/{os.getenv('SPREADSHEET_ID')}")
        logger.info("")
        return True

    except Exception as e:
        logger.error(f"❌ 驗證失敗: {e}", exc_info=True)
        logger.error("")
        return False


def main():
    """主函式"""
    print("\n")
    logger.info("🚀 開始本地測試：文字訊息記錄功能")
    logger.info("")

    # 步驟 1: 驗證環境變數
    if not verify_env():
        logger.error("❌ 環境設定不完整，測試中止")
        sys.exit(1)

    # 步驟 2: 測試 Google Sheets 連線
    if not test_google_sheets_connection():
        logger.error("❌ Google Sheets 連線失敗，測試中止")
        sys.exit(1)

    # 步驟 3: 測試多條文字訊息
    test_messages = [
        "這是第一條測試訊息 📝",
        "Hello World! 測試中文和英文混合",
        "測試特殊字元：!@#$%^&*()",
        "測試 emoji 🎉🎊🎈",
    ]

    success_count = 0
    for i, msg in enumerate(test_messages, 1):
        if test_text_message(msg, user_id=f"test_user_{i:03d}"):
            success_count += 1
        # 短暫延遲，避免時間戳記完全相同
        import time
        time.sleep(0.1)

    logger.info("=" * 60)
    logger.info(f"測試結果: {success_count}/{len(test_messages)} 成功")
    logger.info("=" * 60)
    logger.info("")

    # 步驟 4: 驗證寫入結果
    verify_sheets_data()

    # 總結
    logger.info("=" * 60)
    logger.info("✅ 本地測試完成！")
    logger.info("=" * 60)
    logger.info("")
    logger.info("請執行以下步驟確認測試結果：")
    logger.info("1. 開啟 Google Sheets 試算表")
    logger.info("2. 檢查當前月份的工作表（例如：2025-11）")
    logger.info("3. 確認測試訊息已正確寫入")
    logger.info("4. 確認欄位格式：時間 | 類型 | 內容")
    logger.info("")


if __name__ == '__main__':
    main()
