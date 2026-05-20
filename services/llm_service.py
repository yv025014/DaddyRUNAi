import os
import json
from google import genai
from google.genai import types
from config.prompts import SYSTEM_PROMPT, get_story_prompt, get_report_prompt


def _gemini_client():
    return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def _clean_json(raw: str) -> str:
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        return raw.strip()
    return raw[start:end + 1]


def generate_content(day: int, pillar: str, pillar_name: str, theme: str,
                     content_type: str, script_hint: str = "") -> dict:
    """生成今日繪本故事，使用 Gemini 2.5 Flash"""
    prompt = get_story_prompt(day, pillar, pillar_name, theme, content_type, script_hint)
    client = _gemini_client()

    for model in ["gemini-2.5-flash", "gemini-flash-latest"]:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        max_output_tokens=4000,
                        response_mime_type="application/json",
                    ),
                )
                result = json.loads(_clean_json(response.text))
                print(f"[LLM] 使用模型：{model}")
                return result
            except json.JSONDecodeError as e:
                print(f"[LLM] {model} JSON 解析失敗（第 {attempt+1} 次）：{e}")
            except Exception as e:
                print(f"[LLM] {model} 失敗：{e}")
                break

    raise ValueError("Gemini 無法生成有效內容，請稍後重試")


def generate_report(posts_data: list, insights_data: dict) -> str:
    """生成每日報告，使用 Gemini"""
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
                print(f"[LLM] {model} 報告失敗（第 {attempt+1} 次）：{e}")
                break

    raise ValueError("Gemini 無法生成報告，請稍後重試")
