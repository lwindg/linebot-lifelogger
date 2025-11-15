"""
Flask Application - LINE Webhook Server

LINE Bot 的 Webhook 伺服器主程式。
"""

import logging
from flask import Flask, request, abort

from src.config import Config
from src.services.line_client import get_line_client
from linebot.exceptions import InvalidSignatureError

logger = logging.getLogger(__name__)

# 建立 Flask 應用
app = Flask(__name__)

# 取得 LINE 客戶端
line_client = get_line_client()
line_bot_api = line_client.get_api()
handler = line_client.get_handler()


@app.route("/")
def index():
    """首頁路由"""
    return "LINE Bot LifeLogger is running!", 200


@app.route("/webhook", methods=['POST'])
def webhook():
    """
    LINE Webhook 端點

    接收來自 LINE 平台的事件並處理
    """
    # 取得 X-Line-Signature header
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        logger.warning("缺少 X-Line-Signature header")
        abort(400)

    # 取得請求 body
    body = request.get_data(as_text=True)
    logger.info(f"收到 Webhook 請求")
    logger.debug(f"Request body: {body}")

    # 驗證簽章並處理事件
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("簽章驗證失敗")
        abort(400)
    except Exception as e:
        logger.error(f"處理 Webhook 事件時發生錯誤: {e}", exc_info=True)
        # 仍然返回 200，避免 LINE 重複發送
        return 'OK', 200

    return 'OK', 200


@app.errorhandler(404)
def not_found(error):
    """404 錯誤處理器"""
    logger.warning(f"404 Not Found: {request.url}")
    return "Not Found", 404


@app.errorhandler(500)
def internal_error(error):
    """500 錯誤處理器"""
    logger.error(f"Internal Server Error: {error}", exc_info=True)
    return "Internal Server Error", 500


@app.errorhandler(Exception)
def handle_exception(e):
    """全域例外處理器"""
    logger.error(f"未處理的例外: {e}", exc_info=True)
    return "Internal Server Error", 500


def main():
    """主程式進入點"""
    logger.info("="*60)
    logger.info("LINE Bot LifeLogger 啟動中...")
    logger.info("="*60)
    logger.info(f"環境: {Config.FLASK_ENV}")
    logger.info(f"Debug 模式: {Config.FLASK_DEBUG}")
    logger.info(f"主機: {Config.FLASK_HOST}")
    logger.info(f"埠號: {Config.FLASK_PORT}")
    logger.info("="*60)

    # 驗證配置
    is_valid, missing = Config.validate()
    if not is_valid:
        logger.error(f"配置驗證失敗，缺少: {', '.join(missing)}")
        logger.error("請檢查 .env 檔案")
        return

    # 啟動 Flask 應用
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )


if __name__ == '__main__':
    main()
