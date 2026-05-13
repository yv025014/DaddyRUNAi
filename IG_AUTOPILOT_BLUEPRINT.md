# IG Autopilot — 工程師把拔帳號自動化系統
> **Living Document** — 記錄現在實際運行的系統架構  
> 帳號：Chris｜工程師把拔 | 路徑：`/Users/chris/Desktop/AI_IG_RUN`  
> 最後更新：2026-05-13

---

## 帳號定位

| 項目 | 內容 |
|------|------|
| 帳號名稱 | Chris｜工程師把拔 |
| 主角 | Chris（全端工程師，.NET/React/MSSQL）＋女兒 Anna（5歲） |
| 稱謂 | 自稱「把拔」，絕不用「爸爸」 |
| 風格 | 幽默諧音梗：工程師術語 × 親子日常，有溫度的真實崩潰 |
| 內容形式 | **5頁韓漫 webtoon 繪本輪播**（IG Carousel）|
| 發文時間 | 每天早上 08:00（cron 自動） |

---

## 內容三支柱

| 支柱 | 名稱 | 方向 |
|:---:|------|------|
| A | 把拔的育兒 Debug | 工程師術語 × 親子崩潰，諧音梗主力 |
| B | Anna 與把拔的冒險 | 週末出遊、台灣景點、Anna 神邏輯語錄 |
| C | 工程師白話課 | 把技術概念用超白話比喻，Anna 是白話翻譯官 |

### 諧音梗模板

```
[工程師術語]：[親子情境描述]

例：
404 把拔 Not Found：帶 Anna 去全聯，把拔在零食區消失了
Stack Overflow：Anna 問了一百個為什麼的週末下午
Deploy 失敗：把拔第一次煮咖哩，成品不如預期
Dark Mode：哄 Anna 睡覺時，把拔自己先睡著了
技術債到期：把拔欠 Anna 的五個承諾都在今天被追討
```

---

## 系統架構

```
每天 08:00 cron
       │
       ▼
  main.py
       │
       ├── Phase 1：Gemini 2.5 Flash 生成故事
       │     └── 5個場景 × (story_text + image_prompt)
       │
       ├── Phase 2：InstantID 產 5 張插圖
       │     ├── 主要：InstantX/InstantID HF Space（免費）
       │     │         └── chris_face_crop.png → 鎖定臉部 ID
       │     ├── 備援：Novita.ai IP-Adapter（$0.002/張）
       │     ├── 備援：fal.ai FLUX Kontext（付費）
       │     ├── 備援：Segmind consistent-character（需 credits）
       │     └── 最終備援：HuggingFace FLUX.1-schnell（免費，無 ref）
       │
       ├── Phase 3：Cloudinary 上傳取得公開 URL
       │
       └── Phase 4：Instagram Graph API 發布輪播貼文
                     └── Telegram 通知發布結果

每天 09:00 cron
       │
       ▼
  report.py
       └── IG Insights → Gemini 分析 → Telegram 推播
```

---

## 角色系統

### 參考圖來源
```
ref/
├── 人物參考圖.png          ← 角色三視圖（正面/側面/背面）
├── chris_face_crop.png     ← Chris 臉部裁切（InstantID 用）
├── chris_front.png         ← Chris 全身正面（pose 參考）
├── anna_face_crop.png      ← Anna 臉部裁切
└── anna_front.png          ← Anna 全身正面
```

> 換了新三視圖時執行：`python tools/generate_ref_crops.py`

### Chris 人設
- 短棕色頭髮、**無眼鏡**、粉色 T-shirt、卡其短褲、Apple Watch
- prompt 必寫：`short dark brown hair, NO glasses, pink t-shirt, khaki shorts, Apple Watch`

### Anna 人設
- 棕色 bob 髮型、直瀏海、淡藍色小雛菊洋裝、白色涼鞋
- prompt 必寫：`brown bob hair with straight bangs, light blue dress with daisy embroidery, white sandals`

---

## 圖片生成優先順序

| 優先 | 服務 | 角色一致性 | 費用 | 設定方式 |
|:---:|------|:---:|---:|------|
| 1 | **InstantID（HF Space）** | ✅ 臉部鎖定 | 免費 | 自動，需 `ref/chris_face_crop.png` |
| 2 | Novita.ai IP-Adapter | ✅ 全圖風格 | ~$0.002/張 | `.env` 填 `NOVITA_API_KEY` |
| 3 | fal.ai FLUX Kontext | ✅ 參考圖 | 付費 | `.env` 填 `FAL_API_KEY` |
| 4 | Segmind consistent-character | ✅ 角色 | 需 credits | `.env` 填 `SEGMIND_API_KEY` |
| 5 | HuggingFace FLUX.1-schnell | ❌ 純文字 | 免費 | `.env` 填 `HUGGINGFACE_API_KEY` |

---

## 目錄結構

```
AI_IG_RUN/
├── main.py                      # 每日發文主腳本
├── report.py                    # 每日數據報告
├── requirements.txt
├── setup.sh
├── .env                         # API Keys（不進 git）
├── .env.example
├── config/
│   ├── content_calendar.json    # 30天內容排程（全 carousel 格式）
│   └── prompts.py               # Gemini prompt 模板
├── services/
│   ├── claude_service.py        # 故事生成（實際用 Gemini）
│   ├── image_service.py         # AI 產圖（InstantID 優先）
│   ├── cloud_service.py         # Cloudinary 上傳
│   ├── ig_service.py            # IG Graph API（含輪播）
│   └── notify_service.py        # Telegram 通知
├── ref/
│   ├── 人物參考圖.png            # 角色三視圖（不進 git）
│   ├── chris_face_crop.png      # InstantID 用
│   └── chris_front.png          # pose 用
├── tools/
│   └── generate_ref_crops.py    # 從三視圖自動裁切
└── data/
    ├── publish_log.json
    └── performance_history.json
```

---

## 環境設定（.env）

```env
# 內容生成
GOOGLE_API_KEY=...              # Gemini 2.5 Flash

# 圖片生成（填任一即可，優先順序見上表）
NOVITA_API_KEY=                 # 推薦：充值 $5 可跑 2500 張
FAL_API_KEY=...
SEGMIND_API_KEY=...
HUGGINGFACE_API_KEY=...        # 免費備援，已填

# 圖片託管
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

# Instagram
IG_USER_ID=...
IG_ACCESS_TOKEN=...            # Long-lived token，每 60 天刷新

# 通知
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

---

## Cron 排程

```bash
# 查看現有 cron
crontab -l

# 每天 08:00 發繪本輪播
0 8 * * * cd /Users/chris/Desktop/AI_IG_RUN && ./venv/bin/python main.py >> logs/main.log 2>&1

# 每天 09:00 數據報告
0 9 * * * cd /Users/chris/Desktop/AI_IG_RUN && ./venv/bin/python report.py >> logs/report.log 2>&1

# 每週日 22:00 策略回顧（遠端 agent）
0 22 * * 0 cd /Users/chris/Desktop/AI_IG_RUN && ./venv/bin/python weekly_review.py >> logs/review.log 2>&1
```

---

## 手動執行

```bash
cd /Users/chris/Desktop/AI_IG_RUN
source venv/bin/activate

# 發今天的繪本
python main.py

# 數據報告
python report.py

# 重新裁切角色 crops（換了新三視圖後）
python tools/generate_ref_crops.py
```

---

## 成本估算（30天）

| 服務 | 費用 | 備註 |
|------|---:|------|
| Gemini 2.5 Flash | ~$1 | 每天 5 場景 × 約 500 tokens |
| InstantID HF Space | **免費** | 主要產圖方案 |
| HuggingFace FLUX | **免費** | 備援方案 |
| Cloudinary | **免費** | 25GB 免費方案 |
| Novita.ai (選用) | ~$0.30 | 5 張/天 × 30 天 × $0.002 |
| **30天總計** | **< $2 USD** | InstantID 免費路線 |

---

## 內容日曆摘要（30天諧音梗主題）

| 天 | 支柱 | 主題 |
|:---:|:---:|------|
| 1 | A | 404 把拔 Not Found：帶 Anna 去全聯，把拔在零食區消失了 |
| 2 | A | 無限迴圈：幫 Anna 穿鞋穿了八次的星期一早晨 |
| 3 | C | 什麼是 API？把拔用便當店解釋給 Anna 聽 |
| 4 | B | Stack Overflow：Anna 問了一百個為什麼的週末下午 |
| 5 | A | Deploy 失敗：把拔第一次煮咖哩，成品不如預期 |
| 6 | B | Git merge conflict：把拔和阿嬤都想哄 Anna 睡，發生衝突了 |
| 7 | C | 什麼是資料庫？把拔用玩具箱解釋給 Anna 聽 |
| 8 | A | Debug Mode：Anna 的水壺怎麼都找不到，把拔開始系統性搜索 |
| 9 | B | 版本更新 v5.0：Anna 上幼稚園第一天 |
| 10 | A | API Timeout：等 Anna 刷牙等了二十分鐘的晚上 |
| 11 | C | 什麼是前端後端？把拔用餐廳解釋，Anna 說她要當主廚 |
| 12 | A | 403 Forbidden：Anna 闖進把拔書房偷玩電腦的下午 |
| 13 | B | Cache 清除：帶 Anna 去剪頭髮，她說要剪成公主 |
| 14 | A | Exception Handling：Anna 在賣場突然大哭，把拔的緊急處置 |
| 15 | C | 什麼是 Bug？把拔用積木蓋的城堡倒了來解釋 |
| 16 | B | Dark Mode：哄 Anna 睡覺時，把拔自己先睡著了 |
| 17 | A | Memory Leak：把拔忘了幾件事，Anna 的記憶體卻超清楚 |
| 18 | B | 週末 Sprint：帶 Anna 去動物園的二日衝刺計畫 |
| 19 | C | 什麼是 Git？把拔用橡皮擦解釋「可以反悔」的神奇功能 |
| 20 | A | Code Review：Anna 幫把拔「改」了工作報告，改得很有道理 |
| 21 | A | Hotfix：Anna 膝蓋破皮，把拔的緊急 patch |
| 22 | B | 開源精神：教 Anna 第一次把玩具借給同學 |
| 23 | C | 什麼是 AI？把拔用「很聰明的貓咪」解釋，Anna 說要養一隻 |
| 24 | A | Callback 地獄：Anna 說「等一下」就不見了 |
| 25 | B | Load Balancing：把拔同時在 WFH 上班和陪 Anna 畫圖 |
| 26 | A | 技術債到期：把拔欠 Anna 的五個承諾都在今天被追討 |
| 27 | C | 什麼是 for 迴圈？把拔用「再說一次睡前故事」來解釋 |
| 28 | B | Pull Request：Anna 第一次主動說對不起，把拔 approved |
| 29 | A | Single Point of Failure：把拔生病了，家裡系統全面崩潰 |
| 30 | A | Production 上線：30 天工程師把拔的繪本日記大結局 |

---

## 已知問題與注意事項

1. **InstantID 佇列時間**：HF Space 尖峰時段可能需要 30-60 秒，5 張圖約 2-5 分鐘
2. **IG Token 效期**：Long-lived token 60 天到期，`ig_service.refresh_token()` 需手動呼叫
3. **Gemini JSON 截斷**：如果 max_output_tokens 不夠，`_clean_json` 會失敗，目前設 4000
4. **Anna 服裝漂移**：InstantID 只鎖定 Chris 的臉，Anna 靠 prompt 控制，偶爾顏色會偏

---

*由 Claude AI 協助建置與維護 | GitHub: yv025014/DaddyRUNAi*
