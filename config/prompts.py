SYSTEM_PROMPT = """
你是「Chris｜工程師把拔」這個 IG 帳號的資深社群經營專家兼繪本作家。
帳號定位：全端工程師（.NET / React / MSSQL）＋五歲女兒 Anna 的把拔，台灣在地。
核心人設：用工程師腦袋 debug 人生，真實、有溫度、輕技術。
目標受眾：台灣工程師、科技業父母、想了解程式的一般人。
語言：繁體中文，口語化，避免過度正式。
稱謂規則：自稱「把拔」不用「爸爸」，女兒叫「Anna」，帳號名稱是「工程師把拔」。
內容形式：每篇貼文是一個5頁的繪本故事，透過 IG 輪播呈現。
"""

# 固定人設描述，每張圖都帶這段確保一致性
CHARACTER_BASE = (
    "Studio Ghibli-inspired illustration, detailed hand-drawn style, warm and vivid colors, "
    "Asian engineer dad Chris: early 30s, short brown hair, warm smile, pink casual t-shirt, shorts, Apple Watch on wrist. "
    "5-year-old Asian girl Anna: brown bob hair with bangs, big round eyes, cute expression, "
    "light blue dress with Totoro print, pink Crocs sandals. "
    "Soot sprites (susuwatari) hidden in background corners. "
    "No text in image, no watermark."
)


def get_story_prompt(day: int, pillar: str, pillar_name: str, theme: str, content_type: str) -> str:
    return f"""
今天是第 {day} 天，內容支柱：{pillar}（{pillar_name}），主題：{theme}，格式：{content_type}。

請創作一個5頁的繪本故事，透過 IG 輪播呈現。故事結構：
- 第1頁：場景開場（Hook，吸引停留滑下去）
- 第2頁：衝突或問題（引發讀者共鳴）
- 第3頁：過程或轉折（展現工程師把拔視角）
- 第4頁：解決或溫馨時刻（情感高峰）
- 第5頁：金句收尾（引發留言或分享）

以 JSON 格式回覆，不要有其他文字：

{{
  "story_title": "這個繪本故事的標題（8字以內）",
  "scenes": [
    {{
      "page": 1,
      "story_text": "這一頁的故事文字（繁體中文，30字以內，適合放在圖片下方或旁邊）",
      "image_prompt": "英文圖片生成 prompt，描述這一頁的場景畫面，具體描述 Chris 和 Anna 的動作表情與環境，不含文字"
    }},
    {{
      "page": 2,
      "story_text": "第2頁故事文字",
      "image_prompt": "第2頁英文圖片 prompt"
    }},
    {{
      "page": 3,
      "story_text": "第3頁故事文字",
      "image_prompt": "第3頁英文圖片 prompt"
    }},
    {{
      "page": 4,
      "story_text": "第4頁故事文字",
      "image_prompt": "第4頁英文圖片 prompt"
    }},
    {{
      "page": 5,
      "story_text": "第5頁金句（工程師哲學或親子溫馨語）",
      "image_prompt": "第5頁英文圖片 prompt，收尾畫面"
    }}
  ],
  "caption": "IG 貼文文案，約 100-150 字，包含 emoji，口語化繁體中文，開頭要有吸引人停留的第一句話，結尾留一個引發留言的問題",
  "hashtags": ["標籤1", "標籤2", "標籤3", "標籤4", "標籤5", "標籤6"],
  "story_text": "限時動態的互動問題或內容，否則填 null"
}}
"""


def get_report_prompt(posts_data: list, insights_data: dict) -> str:
    return f"""
以下是過去幾天的 IG 貼文數據與成效：

發文紀錄：
{posts_data}

各貼文 Insights：
{insights_data}

請生成一份繁體中文的「每日成效報告與策略修正建議」，包含：
1. 數據摘要（哪支表現最好/最差，原因分析）
2. 演算法訊號解讀（完播率、存數、留言哪個最強）
3. 明日內容策略建議（主題微調、腳本方向、發文時間建議）
4. 一句鼓勵的話給帳號主理人

請用 Markdown 格式輸出，加上適當標題。
"""
