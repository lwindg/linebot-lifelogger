#!/bin/bash

# Google Sheets 認證設定腳本
# 將 service_account.json 轉換為 Cloud Run 可用的環境變數

set -e

echo "================================================"
echo "  Google Sheets 認證設定工具"
echo "================================================"
echo ""

# 檢查 service_account.json 是否存在
if [ ! -f "service_account.json" ]; then
    echo "❌ 錯誤：找不到 service_account.json"
    echo "請確保檔案存在於專案根目錄"
    exit 1
fi

echo "✓ 找到 service_account.json"
echo ""

# 將 JSON 轉換為單行並移除空白
echo "正在處理 Service Account JSON..."
GOOGLE_CREDENTIALS_JSON=$(cat service_account.json | tr -d '\n' | tr -d ' ')

# 輸出到 .env.production
if [ -f ".env.production" ]; then
    echo ""
    echo "⚠️  .env.production 已存在"
    echo "是否要附加 GOOGLE_CREDENTIALS_JSON 到現有檔案？ (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # 檢查是否已存在該變數
        if grep -q "^GOOGLE_CREDENTIALS_JSON=" .env.production; then
            # 替換現有的
            sed -i.bak '/^GOOGLE_CREDENTIALS_JSON=/d' .env.production
            echo "GOOGLE_CREDENTIALS_JSON='${GOOGLE_CREDENTIALS_JSON}'" >> .env.production
            echo "✓ 已更新現有的 GOOGLE_CREDENTIALS_JSON"
        else
            # 新增
            echo "GOOGLE_CREDENTIALS_JSON='${GOOGLE_CREDENTIALS_JSON}'" >> .env.production
            echo "✓ 已新增 GOOGLE_CREDENTIALS_JSON"
        fi
    fi
else
    # 建立新檔案
    echo "建立 .env.production..."
    cat > .env.production << EOF
# Google Sheets 認證（自動生成）
GOOGLE_CREDENTIALS_JSON='${GOOGLE_CREDENTIALS_JSON}'

# 請填入以下資訊
SPREADSHEET_ID=your_spreadsheet_id_here
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
EOF
    echo "✓ 已建立 .env.production"
fi

echo ""
echo "================================================"
echo "✅ 認證設定完成！"
echo "================================================"
echo ""
echo "下一步："
echo "1. 編輯 .env.production，填入其他必要資訊："
echo "   - SPREADSHEET_ID"
echo "   - LINE_CHANNEL_ACCESS_TOKEN"
echo "   - LINE_CHANNEL_SECRET"
echo ""
echo "2. 執行部署："
echo "   export GCP_PROJECT_ID=your-project-id"
echo "   ./deploy.sh"
echo ""
