import os
import requests


def send_telegram(message: str) -> bool:
    """發送 Telegram 通知"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("[Notify] Telegram 未設定，跳過通知")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }
    resp = requests.post(url, json=payload, timeout=10)
    if resp.status_code == 200:
        print("[Notify] Telegram 通知已發送")
        return True
    else:
        print(f"[Notify] Telegram 發送失敗：{resp.text}")
        return False
