import os
import requests
from PIL import Image
from config.prompts import CHARACTER_BASE


def _build_prompt(scene_prompt: str) -> str:
    """將場景 prompt 與固定人設合併"""
    return f"{CHARACTER_BASE} Scene: {scene_prompt}"


def generate_image_huggingface(prompt: str, output_path: str) -> bool:
    """使用 HuggingFace FLUX.1-schnell 生成圖片"""
    try:
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        print(f"[FLUX] 產圖中...")
        resp = requests.post(
            "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell",
            headers=headers,
            json={"inputs": prompt},
            timeout=120,
        )
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)
        print(f"[FLUX] 圖片已儲存：{output_path}")
        return True
    except Exception as e:
        print(f"[FLUX] 產圖失敗：{e}")
    return False


def generate_image_pollinations(prompt: str, output_path: str) -> bool:
    """備援：Pollinations.ai（免費）"""
    try:
        import urllib.parse
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&model=flux"
        print(f"[Pollinations] 備援產圖中...")
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)
        print(f"[Pollinations] 圖片已儲存：{output_path}")
        return True
    except Exception as e:
        print(f"[Pollinations] 產圖失敗：{e}")
    return False


def generate_image(scene_prompt: str, output_path: str) -> bool:
    """主要入口：帶入固定人設後產圖，FLUX → Pollinations 備援"""
    full_prompt = _build_prompt(scene_prompt)
    if generate_image_huggingface(full_prompt, output_path):
        return True
    print("[Image] FLUX 失敗，改用 Pollinations 備援...")
    return generate_image_pollinations(full_prompt, output_path)


def generate_story_images(scenes: list, output_dir: str) -> list:
    """為繪本故事的5個場景逐一產圖，回傳成功的路徑清單"""
    image_paths = []
    for scene in scenes:
        page = scene["page"]
        path = f"{output_dir}/page_{page:02d}.jpg"
        print(f"\n[Image] 產第 {page}/5 頁...")
        ok = generate_image(scene["image_prompt"], path)
        if ok:
            resize_for_instagram(path)
            image_paths.append(path)
        else:
            print(f"[Image] 第 {page} 頁失敗，跳過")
    return image_paths


def resize_for_instagram(input_path: str, output_path: str = None):
    """確保圖片符合 IG 規格（1:1，1080x1080）"""
    if output_path is None:
        output_path = input_path
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img = img.resize((1080, 1080), Image.LANCZOS)
        img.save(output_path, "JPEG", quality=95)
