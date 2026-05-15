"""
IG Autopilot — 每日主腳本（繪本輪播版）
執行方式：python main.py
Cron：0 8 * * * cd /Users/chris/Desktop/AI_IG_RUN && ./venv/bin/python main.py >> logs/main.log 2>&1
"""

import os
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from services.llm_service import generate_content
from services.composite_service import render_carousel
from services.cloud_service import upload_image
from services.ig_service import post_carousel_to_instagram
from services.notify_service import send_telegram

BASE_DIR = Path(__file__).parent
PROJECT_DIR = Path("/Users/chris/Desktop/AI_IG_RUN")
CALENDAR_PATH = BASE_DIR / "config" / "content_calendar.json"
LOG_PATH = PROJECT_DIR / "data" / "publish_log.json"
OUTPUT_BASE = PROJECT_DIR / "output"


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
    log = load_log()
    published_days = {entry["day"] for entry in log if entry.get("status") == "published"}
    for item in calendar["schedule"]:
        if item["day"] not in published_days:
            return item
    return None


def format_caption(content: dict) -> str:
    tags = " ".join([f"#{t.lstrip('#')}" for t in content.get("hashtags", [])])
    return f"{content['caption']}\n\n{tags}"


def save_brief(output_dir: Path, day: int, schedule_item: dict, content: dict):
    brief_path = output_dir / "today_brief.md"
    scenes_text = "\n\n".join([
        f"**第{s['page']}頁** [{s.get('speaker','')} / {s.get('mood','')}]\n{s['story_text']}"
        for s in content.get("scenes", [])
    ])
    lines = [
        f"# 今日繪本簡報 — 第 {day} 天",
        f"",
        f"**日期**：{datetime.date.today()}",
        f"**故事標題**：{content.get('story_title', '')}",
        f"**支柱**：{schedule_item['pillar']} — {schedule_item.get('theme', '')}",
        f"**格式**：輪播5張繪本",
        f"",
        f"## 故事場景",
        f"",
        scenes_text,
        f"",
        f"## 貼文文案",
        f"",
        content.get("caption", ""),
        f"",
        f"## 標籤",
        f"",
        " ".join([f"#{t}" for t in content.get("hashtags", [])]),
    ]
    brief_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[Main] 簡報已儲存：{brief_path}")


def run():
    print("=" * 50)
    print(f"[Main] IG Autopilot 繪本版啟動 — {datetime.datetime.now()}")
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
    script_hint = today_item.get("script_hint", "")

    print(f"[Main] 今日任務：第 {day} 天 | 支柱 {pillar} | {theme}")

    today_str = datetime.date.today().isoformat()
    output_dir = OUTPUT_BASE / today_str
    output_dir.mkdir(parents=True, exist_ok=True)

    # Phase 1 — 生成繪本故事腳本
    print("\n[Phase 1] 呼叫 Gemini 生成繪本故事...")
    content = generate_content(day, pillar, pillar_info["name"], theme, content_type, script_hint)
    save_brief(output_dir, day, today_item, content)

    scenes = content.get("scenes", [])
    if not scenes:
        msg = f"⚠️ 第 {day} 天 — 故事場景生成失敗"
        send_telegram(msg)
        return

    print(f"[Main] 故事標題：{content.get('story_title')}，共 {len(scenes)} 個場景")

    # Phase 2 — 合成輪播圖（角色立繪 + 背景 + 文字）
    print("\n[Phase 2] 合成輪播圖（角色立繪 + 背景 + 文字）...")
    content["cover_background"] = today_item.get("cover_background", "dining_room")
    image_paths = render_carousel(content, str(output_dir))

    if len(image_paths) < 2:
        msg = f"⚠️ 第 {day} 天 — 輪播合成失敗（{len(image_paths)} 頁），請手動處理"
        print(f"[Main] {msg}")
        send_telegram(msg)
        return

    # Phase 3 — 上傳所有圖片至 Cloudinary
    print(f"\n[Phase 3] 上傳 {len(image_paths)} 張圖片至 Cloudinary...")
    image_urls = []
    for i, path in enumerate(image_paths):
        public_id = f"ig_autopilot/day_{day:02d}_{today_str}_p{i+1}"
        url = upload_image(path, public_id)
        if url:
            image_urls.append(url)

    if len(image_urls) < 2:
        msg = f"⚠️ 第 {day} 天 — 圖片上傳失敗"
        send_telegram(msg)
        return

    # 儲存發文包
    caption = format_caption(content)
    package = {
        "day": day,
        "date": today_str,
        "pillar": pillar,
        "theme": theme,
        "story_title": content.get("story_title"),
        "content_type": "carousel",
        "scenes": scenes,
        "image_urls": image_urls,
        "caption": caption,
    }
    (output_dir / "post_package.json").write_text(
        json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Phase 4 — 發布輪播至 IG
    print(f"\n[Phase 4] 發布 {len(image_urls)} 張輪播至 Instagram...")
    media_id = post_carousel_to_instagram(image_urls, caption)

    # 記錄 log
    log = load_log()
    log.append({
        "day": day,
        "date": today_str,
        "theme": theme,
        "story_title": content.get("story_title"),
        "media_id": media_id,
        "image_count": len(image_urls),
        "status": "published" if media_id else "failed",
    })
    save_log(log)

    # 通知
    if media_id:
        msg = (
            f"✅ *第 {day} 天繪本發布成功！*\n"
            f"📖 {content.get('story_title')}\n"
            f"🖼 {len(image_urls)} 張輪播\n"
            f"主題：{theme}\n"
            f"Media ID：`{media_id}`"
        )
    else:
        msg = f"❌ 第 {day} 天發布失敗，請檢查 log"

    send_telegram(msg)
    print(f"\n[Main] 完成！狀態：{'成功' if media_id else '失敗'}")


if __name__ == "__main__":
    run()
