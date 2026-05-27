import os
import requests
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

def send_slack_alert(url: str, label: str) -> bool:
    """
    Dispatches a JSON payload payload to a configured Slack incoming webhook channel.
    Retrieves the target webhook from the environment variables securely.
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url or "YOUR/WEBHOOK/URL" in webhook_url:
        print("[!] Slack Alert skipped: Webhook URL not configured.")
        return False

    # Structure a clean notification block
    payload = {
        "text": f"*SecureScraper Alert* \nContent modification detected on monitored target!\n*Label:* {label}\n*URL:* {url}"
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"[!] Failed to dispatch Slack alert: {e}")
        return False