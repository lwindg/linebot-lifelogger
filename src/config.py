"""
Configuration Management Module

管理應用程式的配置設定，從環境變數載入並驗證必要的配置項目。
"""

import os
import logging
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()


class Config:
    """應用程式配置類別"""

    # Google API 設定
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'service_account.json')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')

    # LINE Bot 設定
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

    # Flask 設定
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    # Cloud Run 使用 PORT，本地開發使用 FLASK_PORT
    FLASK_PORT = int(os.getenv('PORT', os.getenv('FLASK_PORT', '5000')))

    # 日誌設定
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def validate(cls):
        """
        驗證必要的配置項目是否已設定

        Returns:
            tuple: (is_valid: bool, missing_configs: list)
        """
        required_configs = {
            'SPREADSHEET_ID': cls.SPREADSHEET_ID,
            'LINE_CHANNEL_ACCESS_TOKEN': cls.LINE_CHANNEL_ACCESS_TOKEN,
            'LINE_CHANNEL_SECRET': cls.LINE_CHANNEL_SECRET,
        }

        missing = [key for key, value in required_configs.items() if not value]

        return len(missing) == 0, missing

    @classmethod
    def get_log_level(cls):
        """
        取得日誌級別

        Returns:
            int: logging 模組的日誌級別常數
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        return level_map.get(cls.LOG_LEVEL.upper(), logging.INFO)


def setup_logging():
    """
    設定應用程式的日誌系統

    配置日誌格式、級別和輸出處理器
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(
        level=Config.get_log_level(),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(),  # 輸出到 console
        ]
    )

    # 設定第三方套件的日誌級別（避免過多輸出）
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    logging.getLogger('googleapiclient').setLevel(logging.WARNING)


def check_credentials_file():
    """
    檢查 Google Service Account 憑證檔案是否存在

    Returns:
        bool: 檔案是否存在
    """
    return os.path.exists(Config.GOOGLE_CREDENTIALS_FILE)


# 初始化日誌系統
setup_logging()

# 取得 logger
logger = logging.getLogger(__name__)

# 驗證配置
is_valid, missing = Config.validate()
if not is_valid:
    logger.warning(f"缺少必要的環境變數: {', '.join(missing)}")
    logger.warning("請檢查 .env 檔案是否正確設定")

# 檢查憑證檔案
if not check_credentials_file():
    logger.warning(f"找不到 Google 憑證檔案: {Config.GOOGLE_CREDENTIALS_FILE}")
    logger.warning("請確認 service_account.json 檔案存在於專案根目錄")
