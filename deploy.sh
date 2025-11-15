#!/bin/bash

# Google Cloud Run 部署腳本
# 此腳本會自動建置並部署 LINE Bot 到 Cloud Run

set -e  # 遇到錯誤立即停止

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置變數（請修改為您的值）
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
SERVICE_NAME="${CLOUD_RUN_SERVICE:-linebot-lifelogger}"
REGION="${CLOUD_RUN_REGION:-asia-east1}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# 函式：印出訊息
print_step() {
    echo -e "${BLUE}==>${NC} ${1}"
}

print_success() {
    echo -e "${GREEN}✓${NC} ${1}"
}

print_error() {
    echo -e "${RED}✗${NC} ${1}"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} ${1}"
}

# 函式：檢查必要工具
check_requirements() {
    print_step "檢查必要工具..."

    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI 未安裝"
        echo "請訪問: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "gcloud CLI 已安裝"

    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安裝"
        echo "請訪問: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "Docker 已安裝"
}

# 函式：檢查 GCP 配置
check_gcp_config() {
    print_step "檢查 GCP 配置..."

    # 檢查 Project ID
    if [ "$PROJECT_ID" = "your-project-id" ]; then
        print_error "請設定 GCP_PROJECT_ID 環境變數或修改腳本中的 PROJECT_ID"
        echo "範例: export GCP_PROJECT_ID=my-project-123"
        exit 1
    fi

    # 設定專案
    gcloud config set project "$PROJECT_ID"
    print_success "專案設定為: $PROJECT_ID"
}

# 函式：建置 Docker image
build_image() {
    print_step "建置 Docker image..."

    docker build -t "$IMAGE_NAME:latest" .

    if [ $? -eq 0 ]; then
        print_success "Docker image 建置成功"
    else
        print_error "Docker image 建置失敗"
        exit 1
    fi
}

# 函式：推送 image 到 GCR
push_image() {
    print_step "推送 image 到 Google Container Registry..."

    # 配置 Docker 認證
    gcloud auth configure-docker --quiet

    docker push "$IMAGE_NAME:latest"

    if [ $? -eq 0 ]; then
        print_success "Image 推送成功"
    else
        print_error "Image 推送失敗"
        exit 1
    fi
}

# 函式：部署到 Cloud Run
deploy_to_cloudrun() {
    print_step "部署到 Cloud Run..."

    # 檢查是否需要設定環境變數
    if [ -f ".env.production" ]; then
        print_warning "找到 .env.production，將從中讀取環境變數"

        # 讀取環境變數
        export $(grep -v '^#' .env.production | xargs)
    else
        print_warning "未找到 .env.production，請確保已在 Cloud Run 設定環境變數"
    fi

    # 部署
    gcloud run deploy "$SERVICE_NAME" \
        --image "$IMAGE_NAME:latest" \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --set-env-vars "SPREADSHEET_ID=${SPREADSHEET_ID},LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN},LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET}" \
        --max-instances 10 \
        --memory 512Mi \
        --timeout 300

    if [ $? -eq 0 ]; then
        print_success "部署成功！"
    else
        print_error "部署失敗"
        exit 1
    fi
}

# 函式：顯示服務資訊
show_service_info() {
    print_step "取得服務資訊..."

    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --platform managed \
        --region "$REGION" \
        --format 'value(status.url)')

    echo ""
    echo "=========================================="
    echo -e "${GREEN}部署完成！${NC}"
    echo "=========================================="
    echo "服務名稱: $SERVICE_NAME"
    echo "區域: $REGION"
    echo "服務 URL: $SERVICE_URL"
    echo ""
    echo "Webhook URL: ${SERVICE_URL}/webhook"
    echo ""
    echo "下一步："
    echo "1. 前往 LINE Developers Console"
    echo "2. 設定 Webhook URL 為: ${SERVICE_URL}/webhook"
    echo "3. 驗證 Webhook"
    echo "4. 發送測試訊息"
    echo "=========================================="
}

# 主流程
main() {
    echo ""
    echo "=========================================="
    echo "  LINE Bot Cloud Run 部署腳本"
    echo "=========================================="
    echo ""

    check_requirements
    check_gcp_config
    build_image
    push_image
    deploy_to_cloudrun
    show_service_info
}

# 執行主流程
main
