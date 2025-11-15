#!/usr/bin/env python3
"""
Webhook Server 啟動腳本

啟動 Flask webhook server 以接收 LINE 訊息。
適用於本地開發測試，搭配 ngrok 使用。

使用方法：
    python start_webhook.py

環境需求：
    - .env 檔案已設定所有必要環境變數
    - service_account.json 檔案存在
    - Google Sheets 已分享給 Service Account
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定日誌
from src.config import setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)


def verify_environment():
    """驗證環境設定"""
    from src.config import Config

    logger.info("=" * 60)
    logger.info("🔍 檢查環境設定")
    logger.info("=" * 60)

    is_valid, missing = Config.validate()

    if not is_valid:
        logger.error(f"❌ 缺少必要的環境變數: {', '.join(missing)}")
        logger.error("")
        logger.error("請確認 .env 檔案包含以下設定：")
        logger.error("  - GOOGLE_CREDENTIALS_FILE")
        logger.error("  - SPREADSHEET_ID")
        logger.error("  - LINE_CHANNEL_ACCESS_TOKEN")
        logger.error("  - LINE_CHANNEL_SECRET")
        logger.error("")
        return False

    logger.info("✅ 環境變數檢查通過")
    logger.info("")

    # 測試 Google Sheets 連線
    try:
        from src.services.sheets_client import get_sheets_client
        client = get_sheets_client()
        client.connect()
        spreadsheet = client.get_spreadsheet()
        logger.info(f"✅ Google Sheets 連線成功: {spreadsheet.title}")
        logger.info("")
    except Exception as e:
        logger.error(f"❌ Google Sheets 連線失敗: {e}")
        logger.error("")
        return False

    return True


def main():
    """主函式"""
    print("\n")
    logger.info("🚀 啟動 LINE Bot Webhook Server")
    logger.info("")

    # 驗證環境
    if not verify_environment():
        logger.error("❌ 環境設定不完整，無法啟動 server")
        sys.exit(1)

    # 啟動 Flask app
    logger.info("=" * 60)
    logger.info("🌐 啟動 Flask Server")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Server 將在以下位址運行：")
    logger.info("  - Local:   http://127.0.0.1:5000")
    logger.info("  - Webhook: http://127.0.0.1:5000/webhook")
    logger.info("")
    logger.info("⚠️  請使用 ngrok 建立公開 URL 以接收 LINE 訊息")
    logger.info("   執行：ngrok http 5000")
    logger.info("")
    logger.info("按 Ctrl+C 停止 server")
    logger.info("=" * 60)
    logger.info("")

    try:
        from src.webhook.app import app

        # 開發模式啟動
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=os.getenv('FLASK_DEBUG', '0') == '1'
        )

    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 60)
        logger.info("👋 Server 已停止")
        logger.info("=" * 60)
        logger.info("")
    except Exception as e:
        logger.error(f"❌ Server 啟動失敗: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
