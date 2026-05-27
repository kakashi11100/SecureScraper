import os
import time
import yaml
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Import your custom secure modules
from scraper.validator import is_valid_url, sanitize_selector
from scraper.hasher import calculate_hash
from scraper.storage import init_db, save_snapshot, get_stored_hash
from alerts.slack import send_slack_alert
from alerts.email_alert import send_email_alert
from scraper.tls_validator import verify_tls_health
from scraper.browser import fetch_dynamic_html

# Load environments on launch
load_dotenv()


def process_target(target: dict):
    url = target.get("url")
    selector = target.get("selector")
    label = target.get("label", "Unknown Target")
    is_dynamic = target.get("dynamic", False)  # Read the new config toggle

    # [Your existing Validation and TLS pre-flight gates stay exactly here...]
    if not is_valid_url(url): return
    if url.startswith("https://"):
        tls_ok, tls_msg = verify_tls_health(url)
        if not tls_ok: return

    clean_selector = sanitize_selector(selector)
    print(f"[*] Processing DOM Extraction: {label} ({url})")

    try:
        # 2. Dynamic vs Static routing logic
        if is_dynamic:
            print("[*] JavaScript rendering detected. Spawning headless browser session...")
            html_response = fetch_dynamic_html(url)
        else:
            headers = {'User-Agent': 'SecureScraper/1.0 (Portfolio Demonstration)'}
            response = requests.get(url, headers=headers, timeout=15)
            html_response = response.text if response.status_code == 200 else ""
        
        if not html_response:
            print(f"[!] Failed to acquire source HTML for {url}")
            return
            
        # 3. Hand off the string content directly to BeautifulSoup
        soup = BeautifulSoup(html_response, 'html.parser')
        element = soup.select(clean_selector)
        
        if not element:
            print(f"[!] Selector '{clean_selector}' not found on page.")
            return
            
        extracted_text = element[0].get_text()
        current_hash = calculate_hash(extracted_text)
        previous_hash = get_stored_hash(url)
        
        if previous_hash is None:
            print(f"[+] Initializing baseline data for {label}.")
            save_snapshot(url, current_hash, extracted_text)
        elif previous_hash != current_hash:
            print(f"[🚨] ALERT: Content variation detected on {label}!")
            save_snapshot(url, current_hash, extracted_text)
            send_slack_alert(url, label)
            send_email_alert(url, label)
        else:
            print(f"[✓] Verified: No modifications detected for {label}.")

    except Exception as e:
        print(f"[!] Runtime error processing target {url}: {e}")
    

def main():
    print("🛡️  SecureScraper Daemon Initializing...")
    init_db() # Ensure database infrastructure exists
    
    # Load configuration profiles
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        print(f"[!] Configuration mapping profile missing at {config_path}")
        return
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    targets = config.get("targets", [])
    if not targets:
        print("[!] No tracking metrics found inside config.yaml")
        return

    # Execute an analytical crawl cycle
    for target in targets:
        process_target(target)
        # Polite delay to respect target host processing capacities
        time.sleep(2)
        
    print("🏁 Execution cycle completed safely.")

if __name__ == "__main__":
    main()