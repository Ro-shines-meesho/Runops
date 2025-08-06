import requests
import json
from datetime import datetime
from requests.auth import HTTPBasicAuth
from config import CONFLUENCE_BASE_URL, EMAIL, API_TOKEN

PARENT_PAGE_ID = "2678227022"
OUTPUT_FILE = "devops_runbooks.json"

auth = HTTPBasicAuth(EMAIL, API_TOKEN)
headers = {"Accept": "application/json"}

def fetch_child_pages(parent_id):
    all_pages = []
    start = 0
    limit = 50

    print(f"📂 Fetching child pages of parent ID: {parent_id}...")

    while True:
        url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content/{parent_id}/child/page"
        params = {
            "limit": limit,
            "start": start,
            "expand": "body.storage,version,metadata.labels,space"
        }

        response = requests.get(url, headers=headers, auth=auth, params=params)
        if response.status_code != 200:
            print(f"❌ Error fetching children: {response.status_code} - {response.text}")
            break

        data = response.json()
        results = data.get("results", [])
        if not results:
            break

        for page in results:
            content = page.get("body", {}).get("storage", {}).get("value", "")
            word_count = len(content.split()) if content else 0

            labels = []
            metadata_labels = page.get("metadata", {}).get("labels", {}).get("results", [])
            if metadata_labels:
                labels = [lbl.get("name", "") for lbl in metadata_labels]

            page_data = {
                "id": page.get("id", ""),
                "title": page.get("title", ""),
                "type": page.get("type", ""),
                "status": page.get("status", ""),
                "url": f"{CONFLUENCE_BASE_URL}/wiki{page.get('_links', {}).get('webui', '')}",
                "created": page.get("version", {}).get("when", ""),
                "author": page.get("version", {}).get("by", {}).get("displayName", ""),
                "labels": labels,
                "space": page.get("space", {}).get("key", ""),
                "content": content,
                "word_count": word_count,
                "is_runbook": True
            }

            all_pages.append(page_data)

        print(f"✅ Fetched {len(results)} child pages (start={start})")

        if len(results) < limit:
            break

        start += limit

    return all_pages

def load_existing_data():
    try:
        with open(OUTPUT_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "metadata": {},
            "runbooks": []
        }

def save_combined_data(existing_data, new_pages):
    existing_ids = {rb['id'] for rb in existing_data['runbooks']}
    new_unique_pages = [p for p in new_pages if p['id'] not in existing_ids]

    if not new_unique_pages:
        print("✅ No new runbooks to add.")
        return

    existing_data['runbooks'].extend(new_unique_pages)
    existing_data['metadata'] = {
        "last_fetched": datetime.now().isoformat(),
        "total_runbooks": len(existing_data['runbooks']),
        "source": f"{CONFLUENCE_BASE_URL}/wiki/spaces/DEVOPS/pages/{PARENT_PAGE_ID}/DevOps+RunBooks"
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    print(f"📁 Appended {len(new_unique_pages)} new runbooks to {OUTPUT_FILE}")

    print("\n📋 Summary:")
    for rb in new_unique_pages:
        print(f"  • {rb['title']} ({rb['word_count']} words)")

def main():
    print("🚀 STARTING RUNBOOK FETCH FROM PARENT PAGE")
    pages = fetch_child_pages(PARENT_PAGE_ID)
    existing = load_existing_data()
    save_combined_data(existing, pages)

if __name__ == "__main__":
    main()
