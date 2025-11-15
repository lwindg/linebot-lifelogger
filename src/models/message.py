"""
Message Model

定義訊息資料類別和相關的列舉型別。
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class MessageType(Enum):
    """訊息類型列舉"""
    TEXT = "文字"
    IMAGE = "圖片"
    UNSUPPORTED = "[不支援]"


class MessageStatus(Enum):
    """訊息記錄狀態列舉"""
    SUCCESS = "成功"
    FAILED = "失敗"


@dataclass
class MessageRecord:
    """
    訊息記錄資料類別

    Attributes:
        timestamp: 訊息接收時間（台灣時區）
        message_type: 訊息類型
        content: 訊息內容（文字內容或圖片 URL/IMAGE 公式）
        user_id: LINE 使用者 ID
        status: 記錄狀態
        error_message: 錯誤訊息（如果記錄失敗）
    """
    timestamp: datetime
    message_type: MessageType
    content: str
    user_id: str
    status: MessageStatus = MessageStatus.SUCCESS
    error_message: Optional[str] = None

    def to_sheet_row(self) -> list:
        """
        轉換為 Google Sheets 的一列資料

        Returns:
            list: [時間字串, 類型, 內容]
        """
        from src.services.time_utils import format_datetime

        time_str = format_datetime(self.timestamp)
        type_str = self.message_type.value
        content_str = self.content

        return [time_str, type_str, content_str]

    @classmethod
    def create_text_message(cls, timestamp: datetime, text: str, user_id: str):
        """
        建立文字訊息記錄

        Args:
            timestamp: 訊息時間
            text: 文字內容
            user_id: 使用者 ID

        Returns:
            MessageRecord: 訊息記錄物件
        """
        return cls(
            timestamp=timestamp,
            message_type=MessageType.TEXT,
            content=text,
            user_id=user_id
        )

    @classmethod
    def create_image_message(cls, timestamp: datetime, image_url: str, user_id: str):
        """
        建立圖片訊息記錄（使用 IMAGE 公式）

        Args:
            timestamp: 訊息時間
            image_url: 圖片 URL（Google Drive 連結）
            user_id: 使用者 ID

        Returns:
            MessageRecord: 訊息記錄物件
        """
        # 建立 Google Sheets IMAGE 公式
        image_formula = f'=IMAGE("{image_url}", 1)'

        return cls(
            timestamp=timestamp,
            message_type=MessageType.IMAGE,
            content=image_formula,
            user_id=user_id
        )

    @classmethod
    def create_unsupported_message(cls, timestamp: datetime, user_id: str, message_type_name: str = ""):
        """
        建立不支援的訊息類型記錄

        Args:
            timestamp: 訊息時間
            user_id: 使用者 ID
            message_type_name: 訊息類型名稱（如 "貼圖"、"影片"）

        Returns:
            MessageRecord: 訊息記錄物件
        """
        content = f"[不支援的訊息類型]"
        if message_type_name:
            content = f"[不支援的訊息類型: {message_type_name}]"

        return cls(
            timestamp=timestamp,
            message_type=MessageType.UNSUPPORTED,
            content=content,
            user_id=user_id
        )

    @classmethod
    def create_error_message(cls, timestamp: datetime, user_id: str, error_msg: str, message_type: MessageType = MessageType.TEXT):
        """
        建立錯誤訊息記錄

        Args:
            timestamp: 訊息時間
            user_id: 使用者 ID
            error_msg: 錯誤訊息
            message_type: 原始訊息類型

        Returns:
            MessageRecord: 訊息記錄物件
        """
        return cls(
            timestamp=timestamp,
            message_type=message_type,
            content=f"[錯誤: {error_msg}]",
            user_id=user_id,
            status=MessageStatus.FAILED,
            error_message=error_msg
        )
