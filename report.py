"""
IG Autopilot — 每日數據報告腳本
執行方式：python report.py
Cron：0 9 * * * cd /Users/chris/Desktop/AI_IG_RUN && ./venv/bin/python report.py >> logs/report.log 2>&1
"""

import json
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from services.ig_service import get_recent_posts, get_post_insights
from services.llm_service import generate_report
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


def build_posts_table(published_entries: list, insights_map: dict) -> str:
    """產生 Markdown 表格：發文紀錄 + insights"""
    header = "| 天 | 日期 | 主題 | 觸及 | 按讚 | 留言 | 儲存 | 分享 |"
    sep    = "|---|------|------|------|------|------|------|------|"
    rows = [header, sep]
    for e in published_entries:
        mid = e.get("media_id", "")
        ins = insights_map.get(mid, {})
        reach    = ins.get("reach",    "—")
        likes    = ins.get("likes",    "—")
        comments = ins.get("comments", "—")
        saved    = ins.get("saved",    "—")
        shares   = ins.get("shares",   "—")
        rows.append(
            f"| {e.get('day','?')} | {e.get('date','')} | {e.get('theme','')[:20]} "
            f"| {reach} | {likes} | {comments} | {saved} | {shares} |"
        )
    return "\n".join(rows)


def run():
    print("=" * 50)
    print(f"[Report] 數據報告腳本啟動 — {datetime.datetime.now()}")
    print("=" * 50)

    today_str = datetime.date.today().isoformat()
    log = load_log()
    published = [e for e in log if e.get("status") == "published" and e.get("media_id")]

    # 從 IG API 拉最近貼文 + insights
    recent_posts = get_recent_posts(limit=10)
    api_map = {p["id"]: p for p in recent_posts}

    insights_map: dict = {}
    for entry in published:
        mid = entry["media_id"]
        print(f"[Report] 抓取 insights：{mid} ({entry.get('theme','')[:20]})")
        insights_map[mid] = get_post_insights(mid)

    # 儲存歷史
    history = load_history()
    history.append({
        "date": today_str,
        "snapshot": [
            {**e, "insights": insights_map.get(e["media_id"], {})}
            for e in published
        ],
    })
    save_history(history)

    # 組裝結構化數據
    posts_table = build_posts_table(published, insights_map)

    # 有無有效 insights
    has_data = any(
        bool(v) for v in insights_map.values()
    )
    data_note = "" if has_data else (
        "\n> ⚠️ **注意**：Insights 數據目前為空，可能因為貼文發布不足 24 小時。"
        "明日報告將顯示真實數字。\n"
    )

    # 前綴結構化區塊（不交給 LLM）
    structured_block = f"""# 【工程師把拔】每日報告 — {today_str}

## 發文總覽

| 項目 | 數值 |
|------|------|
| 累計發文 | {len(published)} 篇 |
| 今日新增 | {sum(1 for e in published if e.get('date') == today_str)} 篇 |
| 計劃進度 | 第 {max((e.get('day',0) for e in published), default=0)} 天 / 30 天 |

## 各篇成效數據
{data_note}
{posts_table}

---
"""

    # LLM 分析（只傳最近 7 篇，控制 input token）
    print("[Report] 呼叫 Gemini 生成分析...")
    posts_for_llm = [
        {
            "day": e.get("day"),
            "date": e.get("date"),
            "theme": e.get("theme"),
            "story_title": e.get("story_title"),
            "insights": insights_map.get(e["media_id"], {}),
        }
        for e in published[-7:]
    ]
    recent_insights = {
        e["media_id"]: insights_map[e["media_id"]]
        for e in published[-7:]
        if e["media_id"] in insights_map
    }
    analysis = generate_report(posts_for_llm, recent_insights)

    report_text = structured_block + analysis

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"daily_report_{today_str}.md"
    report_path.write_text(report_text, encoding="utf-8")
    print(f"[Report] 報告已儲存：{report_path}")

    # Discord 通知：結構化摘要
    stats_lines = []
    for e in published[-3:]:  # 最近 3 篇
        mid = e["media_id"]
        ins = insights_map.get(mid, {})
        reach = ins.get("reach", ins.get("impressions", "待更新"))
        saved = ins.get("saved", "待更新")
        stats_lines.append(
            f"• Day{e.get('day','?')} {e.get('theme','')[:18]}｜觸及 {reach}｜儲存 {saved}"
        )

    notify_msg = (
        f"📊 **{today_str} 每日報告**\n\n"
        f"累計發文：{len(published)} 篇（進度 {max((e.get('day',0) for e in published), default=0)}/30）\n\n"
        + "\n".join(stats_lines)
        + "\n\n📄 完整報告已存入本地"
    )
    send_telegram(notify_msg)

    print("[Report] 完成！")


if __name__ == "__main__":
    run()
