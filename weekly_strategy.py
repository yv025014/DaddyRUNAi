"""
週日策略腳本：分析 IG 數據 → Gemini 策略建議 → 更新行事曆 → 產出週報
執行：python weekly_strategy.py
"""
import json
import datetime
import requests
from pathlib import Path
from google import genai
from google.genai import types

# ── 憑證（從環境變數讀取，參考 .env.example）────────────────────────────────
import os
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
IG_USER_ID = os.getenv("IG_USER_ID", "")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "")
BASE_URL = "https://graph.instagram.com/v19.0"
BASE_DIR = Path(__file__).parent
CALENDAR_PATH = BASE_DIR / "config" / "content_calendar.json"
REPORTS_DIR = BASE_DIR / "output" / "reports"
TODAY = datetime.date.today().isoformat()


# ── Step 2：IG Insights ────────────────────────────────────────────────────────
def fetch_ig_insights() -> tuple[list, str]:
    try:
        resp = requests.get(
            f"{BASE_URL}/{IG_USER_ID}/media",
            params={"fields": "id,timestamp,caption", "limit": 7,
                    "access_token": IG_ACCESS_TOKEN},
            timeout=10,
        )
        posts = resp.json().get("data", [])
        if not posts:
            return [], "IG API 回傳空資料"

        posts_data = []
        for post in posts:
            media_id = post["id"]
            ins_resp = requests.get(
                f"{BASE_URL}/{media_id}/insights",
                params={
                    "metric": "impressions,reach,likes,comments,saved,shares",
                    "access_token": IG_ACCESS_TOKEN,
                },
                timeout=10,
            )
            ins = {}
            for item in ins_resp.json().get("data", []):
                ins[item["name"]] = item.get("value", 0)
            posts_data.append({
                "media_id": media_id,
                "date": post.get("timestamp", "")[:10],
                "caption_preview": post.get("caption", "")[:60],
                "insights": ins,
            })
        return posts_data, "IG API 取得成功"
    except Exception as e:
        return [], f"IG API 不可用（環境網路封鎖）：{type(e).__name__}"


# ── Step 3：Gemini 分析 ────────────────────────────────────────────────────────
def analyze_with_gemini(posts_data: list, calendar: dict, ig_status: str) -> str:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    schedule = calendar.get("schedule", [])

    pillar_count = {}
    for entry in schedule:
        p = entry.get("pillar", "")
        pillar_count[p] = pillar_count.get(p, 0) + 1

    calendar_summary = json.dumps(
        [{"day": e["day"], "pillar": e["pillar"], "theme": e["theme"]}
         for e in schedule],
        ensure_ascii=False, indent=2
    )

    if posts_data:
        ig_block = json.dumps(posts_data, ensure_ascii=False, indent=2)
    else:
        ig_block = f"（{ig_status}，本次以內容行事曆結構進行理論評估）"

    prompt = f"""你是「Chris｜工程師把拔」IG 帳號的資深策略顧問。今天是 {TODAY}（週日）。

帳號定位：全端工程師（.NET/React/MSSQL）＋五歲女兒 Anna 的把拔，台灣在地。
三大支柱：
- tech（技術白話）：把拔認真解釋→Anna一句話秒懂→媽咪認證
- workplace（IT職場奇聞）：User提奇怪需求→Chris困惑→Anna一句話講出真相
- office（大人腹黑學）：荒謬職場場景→媽咪一句話補刀

IG 貼文數據：{ig_block}

30 天行事曆：
{calendar_summary}

支柱分佈：{json.dumps(pillar_count, ensure_ascii=False)}

請用繁體中文輸出以下四個區塊：

## 1. 本週數據摘要
說明 API 狀態。根據行事曆評估三大支柱互動潛力排名（workplace/office/tech 哪個最能引發留言、收藏、分享），給出具體原因。

## 2. 演算法訊號解讀
IG 2025 演算法重點（Reels 優先、留言權重最高、前3秒留存率、收藏代表延遲滿足）。分析此帳號「Anna一句話」格式的演算法優勢。列出3個具體優化動作（例：在輪播第一頁加勾子文字、在留言區置頂問題引導留言等）。

## 3. 已調整的主題清單
列出 Day 17-21 共 5 天的主題調整建議（這些天尚未發布）。
格式：Day XX | 支柱 | 舊主題 → 建議新主題 | 一句話調整原因

## 4. 下週策略方向
- 最應強化的支柱（一個）
- 最應測試的新勾子或新格式
- 一個潛力爆款主題（給出完整腳本起點3句話）
- 台灣最佳發文時段（附理由）
- 社群互動策略（發文後前30分鐘應做什麼）"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=16000,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return response.text


# ── Step 4：更新行事曆 ─────────────────────────────────────────────────────────
def update_calendar(gemini_analysis: str, calendar: dict) -> tuple[dict, list]:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    schedule = calendar.get("schedule", [])

    # Day 17-21 為待調整天數
    target_days = [e for e in schedule if 17 <= e["day"] <= 21]
    future_summary = json.dumps(
        [{"day": e["day"], "pillar": e["pillar"], "theme": e["theme"]}
         for e in target_days],
        ensure_ascii=False
    )

    # 從分析中提取第 3 區塊的調整建議
    section3 = ""
    if "## 3." in gemini_analysis:
        parts = gemini_analysis.split("## 3.")
        if len(parts) > 1:
            section3 = parts[1].split("## 4.")[0].strip()

    prompt = f"""根據以下策略分析，產出 JSON 格式的行事曆調整清單。

策略分析中的主題調整建議：
{section3[:800]}

當前 Day 17-21 主題：
{future_summary}

請輸出純 JSON array（不要有任何說明文字、不要 markdown）：
[{{"day": 17, "new_theme": "新主題文字", "reason": "一句話原因"}}, ...]

要求：
1. 只包含需要調整的天數（day 17 到 21）
2. new_theme 用繁體中文，保持工程師把拔人設
3. reason 不超過20字"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=2000,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )

    raw = response.text.strip()
    # 清理可能的 markdown
    for marker in ["```json", "```"]:
        raw = raw.replace(marker, "")
    raw = raw.strip()

    try:
        adjustments = json.loads(raw)
        if not isinstance(adjustments, list):
            adjustments = []
    except json.JSONDecodeError:
        # 嘗試找出 JSON array 部分
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            try:
                adjustments = json.loads(raw[start:end])
            except Exception:
                adjustments = []
        else:
            adjustments = []

    adjustment_map = {a["day"]: a for a in adjustments if isinstance(a, dict)}
    adjusted_list = []
    for entry in calendar["schedule"]:
        if entry["day"] in adjustment_map:
            old_theme = entry["theme"]
            adj = adjustment_map[entry["day"]]
            entry["theme"] = adj["new_theme"]
            adjusted_list.append({
                "day": entry["day"],
                "old_theme": old_theme,
                "new_theme": adj["new_theme"],
                "reason": adj.get("reason", ""),
            })

    return calendar, adjusted_list


# ── Step 5：產出週報 ───────────────────────────────────────────────────────────
def write_report(gemini_analysis: str, adjusted_list: list, ig_status: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"weekly_strategy_{TODAY}.md"

    adj_lines = "\n".join(
        f"- Day {a['day']}：{a['old_theme']} → **{a['new_theme']}**（{a['reason']}）"
        for a in adjusted_list
    ) or "- 本週無需調整主題"

    content = f"""# 週策略報告｜Chris 工程師把拔

**報告日期**：{TODAY}（每週日自動產出）
**IG 數據狀態**：{ig_status}

---

{gemini_analysis}

---

## 附錄：本次行事曆調整清單

{adj_lines}

---
*本報告由 DaddyRUNAi 自動化策略系統產出*
"""
    report_path.write_text(content, encoding="utf-8")
    return report_path


# ── 主流程 ────────────────────────────────────────────────────────────────────
def main():
    print(f"{'='*55}")
    print(f"[策略] 週日策略任務啟動 — {TODAY}")
    print(f"{'='*55}")

    print("\n[Step 2] 取得 IG Insights...")
    posts_data, ig_status = fetch_ig_insights()
    print(f"[Step 2] {ig_status}，取得 {len(posts_data)} 篇貼文")

    with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
        calendar = json.load(f)

    print("\n[Step 3] Gemini 策略分析...")
    gemini_analysis = analyze_with_gemini(posts_data, calendar, ig_status)
    print(f"[Step 3] 完成，分析長度 {len(gemini_analysis)} 字元")

    print("\n[Step 4] 更新內容行事曆...")
    calendar, adjusted_list = update_calendar(gemini_analysis, calendar)
    with open(CALENDAR_PATH, "w", encoding="utf-8") as f:
        json.dump(calendar, f, ensure_ascii=False, indent=2)
    print(f"[Step 4] 完成，共調整 {len(adjusted_list)} 個主題")
    for a in adjusted_list:
        print(f"  Day {a['day']}: {a['old_theme'][:20]}... → {a['new_theme'][:20]}...")

    print("\n[Step 5] 產出週報...")
    report_path = write_report(gemini_analysis, adjusted_list, ig_status)
    print(f"[Step 5] 週報已儲存：{report_path}")

    print(f"\n{'='*55}")
    print("[完成] 週日策略任務結束")
    print(f"{'='*55}")
    return report_path, adjusted_list


if __name__ == "__main__":
    main()
