"""
Image Processor

處理圖片壓縮、格式轉換等操作。
"""

import io
import logging
from PIL import Image
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class ImageProcessor:
    """圖片處理器類別"""

    # 壓縮設定
    MAX_WIDTH = 1920  # 最大寬度
    MAX_HEIGHT = 1920  # 最大高度
    QUALITY = 85  # JPEG 品質（0-100）
    MAX_SIZE_KB = 500  # 目標大小（KB）

    @staticmethod
    def compress_image(
        image_data: bytes,
        max_width: int = MAX_WIDTH,
        max_height: int = MAX_HEIGHT,
        quality: int = QUALITY,
        max_size_kb: int = MAX_SIZE_KB
    ) -> Tuple[bytes, str]:
        """
        壓縮圖片

        Args:
            image_data: 原始圖片資料
            max_width: 最大寬度
            max_height: 最大高度
            quality: JPEG 品質
            max_size_kb: 目標大小（KB）

        Returns:
            tuple: (壓縮後的圖片資料, MIME 類型)
        """
        try:
            # 載入圖片
            image = Image.open(io.BytesIO(image_data))
            original_format = image.format
            original_size = len(image_data)

            logger.info(f"原始圖片: {image.size}, 格式: {original_format}, 大小: {original_size / 1024:.1f}KB")

            # 轉換 RGBA 為 RGB（JPEG 不支援透明度）
            if image.mode in ('RGBA', 'LA', 'P'):
                logger.info(f"轉換圖片模式: {image.mode} -> RGB")
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            # 調整尺寸（保持比例）
            if image.width > max_width or image.height > max_height:
                logger.info(f"調整圖片尺寸: {image.size} -> ", end='')
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                logger.info(f"{image.size}")

            # 壓縮圖片（多級壓縮策略）
            output = io.BytesIO()
            current_quality = quality

            # 第一次壓縮
            image.save(output, format='JPEG', quality=current_quality, optimize=True)
            compressed_size = output.tell()

            logger.info(f"第一次壓縮: {compressed_size / 1024:.1f}KB (品質: {current_quality})")

            # 如果還是太大，降低品質
            attempts = 0
            max_attempts = 3
            while compressed_size > max_size_kb * 1024 and current_quality > 60 and attempts < max_attempts:
                attempts += 1
                current_quality -= 10
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=current_quality, optimize=True)
                compressed_size = output.tell()
                logger.info(f"第 {attempts + 1} 次壓縮: {compressed_size / 1024:.1f}KB (品質: {current_quality})")

            compressed_data = output.getvalue()
            compression_ratio = (1 - compressed_size / original_size) * 100

            logger.info(
                f"壓縮完成: {original_size / 1024:.1f}KB -> {compressed_size / 1024:.1f}KB "
                f"(壓縮率: {compression_ratio:.1f}%)"
            )

            return compressed_data, 'image/jpeg'

        except Exception as e:
            logger.error(f"圖片壓縮失敗: {e}")
            raise

    @staticmethod
    def validate_image(image_data: bytes) -> bool:
        """
        驗證圖片資料是否有效

        Args:
            image_data: 圖片資料

        Returns:
            bool: 是否為有效圖片
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image.verify()
            return True
        except Exception as e:
            logger.error(f"圖片驗證失敗: {e}")
            return False

    @staticmethod
    def get_image_info(image_data: bytes) -> Optional[dict]:
        """
        取得圖片資訊

        Args:
            image_data: 圖片資料

        Returns:
            dict: 圖片資訊（寬、高、格式、大小）
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            return {
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'mode': image.mode,
                'size_kb': len(image_data) / 1024
            }
        except Exception as e:
            logger.error(f"取得圖片資訊失敗: {e}")
            return None
