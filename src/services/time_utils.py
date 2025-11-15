"""
Time Utilities Module

提供時區轉換、週次計算等時間相關的工具函式。
所有時間統一使用台灣時區（Asia/Taipei, UTC+8）。
"""

import pytz
from datetime import datetime, timedelta

# 定義台灣時區
TAIWAN_TZ = pytz.timezone('Asia/Taipei')


def convert_line_timestamp_to_taiwan(timestamp_ms: int) -> datetime:
    """
    將 LINE timestamp（UTC 毫秒）轉換為台灣時區的 datetime

    Args:
        timestamp_ms: LINE 訊息的時間戳記（毫秒）

    Returns:
        datetime: 台灣時區的 datetime 物件
    """
    # 將毫秒轉為秒
    timestamp_sec = timestamp_ms / 1000

    # 建立 UTC datetime
    utc_dt = datetime.utcfromtimestamp(timestamp_sec)
    utc_dt = pytz.utc.localize(utc_dt)

    # 轉換為台灣時區
    taiwan_dt = utc_dt.astimezone(TAIWAN_TZ)

    return taiwan_dt


def format_datetime(dt: datetime) -> str:
    """
    格式化 datetime 為標準字串格式

    Args:
        dt: datetime 物件

    Returns:
        str: 格式化的時間字串 "YYYY-MM-DD HH:MM:SS"
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def get_month_key(dt: datetime) -> str:
    """
    從 datetime 取得月份標識（YYYY-MM 格式）

    Args:
        dt: datetime 物件

    Returns:
        str: 月份標識，例如 "2025-11"
    """
    return dt.strftime('%Y-%m')


def get_week_number(dt: datetime) -> int:
    """
    計算該日期是當年的第幾週（週日為一週的起始日）

    使用演算法：
    1. 找到該年第一個週日
    2. 計算目標日期與第一個週日之間的差距
    3. 計算週數

    Args:
        dt: datetime 物件

    Returns:
        int: 週次（1-based，第一週為 1）
    """
    # 取得該年第一天
    year_start = datetime(dt.year, 1, 1, tzinfo=dt.tzinfo)

    # 計算該年第一個週日
    # weekday(): 週一=0, 週二=1, ..., 週日=6
    days_until_sunday = (6 - year_start.weekday()) % 7
    if days_until_sunday == 0 and year_start.weekday() != 6:
        # 如果第一天不是週日，則找下一個週日
        days_until_sunday = 7
    first_sunday = year_start + timedelta(days=days_until_sunday)

    # 如果日期在第一個週日之前，算作第 1 週
    if dt < first_sunday:
        return 1

    # 計算週數
    delta_days = (dt - first_sunday).days
    week_number = (delta_days // 7) + 2  # +2 因為第一個週日是第 2 週開始

    return week_number


def is_new_week(current_dt: datetime, previous_dt: datetime) -> bool:
    """
    判斷兩個 datetime 之間是否跨越週界（週六到週日）

    Args:
        current_dt: 當前的 datetime
        previous_dt: 前一個 datetime

    Returns:
        bool: True 表示跨週，False 表示同一週
    """
    # weekday(): 週一=0, 週日=6
    # 如果前一個不是週日(6)，而當前是週日(6)，則跨週
    return previous_dt.weekday() != 6 and current_dt.weekday() == 6


def parse_taiwan_time(time_str: str) -> datetime:
    """
    解析時間字串為台灣時區的 datetime

    Args:
        time_str: 時間字串，格式 "YYYY-MM-DD HH:MM:SS"

    Returns:
        datetime: 台灣時區的 datetime 物件
    """
    naive_dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    return TAIWAN_TZ.localize(naive_dt)


def get_current_taiwan_time() -> datetime:
    """
    取得當前的台灣時區時間

    Returns:
        datetime: 當前的台灣時區 datetime 物件
    """
    return datetime.now(TAIWAN_TZ)
