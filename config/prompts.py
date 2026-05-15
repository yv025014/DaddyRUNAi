SYSTEM_PROMPT = """
你是「Chris｜工程師把拔」這個 IG 帳號的資深社群經營專家兼繪本作家。
帳號定位：全端工程師（.NET / React / MSSQL）＋五歲女兒 Anna 的把拔，台灣在地。
核心人設：用工程師腦袋 debug 人生，真實、有溫度、輕技術。
目標受眾：台灣工程師、科技業父母、想了解程式的一般人。
語言：繁體中文，口語化，避免過度正式。

角色設定：
- 把拔（Chris）：全端工程師，喜歡用工程師術語解釋一切，常常被家人看穿
- 媽咪：務實、溫暖，偶爾也會補刀把拔，是家裡的定海神針
- Anna：五歲，看起來比把拔還懂事，語出驚人，是全家的笑點來源

稱謂規則：
- 把拔自稱「把拔」不用「爸爸」
- 女兒叫「Anna」
- 帳號名稱是「工程師把拔」
- 媽咪可以叫「媽咪」或讓 Anna 叫「媽」

內容形式：每篇貼文是一個5頁的繪本故事，透過 IG 輪播呈現。
媽咪可以出現在故事裡，增加家庭感與真實感，但把拔和 Anna 是主角。
"""

# 固定人設描述，每張圖都帶這段確保一致性
# 風格參考：半寫實現代漫畫風，乾淨線條，飽和色彩，台灣在地感
CHARACTER_BASE = (
    "Semi-realistic modern manga illustration style, detailed clean line art, "
    "vibrant saturated colors, cel-shading with soft highlights, "
    "realistic body proportions, high detail on clothing and accessories, "
    "authentic Taiwan daily life settings. "
    "Dad Chris (把拔): tall lean Asian man, early 30s, short straight black hair, "
    "dark navy baseball cap, white graphic t-shirt, light blue jeans, "
    "black backpack, digital watch on left wrist, warm confident smile, "
    "clean-cut appearance. "
    "Mom (媽咪): Asian woman, early 30s, medium-length straight black hair, "
    "blue logo baseball cap, navy blue t-shirt, white pearl bracelet, "
    "small chain shoulder bag, bright cheerful smile, big expressive eyes. "
    "Daughter Anna: 5-6 year old Asian girl, straight black hair with blunt bangs, "
    "shoulder-length hair, very big bright eyes that curve into crescents when smiling, "
    "colorful casual clothes, small sneakers, full of energy and confidence. "
    "No text in image, no watermark, no speech bubbles."
)


def get_story_prompt(day: int, pillar: str, pillar_name: str, theme: str,
                     content_type: str, script_hint: str = "") -> str:
    hint_section = f"\n腳本大綱提示（請依此發展，但可以自由發揮細節）：\n{script_hint}\n" if script_hint else ""
    return f"""
今天是第 {day} 天，內容支柱：{pillar}（{pillar_name}），主題：{theme}。
{hint_section}
請創作一個5頁的繪本故事，透過 IG 輪播呈現。

角色：
- Chris 把拔：工程師，遇到問題喜歡過度分析，常被家人看穿
- Anna：五歲女兒，邏輯直接犀利，一句話讓把拔啞口無言
- 媽咪：務實溫暖，善於在對話最後補刀收尾

故事公式：
- 第1頁：把拔遇到狀況（Hook，讓人想滑下去）
- 第2頁：把拔用工程師思維解釋或應對
- 第3頁：Anna 一句話直接拆穿
- 第4頁：媽咪補刀 or Anna 繼續追問
- 第5頁：把拔心得（自嘲金句，引發留言）

以 JSON 格式回覆，不要有其他文字：

{{
  "story_title": "故事標題（8字以內，有吸引力）",
  "quote": "第5頁的金句，單獨放在深色背景頁，20字以內，有哲學感或自嘲感",
  "scenes": [
    {{
      "page": 1,
      "speaker": "chris",
      "mood": "normal",
      "story_text": "這一頁的對話或獨白（繁體中文，40字以內）",
      "background": "dining_room"
    }},
    {{
      "page": 2,
      "speaker": "chris",
      "mood": "proud",
      "story_text": "第2頁文字",
      "background": "dining_room"
    }},
    {{
      "page": 3,
      "speaker": "anna",
      "mood": "smirk",
      "story_text": "第3頁文字",
      "background": "dining_room"
    }},
    {{
      "page": 4,
      "speaker": "mom",
      "mood": "facepalm",
      "story_text": "第4頁文字",
      "background": "dining_room"
    }},
    {{
      "page": 5,
      "speaker": "chris",
      "mood": "defeated",
      "story_text": "第5頁金句（把拔自嘲收尾）",
      "background": "dining_room"
    }}
  ],
  "caption": "IG 貼文文案，約 100-150 字，包含 emoji，口語化繁體中文，開頭第一句要讓人停住，結尾留一個引發留言的問題",
  "hashtags": ["工程師把拔", "工程師日常", "親子日常", "台灣工程師", "科技爸爸", "Anna語錄"]
}}

speaker 只能是 "chris" | "anna" | "mom"
mood 只能是：
  chris: normal | proud | defeated | surprised | thinking | confused | embarrassed
  anna:  happy | smirk | pointing | proud | curious
  mom:   smiling | facepalm | proud | deadpan | skeptical
background 只能是：dining_room | living_room | office_desk | bedroom | outdoor_park
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
