import os
import requests


def send_telegram(message: str) -> bool:
    """發送 Discord 通知（函式名保留相容性）"""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("[Notify] DISCORD_WEBHOOK_URL 未設定，跳過通知")
        return False

    # Markdown 轉換：*text* → **text**（Discord 用雙星號粗體）
    content = message.replace("*", "**")

    payload = {"content": content}
    resp = requests.post(webhook_url, json=payload, timeout=10)

    if resp.status_code in (200, 204):
        print("[Notify] Discord 通知已發送")
        return True
    else:
        print(f"[Notify] Discord 發送失敗：{resp.text}")
        return False
