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
請創作一個7頁的繪本故事，透過 IG 輪播呈現。

角色：
- Chris 把拔：工程師，喜歡用技術邏輯解釋家庭問題，但總是反被家人用同樣邏輯反殺
- Anna：五歲女兒，邏輯直接犀利，會用把拔自己說的話反問把拔
- 媽咪：全家最有殺氣的人，記得所有把拔的小辮子，補刀不需要超過15字

故事公式（7頁節奏，缺一不可）：
- 第1頁【Hook】Anna 丟出一個讓把拔當場愣住的問題，與技術主題有隱性連結但還沒點明
- 第2頁【建立】把拔自信地用生活比喻解釋技術概念，要埋下會被反殺的邏輯漏洞
- 第3頁【第一次反將】Anna 用把拔第2頁說的話，反問把拔某個真實的失誤或缺點
- 第4頁【嘴硬】把拔試圖解釋或辯解，把自己挖到更深的洞
- 第5頁【致命補刀】媽咪用一句話精準補刀，引用一個把拔逃不掉的具體把柄
- 第6頁【沉默頁】把拔被打敗的反應，台詞極短（5-10字），可以是一句嘆氣、一個動作描述、或一句逃避
- 第7頁【金句】把拔自嘲金句收尾，這頁台詞 = 整篇的金句（quote 欄位）

技術白話原則（非常重要）：
1. 比喻只能用讀者生活中真的用過的東西（超商、手機、外送、Line 等）
2. 禁止說「就像圖書館」「就像資料夾」這種陳腔濫調比喻
3. 每頁台詞讀者看完要有「原來如此」的感覺，而不只是覺得好笑
4. 讀完整篇的人，要能用一句話向朋友解釋這個技術概念

爆款結構原則（非常重要）：

【第1頁 Hook — 強制使用 Anna 開場，把拔不說話】
Anna 必須問一個「讓把拔當場愣住」的問題，這個問題要同時：
  1. 跟今天的技術主題有隱性連結（但還沒點明）
  2. 讓觀眾看了想知道「把拔怎麼回答」

強Hook範例（照這個層級寫）：
  「把拔，你說你記得所有 bug 在哪，那你記不記得上次答應我去動物園是哪天？」
  「把拔，你說資料不會消失，那媽咪生氣的事你為什麼會忘？」
  「把拔，你的電腦記得那麼多事，那它有沒有存你欠媽咪多少次道歉？」

禁止用「把拔發現問題」或「把拔主動解釋」當第1頁開場。

【第2頁 — 把拔解釋，但要埋下被反將的地雷】
把拔用白話比喻解釋技術概念（比喻要新鮮，禁用圖書館/資料夾）。
這頁要讓把拔說出一句「聽起來很合理但可以被反將的邏輯」。

【第3頁 — Anna 反將一軍，這是整篇的靈魂】
Anna 用把拔在第2頁說的那句邏輯，指向把拔自己的某個真實缺點或失誤。
把拔必須沉默或說不出話。
這一頁的笑點要讓人「先笑、再覺得有點心酸、再覺得超準」。

【第5頁 — 媽咪致命補刀（不是教學！）】

媽咪在這頁的角色是**全家最有殺氣的人**，不是老師。
技術白話的任務已經在第2頁把拔那邊完成了，媽咪這頁的任務是**讓笑點升級到讓人想截圖**。

硬性規則：
1. 字數 ≤ 20 字
2. 必須引用一個「把拔逃不掉的具體把柄」（欠的承諾、藏的零食、忘記的紀念日、找不到的東西）
3. 句型要有殺氣或威脅感，不能像在解釋
4. 必須讓技術概念以「武器」的方式出現，不是以「定義」的方式出現

錯誤示範（請避免，這是上課語氣）：
  ❌「資料庫就是 7-11 的收銀機，每筆消費都有紀錄、隨時查得到」
  ❌「資料庫就是把所有重要的事好好收起來的地方」
正確示範（這才是媽咪該說的話）：
  ✅「資料庫就是我的記帳本，你欠的每次倒垃圾都還在。」
  ✅「我手機相簿就是資料庫，你每張黑歷史我都留著。」
  ✅「我腦袋裡的資料庫從不當機，特別是你犯錯那欄。」

【第6頁 — 沉默頁，留白給笑點呼吸】

把拔被打敗的反應頁，台詞極短，5-10 字。
可以是：嘆氣 / 想逃避的動作 / 認輸前的小掙扎。
這頁的功能是讓第5頁的笑點發酵，不是又一個笑點。

範例：
  ✅「...我先去洗碗。」
  ✅「資料庫，可以 rollback 嗎？」
  ✅「（默默放下手機）」
  ✅「我什麼都沒說。」

【第7頁金句 — 整篇靈魂，必須能單獨爆款】

硬性規則（缺一不可）：
1. 字數 ≤ 25 字，越短越好
2. 技術詞彙最多出現 1 個
3. 金句必須能「脫離故事獨立成立」——把金句單獨拿給沒看過前4頁的人，他也要覺得有共鳴
4. 必須跟第1頁 Hook 的情境呼應（首尾呼應，不能換主題）
5. 金句裡必須有「具體的人物或物件」，禁止只有抽象概念

爆款金句公式（任選一種）：
公式A 時間反差：
  例：「以前我擔心資料庫被駭，現在我擔心女兒會查資料庫。」
公式B 身份反差：
  例：「在家裡最危險的不是駭客，是學會看訂單紀錄的女兒。」
公式C 認輸金句（最容易爆）：
  例：「工程師最後悔的事，是教會家人用查詢功能。」

錯誤示範：
  ❌「最難的不是程式，是白話文」（純抽象、沒人物）
  ❌「資料庫不會記錯，但把拔的記憶會自動格式化」（技術詞太多、跟Hook脫節）

【第7頁台詞 = 金句，必須完全一致】
第7頁 story_text 和 quote 必須是同一句話，不要寫兩個版本。
這樣 IG 輪播最後一張和金句卡才能形成完美呼應。

以 JSON 格式回覆，不要有其他文字：

{{
  "story_title": "故事標題（8字以內，有吸引力）",
  "quote": "第5頁的金句，單獨放在深色背景頁，20字以內，有哲學感或自嘲感",
  "scenes": [
    {{
      "page": 1,
      "speaker": "anna",
      "mood": "curious",
      "story_text": "第1頁 Hook：Anna 丟出讓把拔愣住的問題（40字內）",
      "background": "dining_room"
    }},
    {{
      "page": 2,
      "speaker": "chris",
      "mood": "proud",
      "story_text": "第2頁 把拔用生活比喻自信解釋技術（45字內，要埋下會被反殺的邏輯漏洞）",
      "background": "dining_room"
    }},
    {{
      "page": 3,
      "speaker": "anna",
      "mood": "smirk",
      "story_text": "第3頁 Anna 用把拔第2頁的話反問把拔（40字內）",
      "background": "dining_room"
    }},
    {{
      "page": 4,
      "speaker": "chris",
      "mood": "embarrassed",
      "story_text": "第4頁 把拔嘴硬辯解，把自己挖更深的洞（35字內）",
      "background": "dining_room"
    }},
    {{
      "page": 5,
      "speaker": "mom",
      "mood": "deadpan",
      "story_text": "第5頁 媽咪致命補刀（20字內，引用具體把柄，要有殺氣）",
      "background": "dining_room"
    }},
    {{
      "page": 6,
      "speaker": "chris",
      "mood": "defeated",
      "story_text": "第6頁 沉默頁，把拔認輸前的小掙扎（5-10字）",
      "background": "dining_room"
    }},
    {{
      "page": 7,
      "speaker": "chris",
      "mood": "defeated",
      "story_text": "第7頁 金句（和 quote 欄位完全一致，25字內）",
      "background": "dining_room"
    }}
  ],
  "caption": "IG 貼文文案，80-120字。結構：第1句重述Hook吸住觀眾，中間2-3句白話補充技術概念，最後一句留一個能引發留言的問題。emoji ≤ 3個。禁止在caption裡寫hashtag（#開頭的詞），hashtag統一放在hashtags欄位。禁止寫『今天Anna問了一個...』這種劇透式廢話。",
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
