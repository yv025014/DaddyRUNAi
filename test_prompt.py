"""
測試腳本 — 只跑 Phase 1（LLM 生成腳本），不合成圖、不上傳、不發文。
用法：python test_prompt.py
"""

import json
from dotenv import load_dotenv
load_dotenv()

from services.llm_service import generate_content

# 測試參數 — 模擬一個技術白話主題
TEST_DAY = 0
TEST_PILLAR = "tech"
TEST_PILLAR_NAME = "技術白話"
TEST_THEME = "資料庫是什麼"
TEST_CONTENT_TYPE = "carousel"
TEST_SCRIPT_HINT = ""  # 留空讓 LLM 自由發揮


def print_result(content: dict):
    print("\n" + "=" * 60)
    print(f"故事標題：{content.get('story_title')}")
    print("=" * 60)

    for scene in content.get("scenes", []):
        speaker_map = {"chris": "Chris 把拔", "anna": "Anna", "mom": "媽咪"}
        speaker = speaker_map.get(scene.get("speaker", ""), scene.get("speaker", ""))
        print(f"\n【第 {scene['page']} 頁】{speaker}（{scene.get('mood', '')}）")
        print(f"  {scene['story_text']}")

    print("\n" + "-" * 60)
    print(f"金句：{content.get('quote', '')}")
    print("-" * 60)
    print(f"\n貼文文案：\n{content.get('caption', '')}")
    print(f"\n標籤：{' '.join(['#' + t for t in content.get('hashtags', [])])}")
    print("=" * 60)


if __name__ == "__main__":
    print(f"[Test] 主題：{TEST_THEME}")
    print("[Test] 呼叫 Gemini 生成腳本（不發文）...\n")

    content = generate_content(
        TEST_DAY,
        TEST_PILLAR,
        TEST_PILLAR_NAME,
        TEST_THEME,
        TEST_CONTENT_TYPE,
        TEST_SCRIPT_HINT,
    )

    print_result(content)

    # 同時存成 JSON 方便對照
    with open("test_output.json", "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    print("\n[Test] 完整 JSON 已儲存至 test_output.json")
