"""
Google Drive Client

提供 Google Drive API 的封裝，處理檔案上傳操作。
"""

import os
import json
import logging
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.service_account import Credentials

from src.config import Config

logger = logging.getLogger(__name__)


class DriveClient:
    """Google Drive 客戶端類別"""

    def __init__(self):
        """初始化 Google Drive 客戶端"""
        self.folder_id = Config.DRIVE_FOLDER_ID
        self.credentials_file = Config.GOOGLE_CREDENTIALS_FILE

        # 檢查 DRIVE_FOLDER_ID 是否設定
        if not self.folder_id:
            logger.error("DRIVE_FOLDER_ID 未設定")
            logger.error("Service Account 沒有自己的儲存空間，必須上傳到使用者的資料夾")
            logger.error("請在 .env 設定 DRIVE_FOLDER_ID，並將該資料夾分享給 Service Account")
            raise ValueError("DRIVE_FOLDER_ID is required for Service Account uploads")

        # 設定權限範圍
        self.scopes = [
            'https://www.googleapis.com/auth/drive.file'
        ]

        self._service = None

        logger.info(f"DriveClient 初始化完成，目標資料夾: {self.folder_id}")

    def connect(self):
        """
        建立與 Google Drive 的連線

        支援兩種認證方式：
        1. 從環境變數 GOOGLE_CREDENTIALS_JSON 讀取（Cloud Run）
        2. 從檔案讀取（本地開發）
        """
        try:
            # 方式 1: 從環境變數讀取 JSON（優先，用於 Cloud Run）
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')

            if credentials_json:
                logger.info("從環境變數載入 Google 憑證（Drive）")
                credentials_info = json.loads(credentials_json)
                creds = Credentials.from_service_account_info(
                    credentials_info,
                    scopes=self.scopes
                )
            # 方式 2: 從檔案讀取（本地開發）
            else:
                logger.info(f"從檔案載入憑證（Drive）: {self.credentials_file}")
                creds = Credentials.from_service_account_file(
                    self.credentials_file,
                    scopes=self.scopes
                )

            # 建立 Drive service
            self._service = build('drive', 'v3', credentials=creds)
            logger.info("成功連線到 Google Drive")

        except Exception as e:
            logger.error(f"連線 Google Drive 失敗: {e}")
            raise

    def upload_image(
        self,
        image_data: bytes,
        filename: str,
        mime_type: str = 'image/jpeg'
    ) -> str:
        """
        上傳圖片到 Google Drive

        Args:
            image_data: 圖片二進制資料
            filename: 檔案名稱
            mime_type: MIME 類型

        Returns:
            str: 檔案的公開 URL

        Raises:
            Exception: 上傳失敗
        """
        if self._service is None:
            self.connect()

        try:
            # 準備檔案 metadata
            file_metadata = {
                'name': filename,
                'mimeType': mime_type
            }

            # 如果有指定資料夾，加入 parents
            if self.folder_id:
                file_metadata['parents'] = [self.folder_id]

            # 建立 media upload
            media = MediaInMemoryUpload(
                image_data,
                mimetype=mime_type,
                resumable=True
            )

            # 上傳檔案
            logger.info(f"上傳圖片到 Drive: {filename}")
            file = self._service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()

            file_id = file.get('id')
            logger.info(f"圖片上傳成功，File ID: {file_id}")

            # 設定為公開可讀
            self._service.permissions().create(
                fileId=file_id,
                body={
                    'type': 'anyone',
                    'role': 'reader'
                }
            ).execute()

            logger.info(f"已設定檔案為公開可讀")

            # 生成直接存取 URL
            # 格式: https://drive.google.com/uc?id=FILE_ID
            direct_url = f"https://drive.google.com/uc?id={file_id}"

            logger.info(f"圖片 URL: {direct_url}")
            return direct_url

        except Exception as e:
            logger.error(f"上傳圖片失敗: {e}")
            raise

    def delete_file(self, file_id: str):
        """
        刪除 Drive 中的檔案

        Args:
            file_id: 檔案 ID
        """
        if self._service is None:
            self.connect()

        try:
            self._service.files().delete(fileId=file_id).execute()
            logger.info(f"已刪除檔案: {file_id}")
        except Exception as e:
            logger.error(f"刪除檔案失敗: {e}")
            raise


# 單例模式
_drive_client = None


def get_drive_client() -> DriveClient:
    """
    取得 DriveClient 單例

    Returns:
        DriveClient: Drive 客戶端實例
    """
    global _drive_client
    if _drive_client is None:
        _drive_client = DriveClient()
    return _drive_client
