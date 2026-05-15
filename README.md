# IG Autopilot — 工程師把拔帳號自動化系統

> 「用工程師腦袋 debug 人生」— 全端工程師 Chris × 五歲女兒 Anna × 媽咪的繪本輪播帳號

每天 08:00 自動執行：Gemini 生成腳本 → 角色立繪合成輪播圖 → 上傳 Cloudinary → 發布 IG → Discord 通知
每天 09:00 自動執行：抓取 Insights → Gemini 分析 → 推送每日報告

---

## 帳號定位

**三大內容支柱：**

| 支柱 | 主題 | 公式 | 演算法目的 |
|------|------|------|----------|
| `tech` 技術白話 | 複雜技術講到人聽得懂 | Chris解釋 → Anna秒懂 → 媽咪認證 | 收藏＋轉發 |
| `workplace` IT職場奇聞 | User的神奇需求 | User奇怪需求 → Chris困惑 → Anna拆穿 | 留言＋共鳴 |
| `office` 大人腹黑學 | 公司最荒謬的真相 | 荒謬場景 → Chris當事人 → 媽咪補刀 | 破圈轉發 |

---

## 系統架構

```
main.py (08:00)
├── Phase 1: Gemini 生成繪本腳本 (JSON)
│   └── speaker / mood / story_text / background per scene
├── Phase 2: composite_service 合成輪播圖
│   ├── 封面頁（背景 + 標題）
│   ├── 對話頁 × 5（背景 + 角色立繪 + 文字框）
│   └── 金句頁（深色背景 + 大字）
├── Phase 3: Cloudinary 上傳（取得公開 URL）
└── Phase 4: IG Graph API 發布輪播

report.py (09:00)
├── IG Graph API 抓取 Insights
├── 結構化報告（發文總覽表 + 各篇成效數據）
└── Gemini 分析（數據解讀 + 明日策略建議）
```

---

## 角色系統

角色圖為固定立繪 PNG，放在 `assets/characters/`，每次合成時自動去背疊加，零 AI 產圖成本。

| 角色 | 可用情緒 |
|------|---------|
| chris | normal / proud / defeated / surprised / thinking / confused / embarrassed |
| anna | happy / smirk / pointing / proud / curious |
| mom | smiling / facepalm / proud / deadpan / skeptical |

背景圖放在 `assets/backgrounds/`：`dining_room` / `living_room` / `office_desk` / `bedroom` / `outdoor_park`

---

## 快速開始

```bash
cd /Users/chris/Desktop/AI_IG_RUN
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

複製 `.env.example` 填入 API Key：

```bash
cp .env.example .env
```

---

## 必要環境變數

```env
GOOGLE_API_KEY=          # Gemini API（腳本生成 + 報告分析）
INSTAGRAM_USER_ID=       # IG 帳號 User ID
INSTAGRAM_ACCESS_TOKEN=  # IG Graph API Long-lived Token（60天效期）
CLOUDINARY_CLOUD_NAME=   # 圖片託管
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
DISCORD_WEBHOOK_URL=     # 通知用 Webhook
```

---

## 手動執行

```bash
source venv/bin/activate

# 發今天的貼文
python main.py

# 產生數據報告
python report.py
```

---

## 自動排程（cron）

```bash
crontab -e
```

加入：

```
0 8 * * * cd /Users/chris/Desktop/AI_IG_RUN && ./venv/bin/python main.py >> logs/main.log 2>&1
0 9 * * * cd /Users/chris/Desktop/AI_IG_RUN && ./venv/bin/python report.py >> logs/report.log 2>&1
```

---

## 專案結構

```
AI_IG_RUN/
├── main.py                      # 每日發文主腳本
├── report.py                    # 每日數據報告
├── config/
│   ├── content_calendar.json    # 30天內容排程（含 script_hint）
│   └── prompts.py               # Gemini prompt 模板
├── services/
│   ├── llm_service.py           # Gemini 腳本生成 + 報告分析
│   ├── composite_service.py     # 角色立繪 + 背景 + 文字合成
│   ├── cloud_service.py         # Cloudinary 上傳
│   ├── ig_service.py            # IG Graph API 發布 + Insights
│   └── notify_service.py        # Discord Webhook 通知
├── assets/
│   ├── characters/              # 角色立繪 PNG（chris / anna / mom）
│   └── backgrounds/             # 場景背景圖
├── data/
│   ├── publish_log.json         # 發布紀錄
│   └── performance_history.json # 每日 Insights 快照
└── output/
    ├── YYYY-MM-DD/
    │   ├── slide_01.jpg ~ slide_07.jpg  # 輪播圖
    │   ├── today_brief.md               # 今日腳本簡報
    │   └── post_package.json            # 完整發文包
    └── reports/
        └── daily_report_YYYY-MM-DD.md
```

---

## 成本估算

| 服務 | 費用 |
|------|------|
| Gemini API | 免費額度內 |
| 角色立繪合成 | $0（本地 Pillow + rembg） |
| Cloudinary | 免費 25GB |
| Discord Webhook | 免費 |
| **30天總計** | **$0** |
