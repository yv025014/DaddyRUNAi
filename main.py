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

from services.llm_service import generate_content, review_story
from services.feedback_service import get_feedback_context, get_used_concepts
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
    published_days = {
        entry.get("day") for entry in log
        if entry.get("status") == "published" and entry.get("day")
    }
    for item in calendar["schedule"]:
        if item["day"] not in published_days:
            return item
    return None


def format_caption(content: dict) -> str:
    tags = " ".join([f"#{t.lstrip('#')}" for t in content.get("hashtags", [])])
    return f"{content['caption']}\n\n{tags}"


def save_brief(output_dir: Path, day: int, schedule_item: dict, content: dict, content_type: str = ""):
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
        f"**格式**：{content_type}（{len(content.get('scenes', []))} 頁）",
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

    # 載入閉環反饋與去重資料
    print("[Main] 載入過去表現數據與已用概念...")
    feedback_context = get_feedback_context(content_type=content_type)
    used_concepts    = get_used_concepts()
    if feedback_context:
        print("[Main] 反饋摘要已載入")
    used_t = ", ".join(used_concepts["tech_concepts"]) or "無"
    used_e = ", ".join(used_concepts["life_events"]) or "無"
    print(f"[Main] 已用技術概念：{used_t}")
    print(f"[Main] 已用生活事件：{used_e}")

    # Phase 1 + 1.5 — 生成（骨架→腳本）+ 審稿，最多重試 2 次
    content = None
    used_attempt = 1
    for attempt in range(2):
        print(f"\n[Phase 1] 呼叫 Gemini 生成繪本故事...（第 {attempt + 1} 次）")
        try:
            content = generate_content(
                day, pillar, pillar_info["name"], theme, content_type, script_hint,
                feedback_context=feedback_context,
                used_concepts=used_concepts,
            )
        except Exception as e:
            if attempt == 0:
                print(f"[Main] 第1次生成失敗，重試中：{e}")
                continue                        # 不通知，直接重試
            msg = f"⚠️ 第 {day} 天 — Gemini 生成失敗（已重試2次）：{e}"
            print(f"[Main] {msg}")
            send_telegram(msg)
            return

        # 取出說書人審查結果（_narrative_pass 是內部旗標，不存入 brief）
        narrative_pass = content.pop("_narrative_pass", True)

        save_brief(output_dir, day, today_item, content, content_type)

        # 說書人發現結構性斷裂 → 直接重生，不跑 review
        if not narrative_pass:
            if attempt == 0:
                print("[Main] ⚠️ 說書人發現敘事斷裂，重新生成...")
                continue
            else:
                print("[Main] ⚠️ 二次說書人仍有問題，以當前版本繼續")

        print("\n[Phase 1.5] 審稿員檢查格式與字數...")
        content, critical_pass = review_story(content)
        save_brief(output_dir, day, today_item, content, content_type)  # 覆寫，保留審稿後版本

        if critical_pass:
            used_attempt = attempt + 1
            print(f"[Main] ✓ 審稿通過（第 {used_attempt} 次生成）")
            break

        if attempt == 0:
            print("[Main] ⚠️ 審稿發現格式問題，重新生成...")
        else:
            used_attempt = 2
            print("[Main] ⚠️ 二次審稿仍有問題，以當前版本繼續")

    scenes = content.get("scenes", [])
    if not scenes:
        msg = f"⚠️ 第 {day} 天 — 故事場景生成失敗"
        send_telegram(msg)
        return

    print(f"[Main] 故事標題：{content.get('story_title')}，共 {len(scenes)} 個場景")

    # Phase 2 — 合成輪播圖（角色立繪 + 背景 + 文字）
    print("\n[Phase 2] 合成輪播圖（角色立繪 + 背景 + 文字）...")
    # 封面背景：優先用 calendar 的明確指定（特殊覆蓋），
    # 否則跟著第 1 頁場景背景走，讓封面與故事開場一致。
    calendar_bg   = today_item.get("cover_background", "")
    first_scene_bg = (content.get("scenes") or [{}])[0].get("background", "")
    content["cover_background"] = calendar_bg or first_scene_bg or "dining_room"
    print(f"[Main] 封面背景：{content['cover_background']}")
    image_paths = render_carousel(content, str(output_dir))

    if len(image_paths) < 2:
        msg = (
            f"⚠️ *第 {day} 天 — Phase 2 合成失敗*\n"
            f"只合成出 {len(image_paths)} 頁（需要至少 2 頁）\n"
            f"故事已存：output/{today_str}/today_brief.md"
        )
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
        msg = (
            f"⚠️ *第 {day} 天 — Phase 3 上傳失敗*\n"
            f"成功上傳 {len(image_urls)}/{len(image_paths)} 張\n"
            f"圖片已存：output/{today_str}/"
        )
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
        "content_type": content_type,
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
        "content_type": content_type,
        "tech_concept": content.get("tech_concept", ""),
        "life_event":   content.get("life_event", ""),
        "media_id": media_id,
        "image_count": len(image_urls),
        "status": "published" if media_id else "failed",
    })
    save_log(log)

    # 通知
    tech  = content.get("tech_concept", "")
    event = content.get("life_event", "")
    concept_line = f"🔧 {tech} × {event}\n" if (tech or event) else ""
    retry_note   = f"（第 {used_attempt} 次生成才通過）\n" if used_attempt > 1 else ""

    if media_id:
        msg = (
            f"✅ *第 {day} 天｜{content_type} 發布成功！*\n"
            f"📖 {content.get('story_title')}\n"
            f"{concept_line}"
            f"🖼 {len(image_urls)} 張輪播｜主題：{theme}\n"
            f"{retry_note}"
            f"Media ID：`{media_id}`"
        )
    else:
        msg = (
            f"❌ *第 {day} 天 — Phase 4 發布失敗*\n"
            f"📖 {content.get('story_title', '未知')}\n"
            f"{concept_line}"
            f"圖片已上傳 {len(image_urls)} 張，IG API 出錯\n"
            f"可至 output/{today_str}/post_package.json 手動發布"
        )

    send_telegram(msg)
    print(f"\n[Main] 完成！狀態：{'成功' if media_id else '失敗'}")


if __name__ == "__main__":
    run()
