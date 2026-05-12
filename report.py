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

    recent_posts = get_recent_posts(limit=7)
    if not recent_posts:
        print("[Report] 無法取得貼文資料")
        send_telegram("⚠️ 報告腳本：無法取得 IG 貼文資料")
        return

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

    history = load_history()
    today_str = datetime.date.today().isoformat()
    history.append({
        "date": today_str,
        "posts": posts_data,
    })
    save_history(history)

    print("[Report] 呼叫 Claude 生成分析報告...")
    report_text = generate_report(posts_data, insights_data)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"daily_report_{today_str}.md"
    report_path.write_text(report_text, encoding="utf-8")
    print(f"[Report] 報告已儲存：{report_path}")

    summary = report_text[:500] + "\n\n📄 完整報告已存入本地"
    send_telegram(f"📊 *{today_str} 數據報告*\n\n{summary}")

    print("[Report] 完成！")


if __name__ == "__main__":
    run()
