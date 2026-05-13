"""
工具：從角色三視圖自動裁切臉部/全身 crops
用法：python tools/generate_ref_crops.py

如果換了新的三視圖，重新執行即可更新所有 crops。
適用圖片尺寸：1402 x 1122（預設），其他尺寸按比例自動計算。
"""
from PIL import Image
import pathlib

REF_DIR = pathlib.Path(__file__).parent.parent / "ref"
SRC = REF_DIR / "人物參考圖.png"


def generate_crops(src: pathlib.Path = SRC):
    if not src.exists():
        print(f"[Error] 找不到：{src}")
        return False

    img = Image.open(src)
    w, h = img.size
    print(f"三視圖尺寸：{w} x {h}")

    # ─ 座標計算（相對比例，適配不同解析度）────────
    # 假設版面：左側標籤欄 ~7%，三欄正面/側面/背面各 ~31%
    # Chris 上半行，Anna 下半行

    # Chris 正面全身
    x0 = int(w * 0.07)
    x1 = int(w * 0.38)
    y0 = 0
    y1 = int(h * 0.50)
    chris_front = img.crop((x0, y0, x1, y1))
    chris_front.save(str(REF_DIR / "chris_front.png"))
    print(f"  chris_front: {chris_front.size}")

    # Chris 臉部特寫（頭肩部，正面 x 範圍的中心偏右上方）
    cf_x0 = int(w * 0.19)
    cf_y0 = int(h * 0.06)
    cf_x1 = int(w * 0.33)
    cf_y1 = int(h * 0.21)
    chris_face = img.crop((cf_x0, cf_y0, cf_x1, cf_y1))
    chris_face.resize((512, 512), Image.LANCZOS).save(str(REF_DIR / "chris_face_crop.png"))
    print(f"  chris_face_crop: 512x512 (from {chris_face.size})")

    # Anna 正面全身
    anna_front = img.crop((x0, int(h * 0.50), x1, h))
    anna_front.save(str(REF_DIR / "anna_front.png"))
    print(f"  anna_front: {anna_front.size}")

    # Anna 臉部特寫
    af_x0 = int(w * 0.19)
    af_y0 = int(h * 0.59)
    af_x1 = int(w * 0.33)
    af_y1 = int(h * 0.76)
    anna_face = img.crop((af_x0, af_y0, af_x1, af_y1))
    anna_face.resize((512, 512), Image.LANCZOS).save(str(REF_DIR / "anna_face_crop.png"))
    print(f"  anna_face_crop: 512x512 (from {anna_face.size})")

    print("\n✅ 裁切完成：")
    for f in ["chris_front.png", "chris_face_crop.png", "anna_front.png", "anna_face_crop.png"]:
        p = REF_DIR / f
        if p.exists():
            print(f"   {p}")
    return True


if __name__ == "__main__":
    generate_crops()
