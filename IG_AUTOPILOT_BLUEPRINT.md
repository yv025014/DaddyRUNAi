# IG Autopilot — 工程師爸爸帳號自動化系統

> 此文件由 Claude 生成，供 Claude Code 執行建置。  
> 目標：在 `/Users/chris/Desktop/AI_IG_RUN` 建立完整的 IG 自動化發文系統。

---

## 任務總覽

請依序完成以下所有任務：

1. 建立專案目錄結構
2. 建立所有 Python 模組
3. 建立設定檔與內容日曆
4. 建立 cron 排程說明
5. 建立 `.env.example`

---

## 任務 1：建立目錄結構

在 `/Users/chris/Desktop/AI_IG_RUN` 建立以下目錄：

```
AI_IG_RUN/
├── services/
├── config/
├── data/
└── output/
```

---

## 任務 2：建立 `requirements.txt`

路徑：`/Users/chris/Desktop/AI_IG_RUN/requirements.txt`

內容：

```
anthropic>=0.25.0
google-generativeai>=0.5.0
requests>=2.31.0
cloudinary>=1.36.0
python-telegram-bot>=20.0
python-dotenv>=1.0.0
Pillow>=10.0.0
schedule>=1.2.0
```

---

## 任務 3：建立 `.env.example`

路徑：`/Users/chris/Desktop/AI_IG_RUN/.env.example`

內容：

```
# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx

# Google Gemini Imagen
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxx

# NVIDIA NIM (備援產圖)
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxx

# Cloudinary (圖片公開 URL)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Instagram Graph API
IG_USER_ID=123456789012345
IG_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxx

# Telegram Bot 通知
TELEGRAM_BOT_TOKEN=1234567890:AAxxxxxxxxxxxxxxxx
TELEGRAM_CHAT_ID=123456789
```

---

## 任務 4：建立 `config/content_calendar.json`

路徑：`/Users/chris/Desktop/AI_IG_RUN/config/content_calendar.json`

內容：

```json
{
  "account_name": "工程師爸爸",
  "niche": "全端工程師（.NET / React / MSSQL）＋五歲女兒爸爸",
  "bio": "👨‍💻 全端工程師 | .NET × React × MSSQL\n👧 五歲女兒的爸\n⚡ 用工程師腦袋 debug 人生\n▼ 30天工程師爸爸實驗進行中",
  "pillars": {
    "A": {
      "name": "工程師的生活 debug",
      "description": "用工程師術語比喻日常困境，讓非技術受眾也有共鳴",
      "image_style": "flat illustration, minimalist, tech + daily life concept, warm tones, no text in image"
    },
    "B": {
      "name": "爸爸的親子時刻",
      "description": "溫度感親子內容，女兒背影，台灣在地景點與生活",
      "image_style": "warm lifestyle illustration, parent and child silhouette, soft colors, cozy atmosphere"
    },
    "C": {
      "name": "輕技術知識炸彈",
      "description": "把技術觀念用白話說，讓非工程師也懂，工程師也有共鳴",
      "image_style": "clean tech explainer illustration, simple diagram style, blue and purple tones, no text in image"
    }
  },
  "schedule": [
    {"day": 1,  "type": "reels", "pillar": "A", "theme": "工程師爸爸的30天AI實驗開始了"},
    {"day": 2,  "type": "story", "pillar": "A", "theme": "互動：你猜工程師帶小孩最頭痛的是？"},
    {"day": 3,  "type": "reels", "pillar": "C", "theme": "什麼是 API？用便當解釋給爸媽聽"},
    {"day": 4,  "type": "story", "pillar": "B", "theme": "今日女兒語錄"},
    {"day": 5,  "type": "photo", "pillar": "A", "theme": "工程師的工作區長這樣"},
    {"day": 6,  "type": "reels", "pillar": "B", "theme": "週末帶五歲女兒去的台灣景點"},
    {"day": 7,  "type": "story", "pillar": "C", "theme": "投票：你知道前端和後端的差別嗎？"},
    {"day": 8,  "type": "reels", "pillar": "A", "theme": "我把育兒時間排成 sprint"},
    {"day": 9,  "type": "story", "pillar": "A", "theme": "互動問答：你的人生最大 bug 是什麼？"},
    {"day": 10, "type": "reels", "pillar": "C", "theme": "後端工程師的一天長這樣"},
    {"day": 11, "type": "photo", "pillar": "B", "theme": "和女兒一起的週末早晨"},
    {"day": 12, "type": "reels", "pillar": "A", "theme": "育兒就是維護 legacy code"},
    {"day": 13, "type": "story", "pillar": "C", "theme": "小測驗：HTTP 是什麼？"},
    {"day": 14, "type": "reels", "pillar": "B", "theme": "工程師爸爸的親子食譜"},
    {"day": 15, "type": "photo", "pillar": "A", "theme": "下班後的工程師模式"},
    {"day": 16, "type": "reels", "pillar": "C", "theme": "為什麼我選 React 不選 Vue"},
    {"day": 17, "type": "story", "pillar": "B", "theme": "女兒問了我一個答不出的問題"},
    {"day": 18, "type": "reels", "pillar": "A", "theme": "工程師買東西前會做什麼"},
    {"day": 19, "type": "photo", "pillar": "C", "theme": "我的開發工具組合 2025"},
    {"day": 20, "type": "reels", "pillar": "B", "theme": "台灣工程師爸爸的週末行程"},
    {"day": 21, "type": "story", "pillar": "A", "theme": "這30天實驗中期回顧投票"},
    {"day": 22, "type": "reels", "pillar": "C", "theme": "什麼是資料庫？用圖書館解釋"},
    {"day": 23, "type": "photo", "pillar": "A", "theme": "工程師的 side project：帶娃"},
    {"day": 24, "type": "reels", "pillar": "B", "theme": "帶女兒學程式的第一步"},
    {"day": 25, "type": "story", "pillar": "C", "theme": "互動：你最想學的技術是什麼？"},
    {"day": 26, "type": "reels", "pillar": "A", "theme": "工程師式的親子溝通技巧"},
    {"day": 27, "type": "photo", "pillar": "B", "theme": "女兒的第一個程式（畫圖）"},
    {"day": 28, "type": "reels", "pillar": "C", "theme": ".NET vs Node.js 我的真實感受"},
    {"day": 29, "type": "story", "pillar": "A", "theme": "實驗倒數！你有追到嗎？"},
    {"day": 30, "type": "reels", "pillar": "A", "theme": "30天工程師爸爸AI實驗大結局"}
  ]
}
```

---

## 任務 5：建立 `config/prompts.py`

路徑：`/Users/chris/Desktop/AI_IG_RUN/config/prompts.py`

內容：

```python
SYSTEM_PROMPT = """
你是「工程師爸爸」這個 IG 帳號的資深社群經營專家。
帳號定位：全端工程師（.NET / React / MSSQL）＋五歲女兒的爸爸，台灣在地。
核心人設：用工程師腦袋 debug 人生，真實、有溫度、輕技術。
目標受眾：台灣工程師、科技業父母、想了解程式的一般人。
語言：繁體中文，口語化，避免過度正式。
"""

def get_content_prompt(day: int, pillar: str, pillar_name: str, theme: str, content_type: str) -> str:
    return f"""
今天是第 {day} 天，內容支柱：{pillar}（{pillar_name}），主題：{theme}，格式：{content_type}。

請生成以下內容，以 JSON 格式回覆，不要有其他文字：

{{
  "script": "Reels 腳本（如為 reels 類型），包含：Hook（0-3秒文字）、主體3個重點、結尾CTA。如為 photo/story 類型則填入貼文概念說明。",
  "caption": "IG 貼文文案，約 100-150 字，包含 emoji，口語化繁體中文，結尾留一個引發留言的問題",
  "hashtags": ["標籤1", "標籤2", "標籤3", "標籤4", "標籤5"],
  "image_prompt": "給 Gemini Imagen 的英文圖片生成 prompt，描述一張適合這篇貼文封面的插圖，flat illustration 風格，不含文字",
  "story_text": "如果有限時動態要更新，這裡是限時動態的互動問題或內容，否則填 null"
}}
"""

def get_report_prompt(posts_data: list, insights_data: dict) -> str:
    return f"""
以下是過去幾天的 IG 貼文數據與成效：

發文紀錄：
{posts_data}

各貼文 Insights：
{insights_data}

請生成一份繁體中文的「每日成效報告與策略修正建議」，包含：
1. 數據摘要（哪支表現最好/最差，原因分析）
2. 演算法訊號解讀（完播率、存數、留言哪個最強）
3. 明日內容策略建議（主題微調、腳本方向、發文時間建議）
4. 一句鼓勵的話給帳號主理人

請用 Markdown 格式輸出，加上適當標題。
"""
```

---

## 任務 6：建立 `services/claude_service.py`

路徑：`/Users/chris/Desktop/AI_IG_RUN/services/claude_service.py`

內容：

```python
import json
import anthropic
from config.prompts import SYSTEM_PROMPT, get_content_prompt, get_report_prompt


def generate_content(day: int, pillar: str, pillar_name: str, theme: str, content_type: str) -> dict:
    """呼叫 Claude API 生成今日貼文內容"""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": get_content_prompt(day, pillar, pillar_name, theme, content_type)
            }
        ]
    )

    raw = message.content[0].text.strip()
    # 移除可能的 markdown code block 包裝
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    return json.loads(raw)


def generate_report(posts_data: list, insights_data: dict) -> str:
    """呼叫 Claude API 生成每日報告"""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": get_report_prompt(posts_data, insights_data)
            }
        ]
    )

    return message.content[0].text
```

---

## 任務 7：建立 `services/image_service.py`

路徑：`/Users/chris/Desktop/AI_IG_RUN/services/image_service.py`

內容：

```python
import os
import base64
import requests
from pathlib import Path
import google.generativeai as genai
from PIL import Image
import io


def generate_image_gemini(prompt: str, output_path: str) -> bool:
    """使用 Gemini Imagen 3 生成圖片"""
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        imagen = genai.ImageGenerationModel("imagen-3.0-generate-002")
        result = imagen.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="1:1",
        )
        if result.images:
            img = result.images[0]
            img_bytes = img._image_bytes
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            print(f"[Gemini] 圖片已儲存：{output_path}")
            return True
    except Exception as e:
        print(f"[Gemini] 產圖失敗：{e}")
    return False


def generate_image_nvidia(prompt: str, output_path: str) -> bool:
    """使用 NVIDIA NIM (SDXL) 生成圖片（備援）"""
    try:
        api_key = os.getenv("NVIDIA_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "text_prompts": [{"text": prompt, "weight": 1}],
            "cfg_scale": 7,
            "sampler": "K_DPM_2_ANCESTRAL",
            "seed": 0,
            "steps": 25,
            "width": 1024,
            "height": 1024,
        }
        resp = requests.post(
            "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-xl",
            headers=headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        b64 = data["artifacts"][0]["base64"]
        img_bytes = base64.b64decode(b64)
        with open(output_path, "wb") as f:
            f.write(img_bytes)
        print(f"[NVIDIA] 圖片已儲存：{output_path}")
        return True
    except Exception as e:
        print(f"[NVIDIA] 產圖失敗：{e}")
    return False


def generate_image(prompt: str, output_path: str) -> bool:
    """主要入口：先試 Gemini，失敗則用 NVIDIA"""
    if generate_image_gemini(prompt, output_path):
        return True
    print("[Image] Gemini 失敗，改用 NVIDIA 備援...")
    return generate_image_nvidia(prompt, output_path)


def resize_for_instagram(input_path: str, output_path: str = None):
    """確保圖片符合 IG 規格（1:1，最小 1080x1080）"""
    if output_path is None:
        output_path = input_path
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img = img.resize((1080, 1080), Image.LANCZOS)
        img.save(output_path, "JPEG", quality=95)
    print(f"[Image] 已調整為 IG 規格：{output_path}")
```

---

## 任務 8：建立 `services/cloud_service.py`

路徑：`/Users/chris/Desktop/AI_IG_RUN/services/cloud_service.py`

內容：

```python
import os
import cloudinary
import cloudinary.uploader


def upload_image(local_path: str, public_id: str) -> str:
    """上傳圖片至 Cloudinary，回傳公開 URL"""
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    )

    result = cloudinary.uploader.upload(
        local_path,
        public_id=public_id,
        overwrite=True,
        resource_type="image",
        format="jpg",
    )

    url = result.get("secure_url")
    print(f"[Cloudinary] 上傳成功：{url}")
    return url
```

---

## 任務 9：建立 `services/ig_service.py`

路徑：`/Users/chris/Desktop/AI_IG_RUN/services/ig_service.py`

內容：

```python
import os
import time
import requests


BASE_URL = "https://graph.instagram.com/v19.0"


def _get_credentials():
    return os.getenv("IG_USER_ID"), os.getenv("IG_ACCESS_TOKEN")


def create_media_container(image_url: str, caption: str) -> str | None:
    """建立 IG media container，回傳 container_id"""
    user_id, token = _get_credentials()
    url = f"{BASE_URL}/{user_id}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": token,
    }
    resp = requests.post(url, data=payload, timeout=30)
    data = resp.json()

    if "id" in data:
        container_id = data["id"]
        print(f"[IG] Container 建立成功：{container_id}")
        return container_id
    else:
        print(f"[IG] Container 建立失敗：{data}")
        return None


def wait_for_container(container_id: str, max_wait: int = 60) -> bool:
    """等待 container 處理完成"""
    _, token = _get_credentials()
    url = f"{BASE_URL}/{container_id}"
    params = {"fields": "status_code", "access_token": token}

    for i in range(max_wait // 5):
        resp = requests.get(url, params=params, timeout=10)
        status = resp.json().get("status_code", "")
        print(f"[IG] Container 狀態：{status}（{i*5}s）")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            print("[IG] Container 處理錯誤")
            return False
        time.sleep(5)

    print("[IG] Container 等待逾時")
    return False


def publish_media(container_id: str) -> str | None:
    """發布已就緒的 container，回傳 media_id"""
    user_id, token = _get_credentials()
    url = f"{BASE_URL}/{user_id}/media_publish"
    payload = {
        "creation_id": container_id,
        "access_token": token,
    }
    resp = requests.post(url, data=payload, timeout=30)
    data = resp.json()

    if "id" in data:
        media_id = data["id"]
        print(f"[IG] 發布成功！Media ID：{media_id}")
        return media_id
    else:
        print(f"[IG] 發布失敗：{data}")
        return None


def post_to_instagram(image_url: str, caption: str) -> str | None:
    """完整發布流程：建立 container → 等待 → 發布"""
    container_id = create_media_container(image_url, caption)
    if not container_id:
        return None

    if not wait_for_container(container_id):
        return None

    return publish_media(container_id)


def get_post_insights(media_id: str) -> dict:
    """取得貼文 Insights 數據"""
    _, token = _get_credentials()
    url = f"{BASE_URL}/{media_id}/insights"
    params = {
        "metric": "impressions,reach,likes,comments,saves,shares",
        "access_token": token,
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()

    insights = {}
    for item in data.get("data", []):
        insights[item["name"]] = item["values"][0]["value"] if item.get("values") else 0

    return insights


def get_recent_posts(limit: int = 7) -> list:
    """取得最近幾篇貼文的 ID 與時間"""
    user_id, token = _get_credentials()
    url = f"{BASE_URL}/{user_id}/media"
    params = {
        "fields": "id,timestamp,caption",
        "limit": limit,
        "access_token": token,
    }
    resp = requests.get(url, params=params, timeout=10)
    return resp.json().get("data", [])


def refresh_token() -> str | None:
    """刷新 Long-lived Token（每 50 天呼叫一次）"""
    _, token = _get_credentials()
    url = "https://graph.instagram.com/refresh_access_token"
    params = {
        "grant_type": "ig_refresh_token",
        "access_token": token,
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    new_token = data.get("access_token")
    if new_token:
        print(f"[IG] Token 刷新成功，有效期：{data.get('expires_in')} 秒")
    return new_token
```

---

## 任務 10：建立 `services/notify_service.py`

路徑：`/Users/chris/Desktop/AI_IG_RUN/services/notify_service.py`

內容：

```python
import os
import requests


def send_telegram(message: str) -> bool:
    """發送 Telegram 通知"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("[Notify] Telegram 未設定，跳過通知")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }
    resp = requests.post(url, json=payload, timeout=10)
    if resp.status_code == 200:
        print("[Notify] Telegram 通知已發送")
        return True
    else:
        print(f"[Notify] Telegram 發送失敗：{resp.text}")
        return False
```

---

## 任務 11：建立 `main.py`

路徑：`/Users/chris/Desktop/AI_IG_RUN/main.py`

內容：

```python
"""
IG Autopilot — 每日主腳本
執行方式：python main.py
Cron：0 8 * * * /usr/bin/python3 /Users/chris/Desktop/AI_IG_RUN/main.py
"""

import os
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from services.claude_service import generate_content
from services.image_service import generate_image, resize_for_instagram
from services.cloud_service import upload_image
from services.ig_service import post_to_instagram
from services.notify_service import send_telegram

# ── 路徑設定 ──────────────────────────────────────────
BASE_DIR = Path(__file__).parent
CALENDAR_PATH = BASE_DIR / "config" / "content_calendar.json"
LOG_PATH = BASE_DIR / "data" / "publish_log.json"
OUTPUT_BASE = BASE_DIR / "output"


def load_calendar() -> dict:
    with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_log() -> list:
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_log(log: list):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def get_today_schedule(calendar: dict) -> dict | None:
    """根據已發布天數決定今天要發第幾天的內容"""
    log = load_log()
    published_days = {entry["day"] for entry in log if entry.get("status") == "published"}
    schedule = calendar["schedule"]

    for item in schedule:
        if item["day"] not in published_days:
            return item
    return None  # 30 天全部完成


def format_caption(content: dict) -> str:
    """組合文案 + 標籤"""
    tags = " ".join([f"#{t.lstrip('#')}" for t in content.get("hashtags", [])])
    return f"{content['caption']}\n\n{tags}"


def save_brief(output_dir: Path, day: int, schedule_item: dict, content: dict):
    """儲存今日簡報 markdown"""
    brief_path = output_dir / "today_brief.md"
    lines = [
        f"# 今日發文簡報 — 第 {day} 天",
        f"",
        f"**日期**：{datetime.date.today()}",
        f"**支柱**：{schedule_item['pillar']} — {schedule_item.get('theme', '')}",
        f"**格式**：{schedule_item['type']}",
        f"",
        f"## 腳本",
        f"",
        content.get("script", ""),
        f"",
        f"## 貼文文案",
        f"",
        content.get("caption", ""),
        f"",
        f"## 標籤",
        f"",
        " ".join([f"#{t}" for t in content.get("hashtags", [])]),
        f"",
        f"## 圖片 Prompt",
        f"",
        content.get("image_prompt", ""),
    ]
    brief_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[Main] 簡報已儲存：{brief_path}")


def run():
    print("=" * 50)
    print(f"[Main] IG Autopilot 啟動 — {datetime.datetime.now()}")
    print("=" * 50)

    # 1. 讀取日曆
    calendar = load_calendar()
    today_item = get_today_schedule(calendar)

    if today_item is None:
        msg = "🎉 30天計劃全部完成！"
        print(f"[Main] {msg}")
        send_telegram(msg)
        return

    day = today_item["day"]
    pillar = today_item["pillar"]
    pillar_info = calendar["pillars"][pillar]
    theme = today_item["theme"]
    content_type = today_item["type"]

    print(f"[Main] 今日任務：第 {day} 天 | 支柱 {pillar} | {theme}")

    # 2. 建立輸出目錄
    today_str = datetime.date.today().isoformat()
    output_dir = OUTPUT_BASE / today_str
    output_dir.mkdir(parents=True, exist_ok=True)

    # 3. Phase 1 — 生成文案
    print("\n[Phase 1] 呼叫 Claude 生成文案...")
    content = generate_content(day, pillar, pillar_info["name"], theme, content_type)
    save_brief(output_dir, day, today_item, content)

    # 4. Phase 2 — 產圖
    print("\n[Phase 2] 生成封面圖片...")
    image_path = str(output_dir / "cover.jpg")
    img_prompt = content.get("image_prompt", pillar_info["image_style"])
    success = generate_image(img_prompt, image_path)

    if not success:
        msg = f"⚠️ 第 {day} 天 — 圖片生成失敗，請手動處理"
        print(f"[Main] {msg}")
        send_telegram(msg)
        return

    resize_for_instagram(image_path)

    # 5. Phase 3 — 上傳圖片
    print("\n[Phase 3] 上傳圖片至 Cloudinary...")
    public_id = f"ig_autopilot/day_{day:02d}_{today_str}"
    image_url = upload_image(image_path, public_id)

    # 6. 儲存發文包
    package_path = output_dir / "post_package.json"
    package = {
        "day": day,
        "date": today_str,
        "pillar": pillar,
        "theme": theme,
        "content_type": content_type,
        "content": content,
        "image_url": image_url,
        "caption": format_caption(content),
    }
    package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    # 7. Phase 4 — 發布至 IG
    print("\n[Phase 4] 發布至 Instagram...")
    caption = format_caption(content)
    media_id = post_to_instagram(image_url, caption)

    # 8. 記錄 log
    log = load_log()
    log_entry = {
        "day": day,
        "date": today_str,
        "theme": theme,
        "media_id": media_id,
        "image_url": image_url,
        "status": "published" if media_id else "failed",
    }
    log.append(log_entry)
    save_log(log)

    # 9. 通知
    if media_id:
        msg = (
            f"✅ *第 {day} 天發布成功！*\n"
            f"主題：{theme}\n"
            f"Media ID：`{media_id}`\n"
            f"明早 09:00 會收到昨日數據報告 📊"
        )
    else:
        msg = f"❌ 第 {day} 天發布失敗，請檢查 log"

    send_telegram(msg)
    print(f"\n[Main] 完成！狀態：{'成功' if media_id else '失敗'}")


if __name__ == "__main__":
    run()
```

---

## 任務 12：建立 `report.py`

路徑：`/Users/chris/Desktop/AI_IG_RUN/report.py`

內容：

```python
"""
IG Autopilot — 每日數據報告腳本
執行方式：python report.py
Cron：0 9 * * * /usr/bin/python3 /Users/chris/Desktop/AI_IG_RUN/report.py
"""

import os
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from services.ig_service import get_recent_posts, get_post_insights
from services.claude_service import generate_report
from services.notify_service import send_telegram

BASE_DIR = Path(__file__).parent
LOG_PATH = BASE_DIR / "data" / "publish_log.json"
HISTORY_PATH = BASE_DIR / "data" / "performance_history.json"
REPORTS_DIR = BASE_DIR / "output" / "reports"


def load_log() -> list:
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def load_history() -> list:
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history: list):
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def run():
    print("=" * 50)
    print(f"[Report] 數據報告腳本啟動 — {datetime.datetime.now()}")
    print("=" * 50)

    # 取得最近 7 篇貼文
    recent_posts = get_recent_posts(limit=7)
    if not recent_posts:
        print("[Report] 無法取得貼文資料")
        send_telegram("⚠️ 報告腳本：無法取得 IG 貼文資料")
        return

    # 逐一取得 Insights
    log = load_log()
    log_map = {entry.get("media_id"): entry for entry in log if entry.get("media_id")}

    insights_data = {}
    posts_data = []

    for post in recent_posts:
        media_id = post["id"]
        insights = get_post_insights(media_id)
        insights_data[media_id] = insights

        log_entry = log_map.get(media_id, {})
        posts_data.append({
            "media_id": media_id,
            "date": post.get("timestamp", "")[:10],
            "theme": log_entry.get("theme", post.get("caption", "")[:30]),
            "insights": insights,
        })

    # 更新 performance_history
    history = load_history()
    today_str = datetime.date.today().isoformat()
    history.append({
        "date": today_str,
        "posts": posts_data,
    })
    save_history(history)

    # 呼叫 Claude 生成報告
    print("[Report] 呼叫 Claude 生成分析報告...")
    report_text = generate_report(posts_data, insights_data)

    # 儲存報告
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"daily_report_{today_str}.md"
    report_path.write_text(report_text, encoding="utf-8")
    print(f"[Report] 報告已儲存：{report_path}")

    # Telegram 推播摘要（前 500 字）
    summary = report_text[:500] + "\n\n📄 完整報告已存入本地"
    send_telegram(f"📊 *{today_str} 數據報告*\n\n{summary}")

    print("[Report] 完成！")


if __name__ == "__main__":
    run()
```

---

## 任務 13：建立 `setup.sh`

路徑：`/Users/chris/Desktop/AI_IG_RUN/setup.sh`

內容：

```bash
#!/bin/bash
echo "=== IG Autopilot 環境設定 ==="

# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝套件
pip install --upgrade pip
pip install -r requirements.txt

# 建立必要目錄
mkdir -p data output/reports

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
```

---

## 任務 14：建立 `.gitignore`

路徑：`/Users/chris/Desktop/AI_IG_RUN/.gitignore`

內容：

```
.env
venv/
__pycache__/
*.pyc
output/
data/publish_log.json
data/performance_history.json
logs/
*.log
.DS_Store
```

---

## 任務 15：建立 `README.md`

路徑：`/Users/chris/Desktop/AI_IG_RUN/README.md`

內容：

```markdown
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
```

---

## 執行完成後的驗證清單

請確認以下檔案都已建立：

- [ ] `requirements.txt`
- [ ] `.env.example`
- [ ] `config/content_calendar.json`
- [ ] `config/prompts.py`
- [ ] `services/claude_service.py`
- [ ] `services/image_service.py`
- [ ] `services/cloud_service.py`
- [ ] `services/ig_service.py`
- [ ] `services/notify_service.py`
- [ ] `main.py`
- [ ] `report.py`
- [ ] `setup.sh`
- [ ] `.gitignore`
- [ ] `README.md`
- [ ] 目錄：`data/`、`output/`、`services/`、`config/`

所有任務完成後，請輸出：「✅ IG Autopilot 專案建置完成，共建立 N 個檔案」
