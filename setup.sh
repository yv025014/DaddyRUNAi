#!/bin/bash
echo "=== IG Autopilot 環境設定 ==="

# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝套件
pip install --upgrade pip
pip install -r requirements.txt

# 建立必要目錄
mkdir -p data output/reports logs

# 複製 .env 範本
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅ 已建立 .env，請填入你的 API Key"
else
  echo "ℹ️  .env 已存在，跳過"
fi

echo ""
echo "=== 設定完成 ==="
echo ""
echo "下一步："
echo "1. 編輯 .env，填入所有 API Key"
echo "2. 將 IG 帳號切換為「創作者帳號」"
echo "3. 至 Meta for Developers 建立 App 並取得 Access Token"
echo "4. 執行 python main.py 測試第一天"
echo ""
echo "Cron 設定（每天 08:00 發文，09:00 報告）："
echo "0 8 * * * cd /Users/chris/Desktop/AI_IG_RUN && ./venv/bin/python main.py >> logs/main.log 2>&1"
echo "0 9 * * * cd /Users/chris/Desktop/AI_IG_RUN && ./venv/bin/python report.py >> logs/report.log 2>&1"
