import os
import requests
import base64
import pathlib
from PIL import Image

# 參考圖路徑（固定人設來源）
REF_IMAGE_PATH = pathlib.Path(__file__).parent.parent / "ref" / "人物參考圖.png"

# 場景描述 prompt 前綴（風格指定）
STYLE_PREFIX = (
    "Korean manhwa webtoon illustration style, clean flat color, soft shading, "
    "thin precise outlines, children picture book style, soft pastel palette, "
    "no text in image, no watermark. "
)

# 角色強化描述（無參考圖時用 prompt 補強一致性）
CHAR_DESC = (
    "Main character: Asian man (Chris) with short dark brown hair, NO glasses, "
    "wearing pink t-shirt and khaki shorts, Apple Watch on wrist. "
    "Beside him: 5-year-old Asian girl (Anna) with brown bob haircut and straight bangs, "
    "wearing light blue dress with daisy embroidery, white sandals. "
)


def _read_ref_image_b64() -> str:
    """讀取參考圖並轉為 base64"""
    return base64.b64encode(REF_IMAGE_PATH.read_bytes()).decode()


# ─────────────────────────────────────────────
# 方案 A：Novita.ai IP-Adapter（角色一致性，極低成本 ~$0.002/張）
# ─────────────────────────────────────────────
def generate_image_novita(scene_prompt: str, output_path: str) -> bool:
    """Novita.ai SDXL + IP-Adapter（角色一致性，約 $0.002/張）"""
    try:
        api_key = os.getenv("NOVITA_API_KEY")
        if not api_key:
            return False

        ref_b64 = _read_ref_image_b64()
        full_prompt = STYLE_PREFIX + CHAR_DESC + scene_prompt
        print(f"[Novita] 使用 IP-Adapter 產圖中...")

        payload = {
            "model_name": "sd_xl_base_1.0.safetensors",
            "prompt": full_prompt,
            "negative_prompt": (
                "glasses, eyewear, spectacles, ugly, deformed, blurry, "
                "bad anatomy, bad hands, extra limbs, text, watermark, signature"
            ),
            "width": 1024,
            "height": 1024,
            "image_num": 1,
            "steps": 25,
            "seed": -1,
            "clip_skip": 2,
            "guidance_scale": 7.5,
            "loras": [],
            "embeddings": [],
            "ip_adapter": [
                {
                    "model_name": "ip-adapter_sdxl.bin",
                    "image": ref_b64,
                    "strength": 0.6,
                }
            ],
        }

        resp = requests.post(
            "https://api.novita.ai/v3/async/txt2img",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        task_id = resp.json().get("task_id")
        if not task_id:
            print(f"[Novita] 無法取得 task_id：{resp.text[:200]}")
            return False

        print(f"[Novita] 任務已提交：{task_id}，等待完成...")
        return _novita_poll(task_id, output_path, api_key)

    except Exception as e:
        print(f"[Novita] 產圖失敗：{e}")
    return False


def _novita_poll(task_id: str, output_path: str, api_key: str, max_wait: int = 120) -> bool:
    """輪詢 Novita 非同步任務直到完成"""
    import time
    for _ in range(max_wait // 5):
        time.sleep(5)
        try:
            resp = requests.get(
                f"https://api.novita.ai/v3/async/task-result?task_id={task_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            data = resp.json()
            status = data.get("task", {}).get("status", "")
            if status == "TASK_STATUS_SUCCEED":
                imgs = data.get("images", [])
                if imgs:
                    img_url = imgs[0].get("image_url") or imgs[0].get("url")
                    img_resp = requests.get(img_url, timeout=60)
                    img_resp.raise_for_status()
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"[Novita] 圖片已儲存：{output_path}")
                    return True
            elif status in ("TASK_STATUS_FAILED", "TASK_STATUS_TIMEOUT"):
                print(f"[Novita] 任務失敗：{status} - {data.get('task', {}).get('reason', '')}")
                return False
        except Exception as e:
            print(f"[Novita] 輪詢錯誤：{e}")
    print("[Novita] 等待逾時")
    return False


# ─────────────────────────────────────────────
# 方案 B：fal.ai FLUX.1-Kontext（角色一致，付費）
# ─────────────────────────────────────────────
def generate_image_fal(scene_prompt: str, output_path: str) -> bool:
    """fal.ai FLUX.1-Kontext 生成（角色一致性，付費）"""
    try:
        import fal_client
        os.environ["FAL_KEY"] = os.getenv("FAL_API_KEY", "")

        ref_url = fal_client.upload_file(str(REF_IMAGE_PATH))
        print(f"[fal.ai] 參考圖已上傳，開始生成...")

        result = fal_client.subscribe(
            "fal-ai/flux-pro/kontext",
            arguments={
                "prompt": STYLE_PREFIX + scene_prompt,
                "image_url": ref_url,
                "num_images": 1,
                "image_size": "square_hd",
                "guidance_scale": 3.5,
                "num_inference_steps": 28,
                "output_format": "jpeg",
            },
        )

        img_url = result["images"][0]["url"]
        resp = requests.get(img_url, timeout=60)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)
        print(f"[fal.ai] 圖片已儲存：{output_path}")
        return True
    except Exception as e:
        print(f"[fal.ai] 產圖失敗：{e}")
    return False


# ─────────────────────────────────────────────
# 方案 C：Segmind Consistent Character（付費，需儲值）
# ─────────────────────────────────────────────
def generate_image_segmind(scene_prompt: str, output_path: str) -> bool:
    """Segmind consistent-character（需要帳號有 credits）"""
    try:
        api_key = os.getenv("SEGMIND_API_KEY")
        if not api_key:
            return False

        ref_b64 = _read_ref_image_b64()
        full_prompt = STYLE_PREFIX + scene_prompt
        print(f"[Segmind] consistent-character 產圖中...")

        resp = requests.post(
            "https://api.segmind.com/v1/consistent-character",
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            json={
                "prompt": full_prompt,
                "subject_image": ref_b64,
                "output_format": "jpg",
                "output_quality": 90,
                "negative_prompt": (
                    "glasses, eyewear, ugly, deformed, blurry, "
                    "bad anatomy, text, watermark"
                ),
            },
            timeout=120,
        )

        if resp.status_code == 200 and resp.content[:3] != b'{"':
            with open(output_path, "wb") as f:
                f.write(resp.content)
            print(f"[Segmind] 圖片已儲存：{output_path}")
            return True
        else:
            print(f"[Segmind] 產圖失敗：{resp.status_code} - {resp.text[:200]}")
    except Exception as e:
        print(f"[Segmind] 產圖失敗：{e}")
    return False


# ─────────────────────────────────────────────
# 方案 D：HuggingFace FLUX.1-schnell（免費，無角色一致性）
# ─────────────────────────────────────────────
def generate_image_huggingface(scene_prompt: str, output_path: str) -> bool:
    """HuggingFace FLUX.1-schnell（免費，強化 prompt 角色描述）"""
    try:
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        # 無參考圖時用詳細文字描述補強角色一致性
        full_prompt = STYLE_PREFIX + CHAR_DESC + scene_prompt
        print(f"[FLUX] HuggingFace 免費備援產圖中...")
        resp = requests.post(
            "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"inputs": full_prompt},
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


# ─────────────────────────────────────────────
# 主入口：依優先順序嘗試各方案
# ─────────────────────────────────────────────
def generate_image(scene_prompt: str, output_path: str) -> bool:
    """
    優先順序：
    1. Novita.ai IP-Adapter（角色一致，~$0.002/張）
    2. fal.ai FLUX Kontext（角色一致，付費）
    3. Segmind consistent-character（角色一致，需 credits）
    4. HuggingFace FLUX.1-schnell（免費，無角色一致性）
    """
    if os.getenv("NOVITA_API_KEY"):
        if generate_image_novita(scene_prompt, output_path):
            return True
        print("[Image] Novita 失敗，嘗試下一方案...")

    if os.getenv("FAL_API_KEY"):
        if generate_image_fal(scene_prompt, output_path):
            return True
        print("[Image] fal.ai 失敗，嘗試下一方案...")

    if os.getenv("SEGMIND_API_KEY"):
        if generate_image_segmind(scene_prompt, output_path):
            return True
        print("[Image] Segmind 失敗，改用免費備援...")

    return generate_image_huggingface(scene_prompt, output_path)


def generate_story_images(scenes: list, output_dir: str) -> list:
    """為繪本故事的 5 個場景逐一產圖"""
    image_paths = []
    for scene in scenes:
        page = scene["page"]
        path = f"{output_dir}/page_{page:02d}.jpg"
        print(f"\n[Image] 產第 {page}/5 頁...")
        if generate_image(scene["image_prompt"], path):
            resize_for_instagram(path)
            image_paths.append(path)
        else:
            print(f"[Image] 第 {page} 頁失敗，跳過")
    return image_paths


def resize_for_instagram(input_path: str, output_path: str = None):
    """調整為 IG 規格（1080x1080）"""
    if output_path is None:
        output_path = input_path
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img = img.resize((1080, 1080), Image.LANCZOS)
        img.save(output_path, "JPEG", quality=95)
