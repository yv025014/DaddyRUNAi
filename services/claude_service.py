import os
import json
from google import genai
from google.genai import types
from config.prompts import SYSTEM_PROMPT, get_content_prompt, get_report_prompt


def _client():
    return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def _clean_json(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip().rstrip("```").strip()


def generate_content(day: int, pillar: str, pillar_name: str, theme: str, content_type: str) -> dict:
    """使用 Gemini Flash 生成今日貼文內容（免費方案）"""
    client = _client()
    prompt = get_content_prompt(day, pillar, pillar_name, theme, content_type)

    for attempt in range(3):
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=3000,
            ),
        )
        try:
            return json.loads(_clean_json(response.text))
        except json.JSONDecodeError as e:
            print(f"[Gemini] JSON 解析失敗（第 {attempt+1} 次）：{e}")

    raise ValueError("Gemini 回應無法解析為 JSON，請重試")


def generate_report(posts_data: list, insights_data: dict) -> str:
    """使用 Gemini Flash 生成每日報告（免費方案）"""
    client = _client()
    prompt = get_report_prompt(posts_data, insights_data)

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=2000,
        ),
    )

    return response.text
