import os
import cloudinary
import cloudinary.uploader


def upload_image(local_path: str, public_id: str) -> str:
    """上傳圖片至 Cloudinary，回傳公開 URL"""
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    )

    result = cloudinary.uploader.upload(
        local_path,
        public_id=public_id,
        overwrite=True,
        resource_type="image",
        format="jpg",
    )

    url = result.get("secure_url")
    print(f"[Cloudinary] 上傳成功：{url}")
    return url
