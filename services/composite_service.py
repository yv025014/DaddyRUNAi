"""
composite_service.py
背景 + 角色立繪（自動去背）+ 對話文字 → IG 輪播單頁
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.parent
CHAR_DIR = BASE_DIR / "assets" / "characters"
BG_DIR = BASE_DIR / "assets" / "backgrounds"

CANVAS_W, CANVAS_H = 1080, 1350

FONT_PATH = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc"
FONT_FALLBACK = "/System/Library/Fonts/STHeiti Medium.ttc"

SPEAKER_COLORS = {
    "chris": (52, 120, 246),
    "anna":  (229, 77, 114),
    "mom":   (56, 161, 105),
}
SPEAKER_LABELS = {
    "chris": "Chris 把拔",
    "anna":  "Anna",
    "mom":   "媽咪",
}


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    # PingFang TC Regular=index 2, Medium=index 6, Semibold=index 10
    idx = 10 if bold else 2
    try:
        return ImageFont.truetype(FONT_PATH, size, index=idx)
    except Exception:
        pass
    try:
        return ImageFont.truetype(FONT_FALLBACK, size)
    except Exception:
        pass
    return ImageFont.load_default()


def _load_bg(name: str) -> Image.Image:
    for ext in ("png", "jpg", "jpeg"):
        p = BG_DIR / f"{name}.{ext}"
        if p.exists():
            img = Image.open(p).convert("RGB")
            # cover-crop to canvas
            r = img.width / img.height
            cr = CANVAS_W / CANVAS_H
            if r > cr:
                nw, nh = int(CANVAS_H * r), CANVAS_H
            else:
                nw, nh = CANVAS_W, int(CANVAS_W / r)
            img = img.resize((nw, nh), Image.LANCZOS)
            l, t = (nw - CANVAS_W) // 2, (nh - CANVAS_H) // 2
            return img.crop((l, t, l + CANVAS_W, t + CANVAS_H))
    raise FileNotFoundError(f"找不到背景：{name}")


def _remove_bg(img: Image.Image) -> Image.Image:
    """用 rembg 去除灰色背景，回傳 RGBA"""
    try:
        from rembg import remove
        return remove(img)
    except Exception as e:
        print(f"[Composite] rembg 失敗，改用顏色去背：{e}")
        return _chroma_key(img)


def _chroma_key(img: Image.Image, tolerance: int = 30) -> Image.Image:
    """備援：取左上角顏色作為背景色，顏色相近的像素設為透明"""
    img = img.convert("RGBA")
    data = img.load()
    bg = data[0, 0][:3]
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = data[x, y]
            if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) < tolerance * 3:
                data[x, y] = (r, g, b, 0)
    return img


def _load_char(speaker: str, mood: str, height: int = 780) -> Image.Image | None:
    p = CHAR_DIR / speaker / f"{mood}.png"
    if not p.exists():
        print(f"[Composite] 找不到角色圖：{p}，改用 normal")
        p = CHAR_DIR / speaker / "normal.png"
    if not p.exists():
        return None

    img = Image.open(p)
    if img.mode != "RGBA":
        img = _remove_bg(img)

    ratio = height / img.height
    nw = int(img.width * ratio)
    return img.resize((nw, height), Image.LANCZOS)


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    result = []
    for paragraph in text.split("\n"):
        cur = ""
        for ch in paragraph:
            test = cur + ch
            if font.getbbox(test)[2] > max_w and cur:
                result.append(cur)
                cur = ch
            else:
                cur = test
        if cur:
            result.append(cur)
    return result


def _draw_text_box(draw: ImageDraw.ImageDraw, canvas: Image.Image,
                   speaker: str, text: str, page: int, total: int):
    """底部白色圓角文字框 + 說話者標籤 + 對話 + 頁碼"""
    box_top = CANVAS_H - 370
    box_margin = 32

    # 白色圓角底板
    overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle(
        [(box_margin, box_top), (CANVAS_W - box_margin, CANVAS_H - box_margin)],
        radius=28,
        fill=(255, 255, 255, 235),
    )
    canvas.paste(Image.alpha_composite(
        Image.new("RGBA", canvas.size, (0, 0, 0, 0)), overlay
    ).convert("RGB"), mask=overlay.split()[3])

    # 說話者標籤（彩色）
    color = SPEAKER_COLORS.get(speaker, (80, 80, 80))
    label = SPEAKER_LABELS.get(speaker, speaker)
    lf = _font(36)
    draw.text((box_margin + 36, box_top + 26), label, font=lf, fill=color)

    # 對話文字
    tf = _font(50)
    lines = _wrap(text, tf, CANVAS_W - box_margin * 2 - 72)
    y = box_top + 82
    for line in lines[:4]:
        draw.text((box_margin + 36, y), line, font=tf, fill=(28, 28, 28))
        y += 64

    # 頁碼（右下角）
    pf = _font(30)
    label_p = f"{page}  /  {total}"
    pw = pf.getbbox(label_p)[2]
    draw.text((CANVAS_W - box_margin - pw - 20, CANVAS_H - box_margin - 40),
              label_p, font=pf, fill=(180, 180, 180))


def render_cover(background: str, title: str,
                 output_path: str, total: int = 6) -> bool:
    """第 1 頁封面：背景 + 標題"""
    try:
        canvas = _load_bg(background).convert("RGBA")
        draw = ImageDraw.Draw(canvas)

        # 底部漸層暗化
        grad = Image.new("RGBA", (CANVAS_W, 500), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad)
        for i in range(500):
            alpha = int(200 * (i / 500))
            gd.line([(0, i), (CANVAS_W, i)], fill=(0, 0, 0, alpha))
        canvas.alpha_composite(grad, dest=(0, CANVAS_H - 500))

        draw = ImageDraw.Draw(canvas)

        # 標題（置中）
        tf = _font(62, bold=True)
        lines = _wrap(title, tf, CANVAS_W - 120)
        y = CANVAS_H - 300
        for line in lines[:3]:
            lw = tf.getbbox(line)[2]
            draw.text(((CANVAS_W - lw) // 2, y), line, font=tf, fill=(255, 255, 255))
            y += 82

        # 帳號名（置中）
        af = _font(32)
        aw = af.getbbox("工程師把拔")[2]
        draw.text(((CANVAS_W - aw) // 2, CANVAS_H - 70), "工程師把拔", font=af, fill=(200, 200, 200))

        # 頁碼
        pf = _font(30)
        lp = f"1  /  {total}"
        pw = pf.getbbox(lp)[2]
        draw.text((CANVAS_W - 60 - pw, CANVAS_H - 70), lp, font=pf, fill=(200, 200, 200))

        canvas.convert("RGB").save(output_path, "JPEG", quality=95)
        print(f"[Composite] 封面完成：{output_path}")
        return True
    except Exception as e:
        print(f"[Composite] 封面失敗：{e}")
        return False


def render_dialogue(background: str, speaker: str, mood: str,
                    story_text: str, page: int, total: int,
                    output_path: str) -> bool:
    """第 2-5 頁對話頁：背景 + 角色立繪 + 文字框"""
    try:
        canvas = _load_bg(background).convert("RGBA")

        # 角色立繪
        char = _load_char(speaker, mood, height=780)
        if char:
            char_y = CANVAS_H - 370 - char.height + 40
            if speaker == "anna":
                char_x = CANVAS_W - char.width - 10
            else:
                char_x = 10
            canvas.alpha_composite(char, dest=(char_x, max(0, char_y)))

        # 文字框
        rgb = canvas.convert("RGB")
        draw = ImageDraw.Draw(rgb)
        _draw_text_box(draw, rgb, speaker, story_text, page, total)

        rgb.save(output_path, "JPEG", quality=95)
        print(f"[Composite] 第 {page} 頁完成：{output_path}")
        return True
    except Exception as e:
        print(f"[Composite] 第 {page} 頁失敗：{e}")
        return False


def render_final(quote: str, output_path: str, total: int = 6) -> bool:
    """最後一頁金句收尾：深色背景 + 大字"""
    try:
        canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (22, 30, 58))
        draw = ImageDraw.Draw(canvas)

        # 裝飾線
        lc = (80, 110, 200)
        draw.line([(80, 480), (CANVAS_W - 80, 480)], fill=lc, width=2)
        draw.line([(80, CANVAS_H - 480), (CANVAS_W - 80, CANVAS_H - 480)], fill=lc, width=2)

        # 金句（置中）
        qf = _font(54, bold=True)
        lines = _wrap(quote, qf, CANVAS_W - 160)
        total_h = len(lines) * 76
        y = (CANVAS_H - total_h) // 2
        for line in lines:
            lw = qf.getbbox(line)[2]
            draw.text(((CANVAS_W - lw) // 2, y), line, font=qf, fill=(255, 255, 255))
            y += 76

        # 帳號 + 頁碼
        af = _font(32)
        draw.text((80, CANVAS_H - 100), "@工程師把拔", font=af, fill=(120, 150, 220))
        pf = _font(30)
        lp = f"{total}  /  {total}"
        pw = pf.getbbox(lp)[2]
        draw.text((CANVAS_W - 80 - pw, CANVAS_H - 100), lp, font=pf, fill=(120, 130, 160))

        canvas.save(output_path, "JPEG", quality=95)
        print(f"[Composite] 金句頁完成：{output_path}")
        return True
    except Exception as e:
        print(f"[Composite] 金句頁失敗：{e}")
        return False


def render_carousel(story: dict, output_dir: str) -> list[str]:
    """
    主入口：根據 Claude 輸出的 story dict 渲染完整輪播。
    story 格式：
    {
      "story_title": "...",
      "cover_background": "dining_room",
      "quote": "...",
      "scenes": [
        {"page": 1, "speaker": "chris", "mood": "proud",
         "story_text": "...", "background": "dining_room"},
        ...
      ]
    }
    回傳所有 slide 路徑。
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    scenes = story.get("scenes", [])
    total = len(scenes) + 2  # 封面 + 對話頁 + 金句頁
    paths = []

    # 封面
    p = f"{output_dir}/slide_01.jpg"
    if render_cover(story.get("cover_background", "dining_room"),
                    story.get("story_title", ""), p, total):
        paths.append(p)

    # 對話頁
    for scene in scenes:
        page_num = scene["page"] + 1
        p = f"{output_dir}/slide_{page_num:02d}.jpg"
        if render_dialogue(
            background=scene.get("background", "dining_room"),
            speaker=scene["speaker"],
            mood=scene["mood"],
            story_text=scene["story_text"],
            page=page_num,
            total=total,
            output_path=p,
        ):
            paths.append(p)

    # 金句頁
    quote = story.get("quote", scenes[-1]["story_text"] if scenes else "")
    p = f"{output_dir}/slide_{total:02d}.jpg"
    if render_final(quote, p, total):
        paths.append(p)

    print(f"[Composite] 完成，共 {len(paths)} 頁：{output_dir}")
    return paths
