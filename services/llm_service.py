import os
import json
from google import genai
from google.genai import types
from config.prompts import (
    SYSTEM_PROMPT, REVIEW_SYSTEM_PROMPT, EDITOR_SYSTEM_PROMPT, NARRATOR_SYSTEM_PROMPT,
    SYMPTOM_MEME_SYSTEM_PROMPT, FEYNMAN_SYSTEM_PROMPT, HOME_MEME_SYSTEM_PROMPT,
    SYMPTOM_MEME_NARRATOR_SYSTEM_PROMPT, HOME_MEME_NARRATOR_SYSTEM_PROMPT,
    TECH_SYSTEM_PROMPT, TECH_NARRATOR_SYSTEM_PROMPT,
    WORKPLACE_SYSTEM_PROMPT, WORKPLACE_NARRATOR_SYSTEM_PROMPT,
    OFFICE_SYSTEM_PROMPT, OFFICE_NARRATOR_SYSTEM_PROMPT,
    get_outline_prompt, get_story_from_outline_prompt,
    get_story_prompt, get_review_prompt, get_report_prompt,
    get_editor_prompt, get_narrator_prompt,
    get_symptom_meme_prompt, get_feynman_prompt, get_home_meme_prompt,
    get_symptom_meme_narrator_prompt, get_home_meme_narrator_prompt,
    get_tech_prompt, get_tech_narrator_prompt,
    get_workplace_prompt, get_workplace_narrator_prompt,
    get_office_prompt, get_office_narrator_prompt,
)


def _gemini_client():
    return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def _clean_json(raw: str) -> str:
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        return raw.strip()
    return raw[start:end + 1]


def _call_gemini_json(prompt: str, system: str, max_tokens: int = 4000) -> dict:
    """
    呼叫 Gemini，自動跨模型 retry，回傳解析後的 dict。
    失敗則 raise ValueError（交由上層決定 fallback 策略）。
    """
    client = _gemini_client()
    config = types.GenerateContentConfig(
        system_instruction=system,
        max_output_tokens=max_tokens,
        response_mime_type="application/json",
    )
    for model in ["gemini-2.5-flash", "gemini-flash-latest"]:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model, contents=prompt, config=config
                )
                result = json.loads(_clean_json(response.text))
                print(f"[LLM] 模型：{model}")
                return result
            except json.JSONDecodeError as e:
                print(f"[LLM] {model} JSON 解析失敗（第{attempt+1}次）：{e}")
            except Exception as e:
                print(f"[LLM] {model} 失敗：{e}")
                break
    raise ValueError("Gemini 無法生成有效內容，請稍後重試")


# ─────────────────────────────────────────────
# Phase 1a：骨架生成
# ─────────────────────────────────────────────

def _generate_outline(day: int, pillar: str, pillar_name: str, theme: str,
                      content_type: str, script_hint: str,
                      feedback_context: str, used_concepts: dict) -> dict:
    """生成故事骨架（tech_concept, life_event, trap, hook, mom_line, quote）"""
    prompt = get_outline_prompt(
        day, pillar, pillar_name, theme, content_type,
        script_hint, feedback_context, used_concepts,
    )
    outline = _call_gemini_json(prompt, SYSTEM_PROMPT)
    print(
        f"[LLM] 骨架確定：技術概念＝{outline.get('tech_concept')}｜"
        f"生活事件＝{outline.get('life_event')}"
    )
    return outline


# ─────────────────────────────────────────────
# Phase 1b：展開腳本
# ─────────────────────────────────────────────

def _generate_story_from_outline(outline: dict, day: int, pillar: str,
                                  pillar_name: str, theme: str) -> dict:
    """根據鎖定骨架展開完整 7 頁腳本。"""
    prompt = get_story_from_outline_prompt(outline, day, pillar, pillar_name, theme)
    story = _call_gemini_json(prompt, SYSTEM_PROMPT)
    return story


# ─────────────────────────────────────────────
# 對外主函式
# ─────────────────────────────────────────────

def _generate_symptom_meme(pillar_name: str, theme: str, script_hint: str,
                            feedback_context: str, used_concepts: dict) -> dict:
    """症狀型（迷因）單步生成。"""
    prompt = get_symptom_meme_prompt(pillar_name, theme, script_hint, feedback_context, used_concepts)
    story = _call_gemini_json(prompt, SYMPTOM_MEME_SYSTEM_PROMPT)
    print(f"[LLM] 症狀型生成完成：{story.get('tech_concept')} × {story.get('life_event')}")
    return story


def _generate_feynman(pillar_name: str, theme: str, script_hint: str,
                       feedback_context: str, used_concepts: dict) -> dict:
    """費曼教學型單步生成。"""
    prompt = get_feynman_prompt(pillar_name, theme, script_hint, feedback_context, used_concepts)
    story = _call_gemini_json(prompt, FEYNMAN_SYSTEM_PROMPT)
    print(f"[LLM] 費曼型生成完成：{story.get('tech_concept')} × {story.get('life_event')}")
    return story


def _generate_tech(pillar_name: str, theme: str, script_hint: str,
                   feedback_context: str, used_concepts: dict) -> dict:
    """技術白話型單步生成。"""
    prompt = get_tech_prompt(pillar_name, theme, script_hint, feedback_context, used_concepts)
    story = _call_gemini_json(prompt, TECH_SYSTEM_PROMPT)
    print(f"[LLM] 技術白話型生成完成：{story.get('tech_concept')} × {story.get('life_event')}")
    return story


def _generate_workplace(pillar_name: str, theme: str, script_hint: str,
                        feedback_context: str, used_concepts: dict) -> dict:
    """IT職場奇聞型單步生成。"""
    prompt = get_workplace_prompt(pillar_name, theme, script_hint, feedback_context, used_concepts)
    story = _call_gemini_json(prompt, WORKPLACE_SYSTEM_PROMPT)
    print(f"[LLM] 職場奇聞型生成完成：{story.get('tech_concept')} × {story.get('life_event')}")
    return story


def _generate_office(pillar_name: str, theme: str, script_hint: str,
                     feedback_context: str, used_concepts: dict) -> dict:
    """大人腹黑學型單步生成。"""
    prompt = get_office_prompt(pillar_name, theme, script_hint, feedback_context, used_concepts)
    story = _call_gemini_json(prompt, OFFICE_SYSTEM_PROMPT)
    print(f"[LLM] 大人腹黑學型生成完成：{story.get('tech_concept')} × {story.get('life_event')}")
    return story


def _generate_home_meme(pillar_name: str, theme: str, script_hint: str,
                         feedback_context: str, used_concepts: dict) -> dict:
    """家裡有工程師型單步生成。"""
    prompt = get_home_meme_prompt(pillar_name, theme, script_hint, feedback_context, used_concepts)
    story = _call_gemini_json(prompt, HOME_MEME_SYSTEM_PROMPT)
    print(f"[LLM] 家裡型生成完成：{story.get('tech_concept')} × {story.get('life_event')}")
    return story


def generate_content(day: int, pillar: str, pillar_name: str, theme: str,
                     content_type: str, script_hint: str = "",
                     feedback_context: str = "", used_concepts: dict = None) -> dict:
    """
    主生成函式，根據 content_type 路由：
      symptom_meme → 職場/辦公室症狀型單步
      home_meme    → 家裡有工程師型單步
      feynman      → 費曼教學型單步
      carousel     → 骨架 → 展開 → 編輯 → 說書人（原有流程）
    """
    used_concepts = used_concepts or {}

    # ── 症狀型 ──────────────────────────────────────────
    if content_type == "symptom_meme":
        story = _generate_symptom_meme(
            pillar_name, theme, script_hint, feedback_context, used_concepts
        )
        print("[LLM] 說書人審查 symptom_meme 敘事弧線...")
        story, narrative_pass = _narrate_symptom_meme_story(story)
        story["_narrative_pass"] = narrative_pass
        story["_content_type"] = content_type
        return story

    # ── 費曼教學型（舊格式，保留相容） ──────────────────────
    if content_type == "feynman":
        story = _generate_feynman(
            pillar_name, theme, script_hint, feedback_context, used_concepts
        )
        story["_narrative_pass"] = True
        story["_content_type"] = content_type
        return story

    # ── 技術白話型 ────────────────────────────────────────
    if content_type == "tech":
        story = _generate_tech(
            pillar_name, theme, script_hint, feedback_context, used_concepts
        )
        print("[LLM] 說書人審查 tech 比喻邏輯...")
        story, narrative_pass = _narrate_tech_story(story)
        story["_narrative_pass"] = narrative_pass
        story["_content_type"] = content_type
        return story

    # ── IT職場奇聞型 ─────────────────────────────────────
    if content_type == "workplace":
        story = _generate_workplace(
            pillar_name, theme, script_hint, feedback_context, used_concepts
        )
        print("[LLM] 說書人審查 workplace 邏輯節奏...")
        story, narrative_pass = _narrate_workplace_story(story)
        story["_narrative_pass"] = narrative_pass
        story["_content_type"] = content_type
        return story

    # ── 大人腹黑學型 ─────────────────────────────────────
    if content_type == "office":
        story = _generate_office(
            pillar_name, theme, script_hint, feedback_context, used_concepts
        )
        print("[LLM] 說書人審查 office 邏輯節奏...")
        story, narrative_pass = _narrate_office_story(story)
        story["_narrative_pass"] = narrative_pass
        story["_content_type"] = content_type
        return story

    # ── 家裡有工程師型 ───────────────────────────────────
    if content_type == "home_meme":
        story = _generate_home_meme(
            pillar_name, theme, script_hint, feedback_context, used_concepts
        )
        print("[LLM] 說書人審查 home_meme 敘事弧線...")
        story, narrative_pass = _narrate_home_meme_story(story)
        story["_narrative_pass"] = narrative_pass
        story["_content_type"] = content_type
        return story

    # ── 對話型（carousel，原有流程） ──────────────────────
    try:
        # ── Phase 1a ──
        outline = _generate_outline(
            day, pillar, pillar_name, theme, content_type,
            script_hint, feedback_context, used_concepts,
        )
        # ── Phase 1b ──
        print("[LLM] 骨架完成，展開完整腳本...")
        story = _generate_story_from_outline(outline, day, pillar, pillar_name, theme)
        # 骨架資料附加到 story，供 log 使用
        story["tech_concept"] = outline.get("tech_concept", "")
        story["life_event"]   = outline.get("life_event", "")

        # ── Phase 1c：對白優化 ──
        print("[LLM] 對白優化中...")
        story = _edit_story(story)

        # ── Phase 1d：說書人審查（回傳 pass/fail 給 main.py 決定是否重生） ──
        print("[LLM] 說書人審查敘事弧線...")
        story, narrative_pass = _narrate_story(story)
        story["_narrative_pass"] = narrative_pass  # main.py 讀取後自行刪除
        story["_content_type"] = content_type
        return story

    except Exception as e:
        print(f"[LLM] 兩段式生成失敗，fallback 單步：{e}")
        prompt = get_story_prompt(
            day, pillar, pillar_name, theme, content_type,
            script_hint, feedback_context, used_concepts,
        )
        story = _call_gemini_json(prompt, SYSTEM_PROMPT)
        story["_narrative_pass"] = True  # fallback 不重生
        story["_content_type"] = content_type
        return story


# ─────────────────────────────────────────────
# Phase 1c：對白編輯師
# ─────────────────────────────────────────────

def _edit_story(story: dict) -> dict:
    """逐頁優化對白品質。失敗時回傳原稿，不阻斷流程。"""
    try:
        prompt = get_editor_prompt(story)
        edited = _call_gemini_json(prompt, EDITOR_SYSTEM_PROMPT, max_tokens=4000)
        # 確保 tech_concept / life_event 不被 editor 丟失
        for key in ("tech_concept", "life_event"):
            if key in story and key not in edited:
                edited[key] = story[key]
        print("[LLM] 對白編輯完成")
        return edited
    except Exception as e:
        print(f"[LLM] 對白編輯失敗，使用原稿：{e}")
        return story


# ─────────────────────────────────────────────
# Phase 1d：說書人審查敘事弧線
# ─────────────────────────────────────────────

def _narrate_story(story: dict) -> tuple[dict, bool]:
    """
    審查故事弧線連貫性。
    回傳 (修正後的 story dict, narrative_pass: bool)。
    narrative_pass=False → 結構性斷裂，main.py 應重新生成整個 Phase 1。
    失敗時回傳 (story, True) 不阻斷流程。
    """
    import copy
    try:
        prompt = get_narrator_prompt(story)
        result = _call_gemini_json(prompt, NARRATOR_SYSTEM_PROMPT, max_tokens=2000)
        narrative_pass = bool(result.get("narrative_pass", True))
        patches = result.get("patches", [])
        notes = result.get("narrative_notes", "")

        corrected = copy.deepcopy(story)
        for patch in patches:
            target = patch.get("target")
            field = patch.get("field", "")
            value = patch.get("value", "")
            if target == "scene":
                page = patch.get("page")
                for scene in corrected.get("scenes", []):
                    if scene.get("page") == page:
                        scene[field] = value
                        break
            elif target == "top" and field:
                corrected[field] = value

        print(f"[LLM] 說書人審查完成（narrative_pass={narrative_pass}，patches={len(patches)}筆）：{notes}")
        return corrected, narrative_pass
    except Exception as e:
        print(f"[LLM] 說書人審查失敗，使用原稿繼續：{e}")
        return story, True


# ─────────────────────────────────────────────
# 症狀型說書人
# ─────────────────────────────────────────────

def _narrate_symptom_meme_story(story: dict) -> tuple[dict, bool]:
    """
    審查 symptom_meme 的 P2+P3→P4 邏輯橋接、P5 現實切入、P6 純動作。
    失敗時回傳 (story, True) 不阻斷流程。
    """
    import copy
    try:
        prompt = get_symptom_meme_narrator_prompt(story)
        result = _call_gemini_json(prompt, SYMPTOM_MEME_NARRATOR_SYSTEM_PROMPT, max_tokens=1000)
        narrative_pass = bool(result.get("narrative_pass", True))
        patches = result.get("patches", [])
        notes = result.get("narrative_notes", "")

        corrected = copy.deepcopy(story)
        for patch in patches:
            target = patch.get("target")
            field = patch.get("field", "")
            value = patch.get("value", "")
            if target == "scene":
                page = patch.get("page")
                for scene in corrected.get("scenes", []):
                    if scene.get("page") == page:
                        scene[field] = value
                        break
            elif target == "top" and field:
                corrected[field] = value

        print(f"[LLM] 症狀型說書人完成（narrative_pass={narrative_pass}，patches={len(patches)}筆）：{notes}")
        return corrected, narrative_pass
    except Exception as e:
        print(f"[LLM] 症狀型說書人失敗，使用原稿繼續：{e}")
        return story, True


# ─────────────────────────────────────────────
# 家裡型說書人
# ─────────────────────────────────────────────

def _narrate_home_meme_story(story: dict) -> tuple[dict, bool]:
    """
    審查 home_meme 的 P2+P3→P4 依賴邏輯橋接、P5 格式+現實、P6 純動作。
    失敗時回傳 (story, True) 不阻斷流程。
    """
    import copy
    try:
        prompt = get_home_meme_narrator_prompt(story)
        result = _call_gemini_json(prompt, HOME_MEME_NARRATOR_SYSTEM_PROMPT, max_tokens=1000)
        narrative_pass = bool(result.get("narrative_pass", True))
        patches = result.get("patches", [])
        notes = result.get("narrative_notes", "")

        corrected = copy.deepcopy(story)
        for patch in patches:
            target = patch.get("target")
            field = patch.get("field", "")
            value = patch.get("value", "")
            if target == "scene":
                page = patch.get("page")
                for scene in corrected.get("scenes", []):
                    if scene.get("page") == page:
                        scene[field] = value
                        break
            elif target == "top" and field:
                corrected[field] = value

        print(f"[LLM] 家裡型說書人完成（narrative_pass={narrative_pass}，patches={len(patches)}筆）：{notes}")
        return corrected, narrative_pass
    except Exception as e:
        print(f"[LLM] 家裡型說書人失敗，使用原稿繼續：{e}")
        return story, True


# ─────────────────────────────────────────────
# 技術白話說書人
# ─────────────────────────────────────────────

def _narrate_tech_story(story: dict) -> tuple[dict, bool]:
    """
    審查 tech 的 P3→P2 邏輯回應、P4 複述 P3 邏輯、P6 套回家庭非只提詞。
    失敗時回傳 (story, True) 不阻斷流程。
    """
    import copy
    try:
        prompt = get_tech_narrator_prompt(story)
        result = _call_gemini_json(prompt, TECH_NARRATOR_SYSTEM_PROMPT, max_tokens=1000)
        narrative_pass = bool(result.get("narrative_pass", True))
        patches = result.get("patches", [])
        notes = result.get("narrative_notes", "")

        corrected = copy.deepcopy(story)
        for patch in patches:
            target = patch.get("target")
            field = patch.get("field", "")
            value = patch.get("value", "")
            if target == "scene":
                page = patch.get("page")
                for scene in corrected.get("scenes", []):
                    if scene.get("page") == page:
                        scene[field] = value
                        break
            elif target == "top" and field:
                corrected[field] = value

        print(f"[LLM] 技術白話說書人完成（narrative_pass={narrative_pass}，patches={len(patches)}筆）：{notes}")
        return corrected, narrative_pass
    except Exception as e:
        print(f"[LLM] 技術白話說書人失敗，使用原稿繼續：{e}")
        return story, True


# ─────────────────────────────────────────────
# 職場奇聞說書人
# ─────────────────────────────────────────────

def _narrate_workplace_story(story: dict) -> tuple[dict, bool]:
    """
    審查 workplace 的 P3 升級自 P2、P5 針對具體奇聞、P6 有浮誇畫面感。
    失敗時回傳 (story, True) 不阻斷流程。
    """
    import copy
    try:
        prompt = get_workplace_narrator_prompt(story)
        result = _call_gemini_json(prompt, WORKPLACE_NARRATOR_SYSTEM_PROMPT, max_tokens=1000)
        narrative_pass = bool(result.get("narrative_pass", True))
        patches = result.get("patches", [])
        notes = result.get("narrative_notes", "")

        corrected = copy.deepcopy(story)
        for patch in patches:
            target = patch.get("target")
            field = patch.get("field", "")
            value = patch.get("value", "")
            if target == "scene":
                page = patch.get("page")
                for scene in corrected.get("scenes", []):
                    if scene.get("page") == page:
                        scene[field] = value
                        break
            elif target == "top" and field:
                corrected[field] = value

        print(f"[LLM] 職場奇聞說書人完成（narrative_pass={narrative_pass}，patches={len(patches)}筆）：{notes}")
        return corrected, narrative_pass
    except Exception as e:
        print(f"[LLM] 職場奇聞說書人失敗，使用原稿繼續：{e}")
        return story, True


# ─────────────────────────────────────────────
# 大人腹黑學說書人
# ─────────────────────────────────────────────

def _narrate_office_story(story: dict) -> tuple[dict, bool]:
    """
    審查 office 的 P4 Anna 邏輯問、P6 媽咪比喻精準映射 P2+P3、P5 合理化反讓荒謬更明顯。
    失敗時回傳 (story, True) 不阻斷流程。
    """
    import copy
    try:
        prompt = get_office_narrator_prompt(story)
        result = _call_gemini_json(prompt, OFFICE_NARRATOR_SYSTEM_PROMPT, max_tokens=1000)
        narrative_pass = bool(result.get("narrative_pass", True))
        patches = result.get("patches", [])
        notes = result.get("narrative_notes", "")

        corrected = copy.deepcopy(story)
        for patch in patches:
            target = patch.get("target")
            field = patch.get("field", "")
            value = patch.get("value", "")
            if target == "scene":
                page = patch.get("page")
                for scene in corrected.get("scenes", []):
                    if scene.get("page") == page:
                        scene[field] = value
                        break
            elif target == "top" and field:
                corrected[field] = value

        print(f"[LLM] 大人腹黑學說書人完成（narrative_pass={narrative_pass}，patches={len(patches)}筆）：{notes}")
        return corrected, narrative_pass
    except Exception as e:
        print(f"[LLM] 大人腹黑學說書人失敗，使用原稿繼續：{e}")
        return story, True


def review_story(story: dict) -> tuple[dict, bool]:
    """
    Phase 1.5 — 故事審稿員（外科手術模式）。
    僅適用 carousel 格式；symptom_meme / feynman 格式直接跳過。
    回傳 (修正後的 story dict, critical_pass: bool)。
    """
    import copy
    content_type = story.pop("_content_type", "carousel")
    if content_type != "carousel":
        print(f"[LLM] 審稿跳過（格式：{content_type}，非 carousel 不適用審稿規則）")
        return story, True

    prompt = get_review_prompt(story)
    try:
        result = _call_gemini_json(prompt, REVIEW_SYSTEM_PROMPT)
        notes         = result.get("revision_notes", "（無記錄）")
        critical_pass = bool(result.get("critical_pass", True))
        patches       = result.get("patches", [])

        # 外科手術：只把 patch 打進原稿，其他欄位完全不動
        corrected = copy.deepcopy(story)
        for patch in patches:
            target = patch.get("target")
            field  = patch.get("field", "")
            value  = patch.get("value", "")
            if target == "scene":
                page = patch.get("page")
                for scene in corrected.get("scenes", []):
                    if scene.get("page") == page:
                        scene[field] = value
                        break
            elif target == "top" and field:
                corrected[field] = value

        print(f"[LLM] 審稿完成（critical_pass={critical_pass}，patches={len(patches)}筆）：{notes}")
        return corrected, critical_pass

    except Exception as e:
        print(f"[LLM] 審稿失敗，使用原稿繼續：{e}")
        return story, True  # 炸掉時不阻斷流程


def generate_report(posts_data: list, insights_data: dict) -> str:
    """生成每日報告，使用 Gemini（非 JSON 模式）"""
    client = _gemini_client()
    prompt = get_report_prompt(posts_data, insights_data)

    for model in ["gemini-2.5-flash", "gemini-flash-latest"]:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        max_output_tokens=4000,
                    ),
                )
                print(f"[LLM] 報告使用模型：{model}")
                return response.text
            except Exception as e:
                print(f"[LLM] {model} 報告失敗（第{attempt+1}次）：{e}")
                break

    raise ValueError("Gemini 無法生成報告，請稍後重試")
