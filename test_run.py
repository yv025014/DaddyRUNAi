"""
test_run.py — 全流程測試（不發文）

用法：
    python test_run.py --day 2
    python test_run.py --day 9 --attempts 1
    python test_run.py --day 4 --skip-review

流程：
    Phase 1   : LLM 生成故事 + 格式說書人審查（最多重試 2 次）
    Phase 1.5 : 審稿員品質審查（carousel 格式才跑）
    Phase 2   : 合成輪播圖（角色立繪 + 背景 + 文字）
    ✗ Phase 3 : 跳過上傳 Cloudinary
    ✗ Phase 4 : 跳過發布 Instagram

輸出目錄：test/test_day{XX}_{uuid8}/
    - today_brief.md    故事簡報
    - story.json        完整故事 JSON
    - slide_*.png       合成好的圖片
"""

import argparse
import json
import datetime
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from services.llm_service import generate_content, review_story
from services.feedback_service import get_feedback_context, get_used_concepts
from services.composite_service import render_carousel

BASE_DIR = Path(__file__).parent
CALENDAR_PATH = BASE_DIR / "config" / "content_calendar.json"
TEST_DIR = BASE_DIR / "test"


def load_calendar() -> dict:
    with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_day_item(calendar: dict, day: int) -> dict | None:
    for item in calendar["schedule"]:
        if item["day"] == day:
            return item
    return None


def save_brief(output_dir: Path, day: int, schedule_item: dict, content: dict, content_type: str):
    scenes_text = "\n\n".join([
        f"**P{s['page']}** [{s.get('speaker', '')} / {s.get('mood', '')}]\n{s['story_text']}"
        for s in content.get("scenes", [])
    ])
    lines = [
        f"# 測試簡報 — 第 {day} 天",
        f"",
        f"**日期**：{datetime.date.today()}",
        f"**格式**：{content_type}（{len(content.get('scenes', []))} 頁）",
        f"**故事標題**：{content.get('story_title', '')}",
        f"**支柱**：{schedule_item['pillar']} — {schedule_item.get('theme', '')}",
        f"**技術概念**：{content.get('tech_concept', '—')}",
        f"**生活事件**：{content.get('life_event', '—')}",
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
    (output_dir / "today_brief.md").write_text("\n".join(lines), encoding="utf-8")


def run(day: int, max_attempts: int = 2, skip_review: bool = False):
    print("=" * 55)
    print(f"[Test] Day {day} 全流程測試 — {datetime.datetime.now()}")
    print("=" * 55)

    # 建立輸出目錄
    uid = uuid.uuid4().hex[:8]
    output_dir = TEST_DIR / f"test_day{day:02d}_{uid}"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[Test] 輸出目錄：{output_dir}")

    # 讀取 calendar
    calendar = load_calendar()
    today_item = get_day_item(calendar, day)
    if today_item is None:
        print(f"[Test] ✗ 找不到 Day {day} 的行程，請確認 content_calendar.json")
        return

    pillar = today_item["pillar"]
    pillar_info = calendar["pillars"][pillar]
    theme = today_item["theme"]
    content_type = today_item["type"]
    script_hint = today_item.get("script_hint", "")

    print(f"[Test] Day {day} | {content_type} | 支柱：{pillar} | {theme}")

    # 載入 feedback + 去重資料
    print("[Test] 載入反饋與已用概念...")
    feedback_context = get_feedback_context(content_type=content_type)
    used_concepts = get_used_concepts()
    used_t = ", ".join(used_concepts["tech_concepts"]) or "無"
    used_e = ", ".join(used_concepts["life_events"]) or "無"
    print(f"[Test] 已用技術概念：{used_t}")
    print(f"[Test] 已用生活事件：{used_e}")

    # ── Phase 1 + 1.5 ──────────────────────────────────────
    content = None
    used_attempt = 1
    for attempt in range(max_attempts):
        print(f"\n[Phase 1] 生成故事...（第 {attempt + 1} 次）")
        try:
            content = generate_content(
                day, pillar, pillar_info["name"], theme, content_type, script_hint,
                feedback_context=feedback_context,
                used_concepts=used_concepts,
            )
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"[Test] 生成失敗，重試：{e}")
                continue
            print(f"[Test] ✗ 生成失敗（已試 {max_attempts} 次）：{e}")
            return

        narrative_pass = content.pop("_narrative_pass", True)
        save_brief(output_dir, day, today_item, content, content_type)

        if not narrative_pass:
            if attempt < max_attempts - 1:
                print("[Test] ⚠️  說書人發現敘事斷裂，重新生成...")
                continue
            print("[Test] ⚠️  說書人仍有問題，以當前版本繼續")

        if not skip_review:
            print("\n[Phase 1.5] 審稿員檢查...")
            content, critical_pass = review_story(content)
            save_brief(output_dir, day, today_item, content, content_type)
            if critical_pass:
                used_attempt = attempt + 1
                print(f"[Test] ✓ 審稿通過（第 {used_attempt} 次生成）")
                break
            if attempt < max_attempts - 1:
                print("[Test] ⚠️  審稿發現格式問題，重新生成...")
            else:
                used_attempt = max_attempts
                print("[Test] ⚠️  審稿仍有問題，以當前版本繼續")
        else:
            print("[Test] 審稿步驟已跳過（--skip-review）")
            used_attempt = attempt + 1
            break

    scenes = content.get("scenes", [])
    if not scenes:
        print("[Test] ✗ 故事場景為空，終止")
        return

    print(f"\n[Test] 故事標題：{content.get('story_title')}，共 {len(scenes)} 頁")

    # 儲存 story.json
    (output_dir / "story.json").write_text(
        json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ── Phase 2：合成圖片 ────────────────────────────────────
    print("\n[Phase 2] 合成輪播圖...")
    calendar_bg = today_item.get("cover_background", "")
    first_scene_bg = (content.get("scenes") or [{}])[0].get("background", "")
    content["cover_background"] = calendar_bg or first_scene_bg or "dining_room"
    print(f"[Test] 封面背景：{content['cover_background']}")

    image_paths = render_carousel(content, str(output_dir))
    print(f"[Phase 2] 合成完成，共 {len(image_paths)} 張圖片")

    # ── 結果摘要 ─────────────────────────────────────────────
    print("\n" + "=" * 55)
    print(f"[Test] ✅ 完成！Day {day} | {content_type} | 生成次數：{used_attempt}")
    print(f"[Test] 輸出目錄：{output_dir}")
    print(f"[Test] 檔案：")
    for f in sorted(output_dir.iterdir()):
        size = f.stat().st_size
        print(f"         {f.name:30s}  {size:>8,} bytes")
    print("=" * 55)

    # 印出各頁摘要
    print("\n[Test] 故事預覽：")
    for s in scenes:
        print(f"  P{s['page']} [{s.get('speaker',''):8s} / {s.get('mood',''):10s}]  {s['story_text'][:50]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IG Autopilot 全流程測試（不發文）")
    parser.add_argument("--day", type=int, required=True, help="要測試的天數（1–30）")
    parser.add_argument("--attempts", type=int, default=2, help="最大生成嘗試次數（預設 2）")
    parser.add_argument("--skip-review", action="store_true", help="跳過 Phase 1.5 審稿步驟")
    args = parser.parse_args()

    run(day=args.day, max_attempts=args.attempts, skip_review=args.skip_review)
