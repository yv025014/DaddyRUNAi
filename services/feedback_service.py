"""
feedback_service.py
① get_feedback_context()  — 從 performance_history.json 整理高表現故事特徵，注入 prompt
② get_used_concepts()     — 從 publish_log.json 整理已用技術概念與生活事件，供去重使用
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
HISTORY_PATH = BASE_DIR / "data" / "performance_history.json"
LOG_PATH = BASE_DIR / "data" / "publish_log.json"


def _day_to_content_type() -> dict[int, str]:
    """從 publish_log 建立 day → content_type 映射表。"""
    if not LOG_PATH.exists():
        return {}
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        log = json.load(f)
    return {
        entry["day"]: entry.get("content_type", "carousel")
        for entry in log
        if "day" in entry
    }


def get_feedback_context(top_n: int = 3, content_type: str | None = None) -> str:
    """
    讀取 performance_history.json，整理高存數/高留言故事的標題，
    回傳可直接注入 prompt 的文字摘要。沒有資料時回傳空字串。

    評分公式：saved×3 + comments×2 + likes×1（存數最能反映長尾傳播）

    content_type 指定時，優先回傳同格式貼文的反饋；
    同格式貼文不足 top_n 則 fallback 至全格式（並加上說明）。
    """
    if not HISTORY_PATH.exists():
        return ""

    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        history = json.load(f)

    # 攤平所有 snapshot 成單篇記錄
    all_posts = []
    for snapshot in history:
        for post in snapshot.get("snapshot", []):
            ins = post.get("insights", {})
            if not ins:
                continue
            score = (
                ins.get("saved", 0) * 3
                + ins.get("comments", 0) * 2
                + ins.get("likes", 0)
            )
            all_posts.append({**post, "_score": score})

    if not all_posts:
        return ""

    # 若指定 content_type，嘗試過濾同格式貼文
    type_label = ""
    scored = all_posts
    if content_type:
        day_type = _day_to_content_type()
        filtered = [p for p in all_posts if day_type.get(p.get("day")) == content_type]
        if len(filtered) >= top_n:
            scored = filtered
            type_label = f"（僅 {content_type} 格式）"
        # 不足 top_n 時靜默 fallback 至全格式

    scored.sort(key=lambda x: x["_score"], reverse=True)
    top = scored[:top_n]
    bottom_threshold = scored[0]["_score"] * 0.4
    bottom = [p for p in scored[-top_n:] if p["_score"] < bottom_threshold]

    lines = [f"【過去數據參考{type_label}（只參考方向，不要抄主題）】"]
    lines.append("高存數 / 高留言的故事（這類結構有效）：")
    for p in top:
        ins = p.get("insights", {})
        lines.append(
            f"  - 「{p.get('story_title', '')}」"
            f"存數 {ins.get('saved', '?')}｜留言 {ins.get('comments', '?')}｜觸及 {ins.get('reach', '?')}"
        )

    if bottom:
        lines.append("表現較低的故事（避免類似結構）：")
        for p in bottom:
            lines.append(f"  - 「{p.get('story_title', '')}」")

    return "\n".join(lines)


def get_used_concepts() -> dict:
    """
    讀取 publish_log.json，回傳已使用的技術概念與生活事件清單（去重、保持順序）。
    格式：{"tech_concepts": [...], "life_events": [...]}
    """
    if not LOG_PATH.exists():
        return {"tech_concepts": [], "life_events": []}

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        log = json.load(f)

    tech_concepts: list[str] = []
    life_events: list[str] = []
    for entry in log:
        if entry.get("status") == "published":
            if tc := entry.get("tech_concept", "").strip():
                if tc not in tech_concepts:
                    tech_concepts.append(tc)
            if le := entry.get("life_event", "").strip():
                if le not in life_events:
                    life_events.append(le)

    return {"tech_concepts": tech_concepts, "life_events": life_events}
