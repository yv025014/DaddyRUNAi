"""
文字入圖服務 — 台灣 IG 圓體排版風格
字體：jf open 粉圓（justfont 開源，最常見台灣 IG 排版）

版面設計：
  第1頁（Hook）：底部大標題 + 小副標，深色半透明底條
  第2-4頁（故事）：底部文字條 + 右下角頁碼圓點
  第5頁（金句）：中央居中大字，上下裝飾線
"""

import pathlib
import textwrap
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = pathlib.Path(__file__).parent.parent / "assets" / "fonts" / "jf-openhuninn.ttf"
TOTAL_PAGES = 5

# ── 顏色 ──────────────────────────────────────────────
WHITE       = (255, 255, 255, 255)
WHITE_90    = (255, 255, 255, 230)
BLACK_60    = (0,   0,   0,   153)  # 60% 透明黑底條
DARK_80     = (20,  20,  20,  204)  # 頁碼條背景
ACCENT      = (255, 105, 97,  255)  # 珊瑚橘，頁碼點 active
ACCENT_PALE = (255, 200, 196, 180)  # 淡珊瑚，頁碼點 inactive
LINE_COLOR  = (255, 255, 255, 180)  # 金句頁裝飾線


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(FONT_PATH), size)
    except Exception:
        return ImageFont.load_default()


def _draw_rounded_rect(draw: ImageDraw, xy, radius: int, fill):
    """畫圓角矩形（Pillow 9+ 有內建，這裡兼容舊版）"""
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)


def _page_dots(draw: ImageDraw, img_w: int, y: int, current: int, total: int):
    """底部頁碼圓點指示器"""
    dot_r = 6
    gap = 20
    total_w = total * (dot_r * 2) + (total - 1) * gap
    x_start = (img_w - total_w) // 2
    for i in range(total):
        cx = x_start + i * (dot_r * 2 + gap) + dot_r
        color = ACCENT if i == current - 1 else ACCENT_PALE
        draw.ellipse([cx - dot_r, y - dot_r, cx + dot_r, y + dot_r], fill=color)


def _wrap_text(text: str, font, max_width: int) -> list[str]:
    """
    按像素寬度換行，中英混排：
    - 中文逐字切
    - 英文/數字連續序列視為一個 token，不拆斷
    """
    import re
    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    # 把文字切成 tokens：英數字串 or 單一中文字/符號
    tokens = re.findall(r'[A-Za-z0-9_\-\.]+|[^\s]', text)

    lines = []
    current = ""
    for token in tokens:
        # 嘗試加上空格（英文 token 前）
        sep = " " if current and re.match(r'^[A-Za-z0-9]', token) and re.search(r'[A-Za-z0-9]$', current) else ""
        test = current + sep + token
        bbox = dummy_draw.textbbox((0, 0), test, font=font)
        if bbox[2] > max_width and current:
            lines.append(current)
            current = token
        else:
            current = test
    if current:
        lines.append(current)
    return lines


# ─────────────────────────────────────────────────────
# 各頁排版函數
# ─────────────────────────────────────────────────────

def _overlay_page1(img: Image.Image, story_text: str, title: str) -> Image.Image:
    """
    第1頁：底部大標題 + 故事開場文字
    ╔════════════════╗
    │  (圖片)        │
    │                │
    ├────────────────┤  ← 底部 28%
    │ 大標題（諧音梗）│  大字
    │ 故事第一句     │  小字
    │  • • • • •    │  頁碼點
    ╚════════════════╝
    """
    w, h = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 底條高度
    bar_h = int(h * 0.30)
    bar_y = h - bar_h

    # 漸層底條（用多層半透明黑）
    for i in range(bar_h):
        alpha = int(180 * (i / bar_h) ** 0.6)
        draw.line([(0, bar_y + i), (w, bar_y + i)], fill=(10, 10, 10, alpha))

    # 大標題
    font_title = _load_font(int(h * 0.072))
    font_sub   = _load_font(int(h * 0.040))

    title_lines = _wrap_text(title, font_title, int(w * 0.85))
    title_total_h = len(title_lines) * int(h * 0.082)
    title_y = bar_y + int(bar_h * 0.08)

    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        lw = bbox[2] - bbox[0]
        draw.text(((w - lw) // 2, title_y), line, font=font_title, fill=WHITE)
        title_y += int(h * 0.082)

    # 副標（故事文字）
    sub_lines = _wrap_text(story_text, font_sub, int(w * 0.82))
    sub_y = title_y + int(h * 0.008)
    for line in sub_lines[:2]:
        bbox = draw.textbbox((0, 0), line, font=font_sub)
        lw = bbox[2] - bbox[0]
        draw.text(((w - lw) // 2, sub_y), line, font=font_sub,
                  fill=(240, 240, 240, 210))
        sub_y += int(h * 0.046)

    # 頁碼點
    _page_dots(draw, w, h - int(h * 0.025), 1, TOTAL_PAGES)

    result = Image.alpha_composite(img.convert("RGBA"), overlay)
    return result.convert("RGB")


def _overlay_page_mid(img: Image.Image, story_text: str, page: int) -> Image.Image:
    """
    第2-4頁：底部文字條
    ╔════════════════╗
    │  (圖片)        │
    │                │
    ├────────────────┤  ← 底部 22%
    │  故事文字      │  圓角框
    │  • • • • •    │  頁碼點
    ╚════════════════╝
    """
    w, h = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    bar_h = int(h * 0.23)
    bar_y = h - bar_h

    # 底部漸層
    for i in range(bar_h):
        alpha = int(200 * (i / bar_h) ** 0.5)
        draw.line([(0, bar_y + i), (w, bar_y + i)], fill=(10, 10, 10, alpha))

    # 文字框（圓角）
    pad_x = int(w * 0.06)
    pad_y = int(h * 0.018)
    box_y0 = bar_y + pad_y
    box_y1 = h - int(h * 0.062)
    _draw_rounded_rect(draw, [pad_x, box_y0, w - pad_x, box_y1],
                       radius=16, fill=(0, 0, 0, 100))

    # 故事文字
    font_story = _load_font(int(h * 0.044))
    lines = _wrap_text(story_text, font_story, int(w * 0.80))
    text_h = len(lines) * int(h * 0.052)
    box_mid = (box_y0 + box_y1) // 2
    text_y = box_mid - text_h // 2 - int(h * 0.006)

    for line in lines[:3]:
        bbox = draw.textbbox((0, 0), line, font=font_story)
        lw = bbox[2] - bbox[0]
        draw.text(((w - lw) // 2, text_y), line, font=font_story, fill=WHITE)
        text_y += int(h * 0.052)

    # 頁碼點
    _page_dots(draw, w, h - int(h * 0.025), page, TOTAL_PAGES)

    result = Image.alpha_composite(img.convert("RGBA"), overlay)
    return result.convert("RGB")


def _overlay_page5(img: Image.Image, quote_text: str) -> Image.Image:
    """
    第5頁：金句居中，上下裝飾線
    ╔════════════════╗
    │  (圖片)        │
    │                │
    │   ───────     │
    │   金句大字     │  居中
    │   ───────     │
    │  • • • ● •   │  頁碼點（最後一點 active）
    ╚════════════════╝
    """
    w, h = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 全圖漸層暗化底部 40%
    dark_start = int(h * 0.55)
    for i in range(h - dark_start):
        alpha = int(160 * ((i / (h - dark_start)) ** 0.7))
        draw.line([(0, dark_start + i), (w, dark_start + i)],
                  fill=(10, 10, 10, alpha))

    # 金句文字
    font_quote = _load_font(int(h * 0.052))
    lines = _wrap_text(quote_text, font_quote, int(w * 0.78))
    line_h = int(h * 0.062)
    total_text_h = len(lines) * line_h
    text_y_start = h - int(h * 0.38) - total_text_h // 2

    # 裝飾線（上）
    line_w = int(w * 0.30)
    lx = (w - line_w) // 2
    ly = text_y_start - int(h * 0.035)
    draw.line([(lx, ly), (lx + line_w, ly)], fill=LINE_COLOR, width=2)

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        lw = bbox[2] - bbox[0]
        draw.text(((w - lw) // 2, text_y_start), line, font=font_quote, fill=WHITE)
        text_y_start += line_h

    # 裝飾線（下）
    ly2 = text_y_start + int(h * 0.008)
    draw.line([(lx, ly2), (lx + line_w, ly2)], fill=LINE_COLOR, width=2)

    # 頁碼點
    _page_dots(draw, w, h - int(h * 0.025), TOTAL_PAGES, TOTAL_PAGES)

    result = Image.alpha_composite(img.convert("RGBA"), overlay)
    return result.convert("RGB")


# ─────────────────────────────────────────────────────
# 公開介面
# ─────────────────────────────────────────────────────

def apply_text_overlay(image_path: str, story_text: str, page: int,
                       title: str = None) -> None:
    """
    在已存在的圖片上疊加文字後原地儲存（覆寫 JPEG）。

    Args:
        image_path: 圖片路徑（會被覆寫）
        story_text: 這一頁的故事文字
        page:       頁碼（1-5）
        title:      故事標題（僅第1頁使用）
    """
    img = Image.open(image_path).convert("RGB")

    if page == 1:
        result = _overlay_page1(img, story_text, title or story_text)
    elif page == 5:
        result = _overlay_page5(img, story_text)
    else:
        result = _overlay_page_mid(img, story_text, page)

    result.save(image_path, "JPEG", quality=95)
    print(f"[Text] 第{page}頁文字疊加完成")
