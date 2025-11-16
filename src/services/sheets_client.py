"""
Google Sheets Client

提供 Google Sheets API 的封裝，處理試算表的讀寫操作。
"""

import os
import json
import logging
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional, List

from src.config import Config

logger = logging.getLogger(__name__)


class SheetsClient:
    """Google Sheets 客戶端類別"""

    def __init__(self):
        """初始化 Google Sheets 客戶端"""
        self.spreadsheet_id = Config.SPREADSHEET_ID
        self.credentials_file = Config.GOOGLE_CREDENTIALS_FILE

        # 設定權限範圍
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        self._gc = None
        self._spreadsheet = None

        logger.info("SheetsClient 初始化完成")

    def connect(self):
        """
        建立與 Google Sheets 的連線

        支援兩種認證方式：
        1. 從環境變數 GOOGLE_CREDENTIALS_JSON 讀取（Cloud Run）
        2. 從檔案讀取（本地開發）

        Raises:
            FileNotFoundError: 憑證檔案不存在
            Exception: 連線失敗
        """
        try:
            # 方式 1: 從環境變數讀取 JSON（優先，用於 Cloud Run）
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')

            if credentials_json:
                logger.info("從環境變數載入 Google 憑證")
                try:
                    credentials_info = json.loads(credentials_json)
                    creds = Credentials.from_service_account_info(
                        credentials_info,
                        scopes=self.scopes
                    )
                    logger.info("成功從環境變數載入憑證")
                except json.JSONDecodeError as e:
                    logger.error(f"解析環境變數 GOOGLE_CREDENTIALS_JSON 失敗: {e}")
                    raise

            # 方式 2: 從檔案讀取（本地開發）
            else:
                logger.info(f"從檔案載入憑證: {self.credentials_file}")
                creds = Credentials.from_service_account_file(
                    self.credentials_file,
                    scopes=self.scopes
                )

            logger.info("建立 gspread 客戶端")
            self._gc = gspread.authorize(creds)

            logger.info(f"開啟試算表: {self.spreadsheet_id}")
            self._spreadsheet = self._gc.open_by_key(self.spreadsheet_id)

            logger.info(f"成功連線到試算表: {self._spreadsheet.title}")

        except FileNotFoundError:
            logger.error(f"找不到憑證檔案: {self.credentials_file}")
            raise

        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"找不到試算表: {self.spreadsheet_id}")
            raise

        except Exception as e:
            logger.error(f"連線 Google Sheets 失敗: {e}")
            raise

    def get_spreadsheet(self):
        """
        取得試算表物件

        Returns:
            gspread.Spreadsheet: 試算表物件
        """
        if self._spreadsheet is None:
            self.connect()
        return self._spreadsheet

    def get_worksheet(self, title: str):
        """
        取得指定名稱的工作表

        Args:
            title: 工作表名稱

        Returns:
            gspread.Worksheet: 工作表物件，如果不存在則返回 None
        """
        spreadsheet = self.get_spreadsheet()

        try:
            worksheet = spreadsheet.worksheet(title)
            logger.debug(f"找到工作表: {title}")
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            logger.debug(f"工作表不存在: {title}")
            return None

    def create_worksheet(self, title: str, rows: int = 1000, cols: int = 10):
        """
        建立新的工作表

        Args:
            title: 工作表名稱
            rows: 列數
            cols: 欄數

        Returns:
            gspread.Worksheet: 新建立的工作表物件
        """
        spreadsheet = self.get_spreadsheet()

        try:
            logger.info(f"建立新工作表: {title}")
            worksheet = spreadsheet.add_worksheet(
                title=title,
                rows=rows,
                cols=cols
            )
            logger.info(f"成功建立工作表: {title}")
            return worksheet

        except Exception as e:
            logger.error(f"建立工作表失敗: {e}")
            raise

    def append_row(self, worksheet, values: List):
        """
        在工作表最後新增一列

        Args:
            worksheet: 工作表物件
            values: 要新增的值列表

        Raises:
            Exception: 新增失敗
        """
        try:
            worksheet.append_row(values)
            logger.debug(f"成功新增一列到工作表: {worksheet.title}")

        except Exception as e:
            logger.error(f"新增列失敗: {e}")
            raise

    def get_all_values(self, worksheet) -> List[List[str]]:
        """
        取得工作表的所有資料

        Args:
            worksheet: 工作表物件

        Returns:
            List[List[str]]: 所有資料的二維列表
        """
        try:
            values = worksheet.get_all_values()
            logger.debug(f"取得工作表資料，共 {len(values)} 列")
            return values

        except Exception as e:
            logger.error(f"取得工作表資料失敗: {e}")
            raise

    def update_cell(self, worksheet, cell: str, value: str):
        """
        更新單一儲存格

        Args:
            worksheet: 工作表物件
            cell: 儲存格位置（如 "A1"）
            value: 要更新的值
        """
        try:
            worksheet.update(cell, value)
            logger.debug(f"更新儲存格 {cell}: {value}")

        except Exception as e:
            logger.error(f"更新儲存格失敗: {e}")
            raise


# 建立全域的 SheetsClient 實例
_sheets_client = None


def get_sheets_client() -> SheetsClient:
    """
    取得 Google Sheets 客戶端單例

    Returns:
        SheetsClient: Sheets 客戶端實例
    """
    global _sheets_client
    if _sheets_client is None:
        _sheets_client = SheetsClient()
    return _sheets_client
