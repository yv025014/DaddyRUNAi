import os
import time
import requests


BASE_URL = "https://graph.instagram.com/v19.0"


def _get_credentials():
    return os.getenv("IG_USER_ID"), os.getenv("IG_ACCESS_TOKEN")


def create_media_container(image_url: str, caption: str) -> str | None:
    """建立單張 IG media container，回傳 container_id"""
    user_id, token = _get_credentials()
    url = f"{BASE_URL}/{user_id}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": token,
    }
    resp = requests.post(url, data=payload, timeout=30)
    data = resp.json()

    if "id" in data:
        container_id = data["id"]
        print(f"[IG] Container 建立成功：{container_id}")
        return container_id
    else:
        print(f"[IG] Container 建立失敗：{data}")
        return None


def create_carousel_item(image_url: str) -> str | None:
    """建立輪播子項目 container（is_carousel_item=true）"""
    user_id, token = _get_credentials()
    url = f"{BASE_URL}/{user_id}/media"
    payload = {
        "image_url": image_url,
        "is_carousel_item": "true",
        "access_token": token,
    }
    resp = requests.post(url, data=payload, timeout=30)
    data = resp.json()
    if "id" in data:
        print(f"[IG] 輪播子項目建立：{data['id']}")
        return data["id"]
    else:
        print(f"[IG] 輪播子項目失敗：{data}")
        return None


def create_carousel_container(children_ids: list, caption: str) -> str | None:
    """建立輪播主 container"""
    user_id, token = _get_credentials()
    url = f"{BASE_URL}/{user_id}/media"
    payload = {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption,
        "access_token": token,
    }
    resp = requests.post(url, data=payload, timeout=30)
    data = resp.json()
    if "id" in data:
        print(f"[IG] 輪播 Container 建立成功：{data['id']}")
        return data["id"]
    else:
        print(f"[IG] 輪播 Container 失敗：{data}")
        return None


def post_carousel_to_instagram(image_urls: list, caption: str) -> str | None:
    """發布輪播貼文：建立子項目 → 建立輪播容器 → 等待 → 發布"""
    # 1. 建立每張圖的子項目
    children_ids = []
    for i, url in enumerate(image_urls):
        print(f"[IG] 上傳第 {i+1}/{len(image_urls)} 張...")
        cid = create_carousel_item(url)
        if cid:
            children_ids.append(cid)
        time.sleep(1)

    if len(children_ids) < 2:
        print(f"[IG] 子項目不足（{len(children_ids)}），無法建立輪播")
        return None

    # 2. 建立輪播容器
    container_id = create_carousel_container(children_ids, caption)
    if not container_id:
        return None

    # 3. 等待處理
    if not wait_for_container(container_id):
        return None

    # 4. 發布
    return publish_media(container_id)


def wait_for_container(container_id: str, max_wait: int = 60) -> bool:
    """等待 container 處理完成"""
    _, token = _get_credentials()
    url = f"{BASE_URL}/{container_id}"
    params = {"fields": "status_code", "access_token": token}

    for i in range(max_wait // 5):
        resp = requests.get(url, params=params, timeout=10)
        status = resp.json().get("status_code", "")
        print(f"[IG] Container 狀態：{status}（{i*5}s）")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            print("[IG] Container 處理錯誤")
            return False
        time.sleep(5)

    print("[IG] Container 等待逾時")
    return False


def publish_media(container_id: str) -> str | None:
    """發布已就緒的 container，回傳 media_id"""
    user_id, token = _get_credentials()
    url = f"{BASE_URL}/{user_id}/media_publish"
    payload = {
        "creation_id": container_id,
        "access_token": token,
    }
    resp = requests.post(url, data=payload, timeout=30)
    data = resp.json()

    if "id" in data:
        media_id = data["id"]
        print(f"[IG] 發布成功！Media ID：{media_id}")
        return media_id
    else:
        print(f"[IG] 發布失敗：{data}")
        return None


def post_to_instagram(image_url: str, caption: str) -> str | None:
    """完整發布流程：建立 container → 等待 → 發布"""
    container_id = create_media_container(image_url, caption)
    if not container_id:
        return None

    if not wait_for_container(container_id):
        return None

    return publish_media(container_id)


def get_post_insights(media_id: str) -> dict:
    """取得貼文 Insights 數據"""
    _, token = _get_credentials()
    url = f"{BASE_URL}/{media_id}/insights"
    params = {
        "metric": "impressions,reach,likes,comments,saves,shares",
        "access_token": token,
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()

    insights = {}
    for item in data.get("data", []):
        insights[item["name"]] = item["values"][0]["value"] if item.get("values") else 0

    return insights


def get_recent_posts(limit: int = 7) -> list:
    """取得最近幾篇貼文的 ID 與時間"""
    user_id, token = _get_credentials()
    url = f"{BASE_URL}/{user_id}/media"
    params = {
        "fields": "id,timestamp,caption",
        "limit": limit,
        "access_token": token,
    }
    resp = requests.get(url, params=params, timeout=10)
    return resp.json().get("data", [])


def refresh_token() -> str | None:
    """刷新 Long-lived Token（每 50 天呼叫一次）"""
    _, token = _get_credentials()
    url = "https://graph.instagram.com/refresh_access_token"
    params = {
        "grant_type": "ig_refresh_token",
        "access_token": token,
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    new_token = data.get("access_token")
    if new_token:
        print(f"[IG] Token 刷新成功，有效期：{data.get('expires_in')} 秒")
    return new_token
