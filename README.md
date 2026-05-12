# IG Autopilot — 工程師爸爸帳號自動化系統

每天 08:00 自動執行：生成文案 → AI 產圖 → 上傳發布 → Telegram 通知
每天 09:00 自動執行：抓取 Insights → Claude 分析 → 推送每日報告

## 快速開始

```bash
cd /Users/chris/Desktop/AI_IG_RUN
chmod +x setup.sh
./setup.sh
```

然後編輯 `.env`，填入所有 API Key。

## 前置準備

1. **IG 帳號**：設定 → 帳號 → 切換為「創作者帳號」
2. **Facebook Page**：創作者帳號需綁定 FB Page 才能使用 Graph API
3. **Meta for Developers**：
   - 建立新 App → 加入 Instagram Graph API
   - 取得 Short-lived Token → 換成 Long-lived Token（60天）
   - 需要 permissions：`instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`
4. **API Keys**：填入 `.env`

## 手動執行

```bash
source venv/bin/activate

# 發今天的貼文
python main.py

# 產生數據報告
python report.py
```

## 自動排程（cron）

```bash
crontab -e
```

加入以下兩行：

```
0 8 * * * cd /Users/chris/Desktop/AI_IG_RUN && ./venv/bin/python main.py >> logs/main.log 2>&1
0 9 * * * cd /Users/chris/Desktop/AI_IG_RUN && ./venv/bin/python report.py >> logs/report.log 2>&1
```

## 專案結構

```
AI_IG_RUN/
├── main.py              # 每日發文主腳本
├── report.py            # 每日數據報告
├── requirements.txt
├── setup.sh
├── .env                 # API Keys（不進 git）
├── config/
│   ├── content_calendar.json   # 30天內容排程
│   └── prompts.py              # Claude prompt 模板
├── services/
│   ├── claude_service.py       # 文案生成
│   ├── image_service.py        # AI 產圖
│   ├── cloud_service.py        # 圖片上傳
│   ├── ig_service.py           # IG Graph API
│   └── notify_service.py       # Telegram 通知
├── data/
│   ├── publish_log.json        # 發布紀錄
│   └── performance_history.json
└── output/
    ├── YYYY-MM-DD/
    │   ├── cover.jpg
    │   ├── post_package.json
    │   └── today_brief.md
    └── reports/
        └── daily_report_YYYY-MM-DD.md
```

## 成本估算

| 服務 | 費用 |
|------|------|
| Claude API (Haiku) | ~$0.01/天 |
| Gemini Imagen | 免費 15張/日 |
| NVIDIA NIM | 免費額度備援 |
| Cloudinary | 免費 25GB |
| Telegram Bot | 免費 |
| **30天總計** | **< $5 USD** |
