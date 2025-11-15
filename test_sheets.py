"""
Google Sheets 連線測試腳本

此腳本用於驗證 Google Sheets API 設定是否正確。
會從 .env 檔案讀取配置，並嘗試寫入測試資料到試算表。
"""

import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

def test_google_sheets_connection():
    """測試 Google Sheets 連線和寫入功能"""

    # 從環境變數取得配置
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'service_account.json')
    spreadsheet_id = os.getenv('SPREADSHEET_ID')

    # 驗證必要的環境變數
    if not spreadsheet_id:
        print("❌ 錯誤：找不到 SPREADSHEET_ID 環境變數")
        print("請確認 .env 檔案存在且包含 SPREADSHEET_ID=你的試算表ID")
        return False

    # 檢查憑證檔案是否存在
    if not os.path.exists(credentials_file):
        print(f"❌ 錯誤：找不到憑證檔案 {credentials_file}")
        print(f"請確認 {credentials_file} 檔案存在於專案根目錄")
        return False

    print(f"📄 使用憑證檔案: {credentials_file}")
    print(f"📊 試算表 ID: {spreadsheet_id}")
    print()

    try:
        # 設定權限範圍
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        print("🔐 載入 Service Account 憑證...")
        # 載入憑證
        creds = Credentials.from_service_account_file(
            credentials_file,
            scopes=scopes
        )

        print("🔗 建立 gspread 客戶端...")
        # 建立 gspread 客戶端
        gc = gspread.authorize(creds)

        print(f"📂 開啟試算表 (ID: {spreadsheet_id[:20]}...)...")
        # 開啟試算表
        spreadsheet = gc.open_by_key(spreadsheet_id)
        print(f"✅ 成功開啟試算表: {spreadsheet.title}")

        # 測試寫入
        print("✏️  測試寫入第一個工作表...")
        worksheet = spreadsheet.sheet1
        worksheet.update('A1', 'Hello from Python!')
        worksheet.update('B1', 'Google Sheets API 測試成功！')

        # 驗證寫入
        print("🔍 驗證寫入內容...")
        value_a1 = worksheet.acell('A1').value
        value_b1 = worksheet.acell('B1').value

        print()
        print("="*60)
        print("✅ 成功！Google Sheets API 設定正確！")
        print("="*60)
        print(f"試算表名稱: {spreadsheet.title}")
        print(f"工作表名稱: {worksheet.title}")
        print(f"A1 儲存格: {value_a1}")
        print(f"B1 儲存格: {value_b1}")
        print()
        print("🎉 現在可以開始開發 LINE Bot 了！")
        print()

        return True

    except FileNotFoundError as e:
        print(f"❌ 錯誤：找不到檔案 - {e}")
        print("請確認 service_account.json 檔案存在")
        return False

    except gspread.exceptions.APIError as e:
        print(f"❌ Google API 錯誤: {e}")
        if "PERMISSION_DENIED" in str(e):
            print()
            print("可能的原因：")
            print("1. 試算表沒有分享給 Service Account")
            print("2. Service Account Email 不正確")
            print()
            print("解決方法：")
            print("1. 開啟 Google Sheets 試算表")
            print("2. 點擊「共用」按鈕")
            print("3. 新增 Service Account Email（從 service_account.json 中的 client_email）")
            print("4. 權限設為「編輯者」")
        return False

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"❌ 錯誤：找不到試算表 (ID: {spreadsheet_id})")
        print()
        print("可能的原因：")
        print("1. 試算表 ID 不正確")
        print("2. 試算表已被刪除")
        print("3. 試算表沒有分享給 Service Account")
        print()
        print("請檢查：")
        print("1. .env 檔案中的 SPREADSHEET_ID 是否正確")
        print("2. 試算表 URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit")
        return False

    except ValueError as e:
        print(f"❌ 憑證檔案格式錯誤: {e}")
        print("請確認 service_account.json 是有效的 JSON 格式")
        return False

    except Exception as e:
        print(f"❌ 未預期的錯誤: {type(e).__name__}")
        print(f"錯誤訊息: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("Google Sheets 連線測試")
    print("="*60)
    print()

    success = test_google_sheets_connection()

    if not success:
        print()
        print("💡 提示：請參考 specs/001-line-message-logger/google-sheets-setup.md")
        print("   完成 Google Sheets API 設定")
        exit(1)
    else:
        exit(0)
