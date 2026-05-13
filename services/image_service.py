"""
圖片生成服務 - 優先順序：
1. InstantID (HF Space, 免費, 人臉一致性)
2. Novita.ai IP-Adapter (付費 ~$0.002/張, 角色一致)
3. fal.ai FLUX Kontext (付費, 角色一致)
4. Segmind consistent-character (需 credits)
5. HuggingFace FLUX.1-schnell (免費, 純文字)
"""

import os
import requests
import base64
import pathlib
import shutil
from PIL import Image

# ── 路徑設定 ──────────────────────────────────────
REF_DIR        = pathlib.Path(__file__).parent.parent / "ref"
REF_IMAGE_PATH = REF_DIR / "人物參考圖.png"
CHRIS_FACE     = REF_DIR / "chris_face_crop.png"
CHRIS_FRONT    = REF_DIR / "chris_front.png"

# ── 風格前綴（對齊參考圖質感：圖畫書水彩線稿，非遊戲 CG）──
STYLE_PREFIX = (
    "Warm picture book illustration, Korean webtoon line art style, "
    "soft watercolor shading, gentle hand-drawn quality, "
    "warm pastel color palette, simple clean backgrounds, "
    "soft natural lighting, flat perspective, "
    "no 3D rendering, no game art, no shiny highlights, no cel shading, "
    "no text, no watermark, no logo. "
)

# ── 角色文字描述（純文字備援用）────────────────────
CHAR_DESC = (
    "Main character: Asian man (Chris/把拔) with short dark brown hair, NO glasses, "
    "wearing pink t-shirt and khaki shorts, Apple Watch on wrist. "
    "Beside him: 5-year-old Asian girl (Anna) with brown bob haircut and straight bangs, "
    "wearing light blue dress with daisy embroidery, white sandals. "
)

# ── 固定角色服裝的強化 prompt ─────────────────────
OUTFIT_ENFORCE = (
    "Chris wearing pink t-shirt and khaki shorts, Apple Watch. "
    "Anna wearing light blue dress with daisy embroidery, white sandals. "
)


def _read_ref_image_b64(path: pathlib.Path = REF_IMAGE_PATH) -> str:
    """讀取圖片並轉為 base64"""
    return base64.b64encode(path.read_bytes()).decode()


def _ensure_crops():
    """確保臉部裁切圖已存在，否則自動生成"""
    if CHRIS_FACE.exists() and CHRIS_FRONT.exists():
        return True
    if not REF_IMAGE_PATH.exists():
        print("[Image] 找不到參考圖：ref/人物參考圖.png")
        return False
    try:
        img = Image.open(REF_IMAGE_PATH)
        w, h = img.size  # 預期 ~1402 x 1122

        # Chris 正面全身（左 1/3，上 1/2）
        chris_front = img.crop((100, 0, 520, 560))
        chris_front.save(str(CHRIS_FRONT))

        # Chris 臉部特寫（正面頭肩部）
        chris_face = img.crop((265, 65, 460, 240))
        chris_face.resize((512, 512), Image.LANCZOS).save(str(CHRIS_FACE))

        print(f"[Image] 臉部裁切完成：{CHRIS_FACE}")
        return True
    except Exception as e:
        print(f"[Image] 自動裁切失敗：{e}")
        return False


# ─────────────────────────────────────────────────
# 方案 A：InstantID via HF Space（免費，~15s/張）
# ─────────────────────────────────────────────────
def generate_image_instantid(scene_prompt: str, output_path: str) -> bool:
    """
    InstantX/InstantID HF Space（完全免費）
    - 臉部裁切 → ID 鎖定 Chris 的臉
    - 全身圖 → pose 參考
    - prompt → 場景 + Anna 描述
    """
    try:
        from gradio_client import Client, handle_file

        if not _ensure_crops():
            return False

        full_prompt = STYLE_PREFIX + OUTFIT_ENFORCE + scene_prompt

        print("[InstantID] 連接 HF Space...")
        c = Client("InstantX/InstantID", verbose=False)

        result = c.predict(
            face_image_path=handle_file(str(CHRIS_FACE)),   # 鎖定 Chris 臉部 ID
            pose_image_path=handle_file(str(CHRIS_FRONT)),  # 全身 pose 比例
            prompt=full_prompt,
            negative_prompt=(
                "glasses, eyewear, spectacles, realistic photo, ugly, deformed, "
                "blurry, bad anatomy, extra limbs, text, watermark, logo, "
                "3d render, signature"
            ),
            style_name="(No style)",
            num_steps=25,
            identitynet_strength_ratio=0.85,
            adapter_strength_ratio=0.80,
            canny_strength=0.3,
            depth_strength=0.4,
            controlnet_selection=["depth"],
            guidance_scale=5.5,
            seed=-1,              # 每張隨機
            scheduler="EulerDiscreteScheduler",
            enable_lcm=False,
            enhance_face_region=True,
            api_name="/generate_image",
        )

        out_tmp = result[0]
        shutil.copy(out_tmp, output_path)
        print(f"[InstantID] 圖片已儲存：{output_path}")
        return True

    except Exception as e:
        print(f"[InstantID] 失敗：{e}")
    return False


# ─────────────────────────────────────────────────
# 方案 B：Novita.ai IP-Adapter（~$0.002/張）
# ─────────────────────────────────────────────────
def generate_image_novita(scene_prompt: str, output_path: str) -> bool:
    """Novita.ai SDXL + IP-Adapter（角色一致性，約 $0.002/張）"""
    try:
        api_key = os.getenv("NOVITA_API_KEY")
        if not api_key:
            return False

        ref_b64 = _read_ref_image_b64()
        full_prompt = STYLE_PREFIX + CHAR_DESC + scene_prompt
        print("[Novita] 使用 IP-Adapter 產圖中...")

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
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        task_id = resp.json().get("task_id")
        if not task_id:
            print(f"[Novita] 無法取得 task_id：{resp.text[:200]}")
            return False

        print(f"[Novita] 任務已提交：{task_id}")
        return _novita_poll(task_id, output_path, api_key)

    except Exception as e:
        print(f"[Novita] 產圖失敗：{e}")
    return False


def _novita_poll(task_id: str, output_path: str, api_key: str, max_wait: int = 120) -> bool:
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
                print(f"[Novita] 任務失敗：{status}")
                return False
        except Exception as e:
            print(f"[Novita] 輪詢錯誤：{e}")
    print("[Novita] 等待逾時")
    return False


# ─────────────────────────────────────────────────
# 方案 C：fal.ai FLUX Kontext（付費）
# ─────────────────────────────────────────────────
def generate_image_fal(scene_prompt: str, output_path: str) -> bool:
    try:
        import fal_client
        os.environ["FAL_KEY"] = os.getenv("FAL_API_KEY", "")

        ref_url = fal_client.upload_file(str(REF_IMAGE_PATH))
        print("[fal.ai] 參考圖已上傳，開始生成...")

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


# ─────────────────────────────────────────────────
# 方案 D：Segmind consistent-character（需 credits）
# ─────────────────────────────────────────────────
def generate_image_segmind(scene_prompt: str, output_path: str) -> bool:
    try:
        api_key = os.getenv("SEGMIND_API_KEY")
        if not api_key:
            return False

        ref_b64 = _read_ref_image_b64()
        print("[Segmind] consistent-character 產圖中...")

        resp = requests.post(
            "https://api.segmind.com/v1/consistent-character",
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            json={
                "prompt": STYLE_PREFIX + scene_prompt,
                "subject_image": ref_b64,
                "output_format": "jpg",
                "output_quality": 90,
                "negative_prompt": "glasses, eyewear, ugly, deformed, blurry, text, watermark",
            },
            timeout=120,
        )

        if resp.status_code == 200 and not resp.content.startswith(b'{"'):
            with open(output_path, "wb") as f:
                f.write(resp.content)
            print(f"[Segmind] 圖片已儲存：{output_path}")
            return True
        else:
            print(f"[Segmind] 失敗：{resp.status_code} - {resp.text[:200]}")
    except Exception as e:
        print(f"[Segmind] 失敗：{e}")
    return False


# ─────────────────────────────────────────────────
# 方案 E：HuggingFace FLUX.1-schnell（免費，純文字）
# ─────────────────────────────────────────────────
def generate_image_huggingface(scene_prompt: str, output_path: str) -> bool:
    try:
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        full_prompt = STYLE_PREFIX + CHAR_DESC + OUTFIT_ENFORCE + scene_prompt
        print("[FLUX] HuggingFace 備援產圖中...")
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
        print(f"[FLUX] 失敗：{e}")
    return False


# ─────────────────────────────────────────────────
# 主入口：依優先順序嘗試各方案
# ─────────────────────────────────────────────────
def generate_image(scene_prompt: str, output_path: str) -> bool:
    """
    優先順序：
    1. InstantID（免費，臉部一致，HF Space）
    2. Novita.ai IP-Adapter（$0.002/張）
    3. fal.ai FLUX Kontext（付費）
    4. Segmind（需 credits）
    5. HuggingFace FLUX.1-schnell（免費，純文字）
    """
    # 1. InstantID（免費首選）
    if REF_IMAGE_PATH.exists():
        if generate_image_instantid(scene_prompt, output_path):
            return True
        print("[Image] InstantID 失敗，嘗試下一方案...")

    # 2. Novita.ai
    if os.getenv("NOVITA_API_KEY"):
        if generate_image_novita(scene_prompt, output_path):
            return True
        print("[Image] Novita 失敗，嘗試下一方案...")

    # 3. fal.ai
    if os.getenv("FAL_API_KEY"):
        if generate_image_fal(scene_prompt, output_path):
            return True
        print("[Image] fal.ai 失敗，嘗試下一方案...")

    # 4. Segmind
    if os.getenv("SEGMIND_API_KEY"):
        if generate_image_segmind(scene_prompt, output_path):
            return True
        print("[Image] Segmind 失敗，改用 HF 備援...")

    # 5. HuggingFace FLUX（最終備援）
    return generate_image_huggingface(scene_prompt, output_path)


def generate_story_images(scenes: list, output_dir: str,
                          story_title: str = "") -> list:
    """為繪本故事的 5 個場景逐一產圖，並疊加文字"""
    from services.text_overlay_service import apply_text_overlay

    image_paths = []
    for scene in scenes:
        page        = scene["page"]
        story_text  = scene.get("story_text", "")
        path        = f"{output_dir}/page_{page:02d}.jpg"

        print(f"\n[Image] 產第 {page}/5 頁...")
        if generate_image(scene["image_prompt"], path):
            resize_for_instagram(path)
            # 疊加文字（圓體排版）
            apply_text_overlay(
                image_path=path,
                story_text=story_text,
                page=page,
                title=story_title if page == 1 else None,
            )
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
