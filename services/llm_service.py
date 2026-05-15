import os
import json
from google import genai
from google.genai import types
from config.prompts import SYSTEM_PROMPT, get_story_prompt, get_report_prompt


def _client():
    return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def _clean_json(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip().rstrip("```").strip()


def generate_content(day: int, pillar: str, pillar_name: str, theme: str,
                     content_type: str, script_hint: str = "") -> dict:
    """使用 Gemini 2.5 Flash 生成今日繪本故事內容"""
    client = _client()
    prompt = get_story_prompt(day, pillar, pillar_name, theme, content_type, script_hint)

    # 優先用 2.5 Pro（品質最好），失敗則降級用 Flash
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
                result = json.loads(_clean_json(response.text))
                print(f"[Gemini] 使用模型：{model}")
                return result
            except json.JSONDecodeError as e:
                print(f"[Gemini] {model} JSON 解析失敗（第 {attempt+1} 次）：{e}")
            except Exception as e:
                print(f"[Gemini] {model} 失敗：{e}")
                break  # 換下一個模型

    raise ValueError("所有模型均無法生成有效內容，請重試")


def generate_report(posts_data: list, insights_data: dict) -> str:
    """使用 Gemini 2.5 Flash 生成每日報告"""
    client = _client()
    prompt = get_report_prompt(posts_data, insights_data)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=2000,
        ),
    )
    return response.text
