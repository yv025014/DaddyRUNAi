import os
import base64
import requests
from PIL import Image
from google import genai
from google.genai import types


def generate_image_gemini(prompt: str, output_path: str) -> bool:
    """使用 Gemini Imagen 4 生成圖片"""
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
            ),
        )
        if response.generated_images:
            img_bytes = response.generated_images[0].image.image_bytes
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            print(f"[Gemini] 圖片已儲存：{output_path}")
            return True
    except Exception as e:
        print(f"[Gemini] 產圖失敗：{e}")
    return False


def generate_image_nvidia(prompt: str, output_path: str) -> bool:
    """使用 NVIDIA NIM (SDXL) 生成圖片（備援）"""
    try:
        api_key = os.getenv("NVIDIA_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "text_prompts": [{"text": prompt, "weight": 1}],
            "cfg_scale": 7,
            "sampler": "K_DPM_2_ANCESTRAL",
            "seed": 0,
            "steps": 25,
            "width": 1024,
            "height": 1024,
        }
        resp = requests.post(
            "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-xl",
            headers=headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        b64 = data["artifacts"][0]["base64"]
        img_bytes = base64.b64decode(b64)
        with open(output_path, "wb") as f:
            f.write(img_bytes)
        print(f"[NVIDIA] 圖片已儲存：{output_path}")
        return True
    except Exception as e:
        print(f"[NVIDIA] 產圖失敗：{e}")
    return False


def generate_image_pollinations(prompt: str, output_path: str) -> bool:
    """使用 Pollinations.ai 生成圖片（完全免費，無需 API Key）"""
    try:
        import urllib.parse
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&model=flux"
        print(f"[Pollinations] 產圖中...")
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)
        print(f"[Pollinations] 圖片已儲存：{output_path}")
        return True
    except Exception as e:
        print(f"[Pollinations] 產圖失敗：{e}")
    return False


def generate_image(prompt: str, output_path: str) -> bool:
    """主要入口：Pollinations（免費）→ NVIDIA（備援）"""
    if generate_image_pollinations(prompt, output_path):
        return True
    print("[Image] Pollinations 失敗，改用 NVIDIA 備援...")
    return generate_image_nvidia(prompt, output_path)


def resize_for_instagram(input_path: str, output_path: str = None):
    """確保圖片符合 IG 規格（1:1，1080x1080）"""
    if output_path is None:
        output_path = input_path
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img = img.resize((1080, 1080), Image.LANCZOS)
        img.save(output_path, "JPEG", quality=95)
    print(f"[Image] 已調整為 IG 規格：{output_path}")
