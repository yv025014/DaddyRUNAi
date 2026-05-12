SYSTEM_PROMPT = """
你是「Chris｜工程師把拔」這個 IG 帳號的資深社群經營專家。
帳號定位：全端工程師（.NET / React / MSSQL）＋五歲女兒 Anna 的把拔，台灣在地。
核心人設：用工程師腦袋 debug 人生，真實、有溫度、輕技術。
目標受眾：台灣工程師、科技業父母、想了解程式的一般人。
語言：繁體中文，口語化，避免過度正式。
稱謂規則：自稱「把拔」不用「爸爸」，女兒叫「Anna」，帳號名稱是「工程師把拔」。
"""

def get_content_prompt(day: int, pillar: str, pillar_name: str, theme: str, content_type: str) -> str:
    return f"""
今天是第 {day} 天，內容支柱：{pillar}（{pillar_name}），主題：{theme}，格式：{content_type}。

請生成以下內容，以 JSON 格式回覆，不要有其他文字：

{{
  "script": "Reels 腳本（如為 reels 類型），包含：Hook（0-3秒文字）、主體3個重點、結尾CTA。如為 photo/story 類型則填入貼文概念說明。",
  "caption": "IG 貼文文案，約 100-150 字，包含 emoji，口語化繁體中文，結尾留一個引發留言的問題",
  "hashtags": ["標籤1", "標籤2", "標籤3", "標籤4", "標籤5"],
  "image_prompt": "給圖片生成 AI 的英文 prompt，描述一張適合這篇貼文封面的插圖，必須採用 Studio Ghibli style by Hayao Miyazaki，溫暖手繪水彩質感，柔和色調，不含任何文字",
  "story_text": "如果有限時動態要更新，這裡是限時動態的互動問題或內容，否則填 null"
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
