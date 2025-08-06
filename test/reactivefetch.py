# reactive_fetch_and_reload.py
# Runs in background: periodically fetches new/updated runbooks and reloads into RAG

import os
import json
import time
from datetime import datetime
from subprocess import run
from simple_rag import SimpleRAGSystem  # Ensure this is importable

LAST_SYNC_FILE = "last_sync.json"
FETCH_SCRIPT = "fetch_runbooks.py"
SYNC_INTERVAL_SECS = 600  # every 10 minutes


def load_last_sync():
    if os.path.exists(LAST_SYNC_FILE):
        with open(LAST_SYNC_FILE) as f:
            return json.load(f).get("last_synced_at", "1970-01-01T00:00:00.000Z")
    return "1970-01-01T00:00:00.000Z"


def update_last_sync():
    with open(LAST_SYNC_FILE, "w") as f:
        json.dump({"last_synced_at": datetime.now().isoformat()}, f)


def run_fetch():
    print("📥 Fetching updated runbooks from Confluence...")
    result = run(["python", FETCH_SCRIPT])
    if result.returncode != 0:
        print("❌ Failed to fetch runbooks")
        return False
    print("✅ Successfully fetched runbooks")
    return True


def find_latest_json():
    json_files = [f for f in os.listdir('.') if f.startswith('runbooks_data_') and f.endswith('.json')]
    if not json_files:
        return None
    return max(json_files, key=os.path.getmtime)


def main():
    rag = SimpleRAGSystem()
    last_sync_time = load_last_sync()

    while True:
        print("\n🕒 Checking for updates...")

        # Inject last_sync_time into fetch_runbooks.py via env var or config if needed
        os.environ['LAST_SYNC_ISO'] = last_sync_time

        if run_fetch():
            update_last_sync()

            latest_file = find_latest_json()
            if latest_file:
                print(f"🔄 Reloading RAG from {latest_file}...")
                rag.load_runbooks()
                print("✅ RAG reloaded with fresh content")

        print(f"🛌 Sleeping for {SYNC_INTERVAL_SECS // 60} minutes...")
        time.sleep(SYNC_INTERVAL_SECS)


if __name__ == "__main__":
    main()
