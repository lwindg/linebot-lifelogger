"""
Google Cloud Storage Client

提供 Google Cloud Storage API 的封裝，處理圖片上傳操作。
"""

import os
import json
import logging
from typing import Optional
from google.cloud import storage
from google.oauth2.service_account import Credentials

from src.config import Config

logger = logging.getLogger(__name__)


class StorageClient:
    """Google Cloud Storage 客戶端類別"""

    def __init__(self):
        """初始化 Google Cloud Storage 客戶端"""
        self.bucket_name = Config.STORAGE_BUCKET_NAME
        self.credentials_file = Config.GOOGLE_CREDENTIALS_FILE

        # 檢查 STORAGE_BUCKET_NAME 是否設定
        if not self.bucket_name:
            logger.error("STORAGE_BUCKET_NAME 未設定")
            logger.error("請在 .env 設定 STORAGE_BUCKET_NAME")
            logger.error("請參考 GOOGLE_CLOUD_STORAGE_SETUP.md 建立 bucket")
            raise ValueError("STORAGE_BUCKET_NAME is required")

        # 允許的圖片類型
        self.allowed_mime_types = [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp'
        ]

        self._client = None
        self._bucket = None

        logger.info(f"StorageClient 初始化完成，Bucket: {self.bucket_name}")

    def connect(self):
        """
        建立與 Google Cloud Storage 的連線

        支援兩種認證方式：
        1. 從環境變數 GOOGLE_CREDENTIALS_JSON 讀取（Cloud Run）
        2. 從檔案讀取（本地開發）
        """
        try:
            # 方式 1: 從環境變數讀取 JSON（優先，用於 Cloud Run）
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')

            if credentials_json:
                logger.info("從環境變數載入 Google 憑證（Storage）")
                credentials_info = json.loads(credentials_json)
                creds = Credentials.from_service_account_info(credentials_info)
                self._client = storage.Client(
                    credentials=creds,
                    project=credentials_info.get('project_id')
                )
            # 方式 2: 從檔案讀取（本地開發）
            else:
                logger.info(f"從檔案載入憑證（Storage）: {self.credentials_file}")
                creds = Credentials.from_service_account_file(self.credentials_file)

                # 讀取 project_id
                with open(self.credentials_file, 'r') as f:
                    creds_data = json.load(f)
                    project_id = creds_data.get('project_id')

                self._client = storage.Client(
                    credentials=creds,
                    project=project_id
                )

            # 取得 bucket
            self._bucket = self._client.bucket(self.bucket_name)

            # 驗證 bucket 是否存在
            if not self._bucket.exists():
                logger.error(f"Bucket 不存在: {self.bucket_name}")
                logger.error("請參考 GOOGLE_CLOUD_STORAGE_SETUP.md 建立 bucket")
                raise ValueError(f"Bucket '{self.bucket_name}' does not exist")

            logger.info(f"成功連線到 Cloud Storage bucket: {self.bucket_name}")

        except Exception as e:
            logger.error(f"連線 Cloud Storage 失敗: {e}")
            raise

    def upload_image(
        self,
        image_data: bytes,
        filename: str,
        mime_type: str = 'image/jpeg'
    ) -> str:
        """
        上傳圖片到 Google Cloud Storage

        Args:
            image_data: 圖片二進制資料
            filename: 檔案名稱
            mime_type: MIME 類型

        Returns:
            str: 檔案的公開 URL

        Raises:
            ValueError: 不支援的圖片類型
            Exception: 上傳失敗
        """
        # 驗證 MIME 類型
        if mime_type not in self.allowed_mime_types:
            raise ValueError(
                f"不支援的圖片類型: {mime_type}。"
                f"支援的類型: {', '.join(self.allowed_mime_types)}"
            )

        # 確保已連線
        if self._client is None or self._bucket is None:
            self.connect()

        try:
            # 建立 blob (GCS 中的檔案物件)
            blob = self._bucket.blob(filename)

            # 設定 content type
            blob.content_type = mime_type

            # 上傳圖片
            logger.info(f"上傳圖片到 Cloud Storage: {filename}")
            blob.upload_from_string(
                image_data,
                content_type=mime_type
            )

            # 設定為公開可讀（讓 Google Sheets 可以顯示）
            blob.make_public()

            # 生成公開 URL
            # 格式: https://storage.googleapis.com/bucket-name/filename
            public_url = blob.public_url

            logger.info(f"圖片上傳成功: {public_url}")
            return public_url

        except Exception as e:
            logger.error(f"上傳圖片失敗: {e}")
            raise

    def delete_file(self, filename: str):
        """
        刪除 Cloud Storage 中的檔案

        Args:
            filename: 檔案名稱
        """
        if self._client is None or self._bucket is None:
            self.connect()

        try:
            blob = self._bucket.blob(filename)
            blob.delete()
            logger.info(f"已刪除檔案: {filename}")
        except Exception as e:
            logger.error(f"刪除檔案失敗: {e}")
            raise

    def list_files(self, prefix: Optional[str] = None, max_results: int = 100):
        """
        列出 bucket 中的檔案

        Args:
            prefix: 檔案名稱前綴（用於篩選）
            max_results: 最多返回幾個結果

        Returns:
            list: 檔案名稱列表
        """
        if self._client is None or self._bucket is None:
            self.connect()

        try:
            blobs = self._bucket.list_blobs(prefix=prefix, max_results=max_results)
            filenames = [blob.name for blob in blobs]
            logger.info(f"找到 {len(filenames)} 個檔案")
            return filenames
        except Exception as e:
            logger.error(f"列出檔案失敗: {e}")
            raise


# 單例模式
_storage_client = None


def get_storage_client() -> StorageClient:
    """
    取得 StorageClient 單例

    Returns:
        StorageClient: Storage 客戶端實例
    """
    global _storage_client
    if _storage_client is None:
        _storage_client = StorageClient()
    return _storage_client
