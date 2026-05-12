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

    today_str = datetime.date.today().isoformat()
    output_dir = OUTPUT_BASE / today_str
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n[Phase 1] 呼叫 Claude 生成文案...")
    content = generate_content(day, pillar, pillar_info["name"], theme, content_type)
    save_brief(output_dir, day, today_item, content)

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

    print("\n[Phase 3] 上傳圖片至 Cloudinary...")
    public_id = f"ig_autopilot/day_{day:02d}_{today_str}"
    image_url = upload_image(image_path, public_id)

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

    print("\n[Phase 4] 發布至 Instagram...")
    caption = format_caption(content)
    media_id = post_to_instagram(image_url, caption)

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
