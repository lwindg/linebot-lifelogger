#!/usr/bin/env python3
"""
Cloud Run 啟動診斷工具

測試應用程式在 Cloud Run 環境下能否正常啟動
"""

import os
import sys
import json

print("=" * 60)
print("Cloud Run 啟動診斷")
print("=" * 60)
print()

# 檢查 1: PORT 環境變數
print("1. 檢查 PORT 環境變數")
port = os.getenv('PORT', '8080')
print(f"   PORT = {port}")
print()

# 檢查 2: 必要環境變數
print("2. 檢查必要環境變數")
required_vars = [
    'SPREADSHEET_ID',
    'LINE_CHANNEL_ACCESS_TOKEN',
    'LINE_CHANNEL_SECRET',
    'GOOGLE_CREDENTIALS_JSON'
]

all_ok = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        if var == 'GOOGLE_CREDENTIALS_JSON':
            print(f"   ✓ {var} = (長度: {len(value)} 字元)")
        elif 'TOKEN' in var or 'SECRET' in var:
            print(f"   ✓ {var} = {value[:10]}...")
        else:
            print(f"   ✓ {var} = {value}")
    else:
        print(f"   ✗ {var} = 未設定")
        all_ok = False
print()

if not all_ok:
    print("❌ 缺少必要環境變數")
    sys.exit(1)

# 檢查 3: Google 憑證 JSON 格式
print("3. 檢查 Google 憑證 JSON 格式")
try:
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    creds_data = json.loads(creds_json)
    print(f"   ✓ JSON 格式正確")
    print(f"   ✓ Project ID: {creds_data.get('project_id')}")
    print(f"   ✓ Client Email: {creds_data.get('client_email')}")
except json.JSONDecodeError as e:
    print(f"   ✗ JSON 格式錯誤: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ 解析失敗: {e}")
    sys.exit(1)
print()

# 檢查 4: 測試 Google Sheets 連線
print("4. 測試 Google Sheets 連線")
try:
    from src.services.sheets_client import get_sheets_client

    client = get_sheets_client()
    client.connect()

    spreadsheet = client.get_spreadsheet()
    print(f"   ✓ 成功連線到試算表: {spreadsheet.title}")
except Exception as e:
    print(f"   ✗ 連線失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

# 檢查 5: 測試 Flask app 能否建立
print("5. 測試 Flask app 能否建立")
try:
    from src.webhook.app import app
    print(f"   ✓ Flask app 建立成功")
    print(f"   ✓ App name: {app.name}")
except Exception as e:
    print(f"   ✗ Flask app 建立失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

# 檢查 6: 測試能否啟動 server
print("6. 測試 Gunicorn 設定")
try:
    import gunicorn
    print(f"   ✓ Gunicorn 版本: {gunicorn.__version__}")
    print(f"   ✓ 綁定位址: 0.0.0.0:{port}")
    print(f"   ✓ Workers: 1")
    print(f"   ✓ Threads: 8")
except Exception as e:
    print(f"   ✗ Gunicorn 檢查失敗: {e}")
    sys.exit(1)
print()

print("=" * 60)
print("✅ 所有檢查通過！應用程式應該可以正常啟動")
print("=" * 60)
print()
print("如果 Cloud Run 還是失敗，請檢查：")
print("1. 容器記憶體是否足夠（建議 512Mi）")
print("2. 啟動超時設定（建議 300 秒）")
print("3. Cloud Run 日誌中的錯誤訊息")
