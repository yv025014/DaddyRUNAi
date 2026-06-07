#!/usr/bin/env python3
"""週日策略執行腳本（urllib 直呼 Gemini REST，不依賴 google-genai 套件）"""

import json, datetime, urllib.request, re, time
from pathlib import Path

GOOGLE_API_KEY = "AIzaSyAUkCHhIxLDMl2Ox4wsd0sM4fzNn6nuXJc"
IG_USER_ID    = "26910364638579613"
IG_TOKEN      = "IGAAbhzps2uFVBZAGItNTkzTENBdWdMNjVFZA1FlcTRGb1NPOGlvZA3czTzg3cUFRVXh1cW1rSXMzenF2TTllRTF1bks1RlBpcXRlQzAxNlRWX0t1YTVNbUV5dmFNRHljX1duWjNDNnVFSzdVQUlQcXFjSkxRd0VEV0JjN0RZAMVZAPVQZDZD"

BASE_DIR      = Path("/home/user/DaddyRUNAi")
CALENDAR_PATH = BASE_DIR / "config" / "content_calendar.json"
REPORTS_DIR   = BASE_DIR / "output" / "reports"
TODAY         = datetime.date.today().isoformat()
START_DATE    = datetime.date(2026, 5, 1)
CURRENT_DAY   = (datetime.date.today() - START_DATE).days + 1  # 38


# ── Gemini REST ────────────────────────────────────────────────────────────────
def gemini(prompt: str, model: str = "gemini-2.0-flash-lite", retries: int = 5) -> str:
    # Try list: primary model, then fallbacks
    models_to_try = [model, "gemini-flash-lite-latest", "gemini-2.0-flash-lite-001",
                     "gemini-2.5-flash-lite", "gemini-flash-latest"]
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 16000, "temperature": 0.7},
    }).encode()
    for m in models_to_try:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{m}:generateContent?key={GOOGLE_API_KEY}")
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        for attempt in range(retries):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    result = json.loads(r.read())
                print(f"  [Gemini] 使用模型: {m}")
                return result["candidates"][0]["content"]["parts"][0]["text"]
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < retries - 1:
                    wait = 15 * (attempt + 1)
                    print(f"  [Gemini] {m} 429，等待 {wait}s…")
                    time.sleep(wait)
                elif e.code == 429:
                    print(f"  [Gemini] {m} 配額耗盡，換下一個模型")
                    break
                else:
                    raise
    raise RuntimeError("所有 Gemini 模型均達配額上限")


# ── IG Insights（網路封鎖時優雅降級）─────────────────────────────────────────
def fetch_ig() -> tuple[list, str]:
    try:
        url = (f"https://graph.instagram.com/v19.0/{IG_USER_ID}/media"
               f"?fields=id,timestamp,caption&limit=7&access_token={IG_TOKEN}")
        with urllib.request.urlopen(url, timeout=10) as r:
            posts = json.loads(r.read()).get("data", [])
        out = []
        for p in posts:
            ins_url = (f"https://graph.instagram.com/v19.0/{p['id']}/insights"
                       f"?metric=impressions,reach,likes,comments,saved,shares"
                       f"&access_token={IG_TOKEN}")
            with urllib.request.urlopen(ins_url, timeout=10) as r2:
                ins = {i["name"]: i.get("value", 0)
                       for i in json.loads(r2.read()).get("data", [])}
            out.append({"media_id": p["id"], "date": p.get("timestamp","")[:10],
                        "caption_preview": p.get("caption","")[:60], "insights": ins})
        return out, f"IG API 成功取得 {len(out)} 篇"
    except Exception as e:
        return [], f"IG API 不可用（{type(e).__name__}）：環境網路封鎖"


# ── Step 3：Gemini 策略分析 ───────────────────────────────────────────────────
def analyze(posts_data: list, calendar: dict, ig_status: str) -> str:
    schedule = calendar.get("schedule", [])
    max_day = max(e["day"] for e in schedule)
    adj_start = CURRENT_DAY          # 38（今天）
    adj_end   = adj_start + 4        # 42

    pillar_count = {}
    for e in schedule:
        p = e.get("pillar", "")
        pillar_count[p] = pillar_count.get(p, 0) + 1

    cal_summary = json.dumps(
        [{"day": e["day"], "pillar": e["pillar"], "theme": e["theme"]}
         for e in schedule],
        ensure_ascii=False, indent=2
    )
    ig_block = (json.dumps(posts_data, ensure_ascii=False, indent=2)
                if posts_data else f"（{ig_status}，以行事曆結構進行理論評估）")

    prompt = f"""你是「Chris｜工程師把拔」IG 帳號的資深策略顧問。今天是 {TODAY}（週日），實驗第 {CURRENT_DAY} 天。

帳號定位：全端工程師（.NET/React/MSSQL）＋五歲女兒 Anna 的把拔，台灣在地。
四大支柱：
- tech（技術白話）：Anna生活疑問 → Chris生活比喻 → Anna童言反殺 → 收藏金句
- workplace（IT職場奇聞）：迷因標題 → 荒謬需求 → 工程師視角崩潰 → Tag共鳴金句
- home_meme（家裡有工程師）：「家裡有工程師，＿＿不能亂＿＿」格式 → 媽咪補刀 → 軟共鳴
- office（大人腹黑學）：荒謬職場場景 → Anna小孩邏輯 → 媽咪一句話揭真相 → 黑色幽默破圈

IG 數據（近7篇）：{ig_block}

現有行事曆（Day 1–{max_day}，目前已執行到 Day {CURRENT_DAY-1}）：
{cal_summary}

支柱分佈統計：{json.dumps(pillar_count, ensure_ascii=False)}

請用繁體中文輸出以下四個區塊：

## 1. 本週數據摘要
說明 API 狀態。根據行事曆評估四大支柱互動潛力排名（哪個最能引發留言、收藏、分享），給出具體原因。

## 2. 演算法訊號解讀
IG 2025/2026 演算法重點（Reels 優先、留言權重最高、前3秒留存率、收藏代表延遲滿足）。
分析此帳號「Anna一句話反殺」＋「媽咪補刀」格式的演算法優勢。
列出3個具體優化動作（輪播第一頁加勾子文字、留言區置頂問題、限時動態互動等）。

## 3. 已調整的主題清單
行事曆現有內容截止到 Day {max_day}，今天是 Day {CURRENT_DAY}。
請提供 Day {adj_start} 到 Day {adj_end} 共 5 天的【全新主題】（延伸第二季內容）。
格式嚴格遵守如下（每行一條，不可加任何前綴符號或額外格式）：
Day {adj_start} | <支柱名稱> | 新主題文字 | 一句話原因（15字內）
Day {adj_start+1} | <支柱名稱> | 新主題文字 | 一句話原因（15字內）
Day {adj_start+2} | <支柱名稱> | 新主題文字 | 一句話原因（15字內）
Day {adj_start+3} | <支柱名稱> | 新主題文字 | 一句話原因（15字內）
Day {adj_start+4} | <支柱名稱> | 新主題文字 | 一句話原因（15字內）
支柱名稱只能用：tech / workplace / home_meme / office

## 4. 下週策略方向
- 最應強化的支柱（一個）＋理由
- 最應測試的新勾子或新格式
- 一個潛力爆款主題（給出完整腳本起點3句話）
- 台灣最佳發文時段（附理由）
- 社群互動策略（發文後前30分鐘應做什麼）"""

    return gemini(prompt)


# ── Step 4：延伸行事曆 ────────────────────────────────────────────────────────
def extend_calendar(analysis: str, calendar: dict) -> tuple[dict, list]:
    schedule = calendar.get("schedule", [])
    max_day = max(e["day"] for e in schedule)
    adj_start = CURRENT_DAY
    adj_end   = adj_start + 4

    section3 = ""
    if "## 3." in analysis:
        parts = analysis.split("## 3.")
        if len(parts) > 1:
            section3 = parts[1].split("## 4.")[0].strip()

    # Parse: Day XX | pillar | theme | reason
    valid_pillars = {"tech", "workplace", "home_meme", "office"}
    new_entries = []
    for line in section3.splitlines():
        line = line.strip().lstrip("*- ").strip()
        m = re.match(r'Day\s*(\d+)\s*\|\s*([^\|]+)\s*\|\s*([^\|]+)\s*\|\s*(.+)', line)
        if m:
            day = int(m.group(1))
            pillar = m.group(2).strip().lower()
            theme  = m.group(3).strip().strip("**")
            reason = m.group(4).strip()
            if adj_start <= day <= adj_end and pillar in valid_pillars:
                new_entries.append({"day": day, "pillar": pillar,
                                    "theme": theme, "reason": reason})

    existing_days = {e["day"] for e in schedule}
    added = []
    for ne in new_entries:
        if ne["day"] not in existing_days:
            type_map = {"tech": "tech", "workplace": "workplace",
                        "home_meme": "home_meme", "office": "carousel"}
            schedule.append({
                "day": ne["day"],
                "type": type_map.get(ne["pillar"], "carousel"),
                "pillar": ne["pillar"],
                "theme": ne["theme"],
                "cover_background": "office_desk",
                "script_hint": f"[AI建議] {ne['reason']}",
            })
            added.append(ne)
            existing_days.add(ne["day"])

    # Sort schedule by day
    calendar["schedule"] = sorted(schedule, key=lambda x: x["day"])
    return calendar, added


# ── Step 5：週報 ──────────────────────────────────────────────────────────────
def write_report(analysis: str, added: list, ig_status: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"weekly_strategy_{TODAY}.md"

    added_lines = "\n".join(
        f"- Day {a['day']} [{a['pillar']}]：**{a['theme']}**（{a.get('reason','')}）"
        for a in added
    ) or "- 本週無新增主題（行事曆已涵蓋）"

    content = f"""# 週策略報告｜Chris 工程師把拔

**報告日期**：{TODAY}（每週日自動產出）
**實驗天數**：Day {CURRENT_DAY}
**IG 數據狀態**：{ig_status}

---

{analysis}

---

## 附錄：本次新增行事曆主題

{added_lines}

---
*本報告由 DaddyRUNAi 自動化策略系統產出*
"""
    path.write_text(content, encoding="utf-8")
    return path


# ── 主流程 ────────────────────────────────────────────────────────────────────
def main():
    sep = "=" * 55
    print(f"{sep}\n[策略] 週日策略任務啟動 — {TODAY}  Day {CURRENT_DAY}\n{sep}")

    print("\n[Step 2] 取得 IG Insights…")
    posts_data, ig_status = fetch_ig()
    print(f"         {ig_status}")

    with open(CALENDAR_PATH, encoding="utf-8") as f:
        calendar = json.load(f)
    max_day = max(e["day"] for e in calendar["schedule"])
    print(f"\n[Step 3] 行事曆現有 Day 1–{max_day}，今天 Day {CURRENT_DAY}，延伸至 Day {CURRENT_DAY+4}")

    cache = REPORTS_DIR / f".analysis_cache_{TODAY}.txt"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        analysis = cache.read_text(encoding="utf-8")
        print(f"         使用快取（{len(analysis)} 字元）")
    else:
        print("         呼叫 Gemini 分析…")
        analysis = analyze(posts_data, calendar, ig_status)
        cache.write_text(analysis, encoding="utf-8")
        print(f"         完成，{len(analysis)} 字元")

    print("\n[Step 4] 延伸內容行事曆…")
    calendar, added = extend_calendar(analysis, calendar)
    with open(CALENDAR_PATH, "w", encoding="utf-8") as f:
        json.dump(calendar, f, ensure_ascii=False, indent=2)
    print(f"         新增 {len(added)} 個主題")
    for a in added:
        print(f"  Day {a['day']} [{a['pillar']}]: {a['theme'][:40]}")

    print("\n[Step 5] 產出週報…")
    rp = write_report(analysis, added, ig_status)
    print(f"         {rp}")

    print(f"\n{sep}\n[完成] 週日策略任務結束\n{sep}")


if __name__ == "__main__":
    main()
