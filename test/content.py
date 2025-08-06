import requests
import json
import os
from datetime import datetime
from requests.auth import HTTPBasicAuth
from config import CONFLUENCE_BASE_URL, EMAIL, API_TOKEN, SPACE_KEY

FILENAME = "runbooks_data.json"

def load_existing_runbooks():
    if not os.path.exists(FILENAME):
        print(f"🆕 No existing file found, starting fresh.")
        return []
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            data = json.load(f)
            runbooks = data.get("runbooks", [])
            print(f"📂 Loaded {len(runbooks)} existing runbooks from {FILENAME}")
            return runbooks
    except Exception as e:
        print(f"❌ Error loading existing runbooks: {e}")
        return []

def save_runbooks(runbooks):
    data = {
        "metadata": {
            "saved_at": datetime.now().isoformat(),
            "total_runbooks": len(runbooks),
            "confluence_base_url": CONFLUENCE_BASE_URL,
            "space_key": SPACE_KEY
        },
        "runbooks": runbooks
    }
    try:
        with open(FILENAME, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(runbooks)} runbooks to {FILENAME}")
    except Exception as e:
        print(f"❌ Error saving runbooks: {e}")

def fetch_all_pages(space_key):
    base_url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/search"
    headers = {"Accept": "application/json"}
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)

    limit = 50
    start = 0
    all_pages = []
    fetched_ids = set()

    cql_query = f"space = {space_key} AND type = page"

    print(f"🔍 Fetching pages from space '{space_key}' with CQL: {cql_query}")

    while True:
        params = {
            "cql": cql_query,
            "limit": limit,
            "start": start,
            "expand": "body.storage,version,metadata.labels,space,ancestors"
        }

        print(f"⏳ Fetching pages... start={start}")
        response = requests.get(base_url, headers=headers, params=params, auth=auth)
        print(f"📡 Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Failed to fetch pages: {response.status_code} {response.text}")
            break

        try:
            data = response.json()
        except Exception as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Response text: {response.text}")
            break

        results = data.get("results", [])
        if not results:
            print("✅ No more pages to fetch, stopping.")
            break

        # Filter out any duplicate IDs in this batch
        new_results = []
        for page in results:
            page_id = page.get("id")
            if page_id not in fetched_ids:
                fetched_ids.add(page_id)
                new_results.append(page)
            else:
                print(f"⚠️ Duplicate page id {page_id} ignored in fetch")

        if not new_results:
            print("✅ No new unique pages found in this batch, stopping.")
            break

        all_pages.extend(new_results)
        print(f"✅ Fetched {len(new_results)} new unique pages (total so far: {len(all_pages)})")

        # Stop if fetched less than limit (means last page)
        if len(results) < limit:
            break

        start += limit

    print(f"🎯 Total unique pages fetched: {len(all_pages)}")
    return all_pages

def filter_runbooks(pages):
    runbooks = []
    seen_ids = set()
    for page in pages:
        page_id = page.get("id")
        if page_id in seen_ids:
            continue
        seen_ids.add(page_id)

        title = page.get("title", "").lower()
        labels = []
        metadata_labels = page.get("metadata", {}).get("labels", {})
        if metadata_labels and "results" in metadata_labels:
            labels = [label.get("name", "").lower() for label in metadata_labels["results"]]

        if "runbook" in title or any("runbook" in label for label in labels):
            runbooks.append(page)

    print(f"🎯 Filtered runbooks count: {len(runbooks)}")
    return runbooks

def process_runbooks(pages):
    processed = []
    for page in pages:
        title = page.get("title", "")
        page_id = page.get("id", "")
        page_type = page.get("type", "")

        body_storage = page.get("body", {}).get("storage", {})
        content = body_storage.get("value", "") if body_storage else ""
        content_representation = body_storage.get("representation", "") if body_storage else ""

        version_info = page.get("version", {})
        version_number = version_info.get("number", 0)
        version_when = version_info.get("when", "")
        version_by = version_info.get("by", {}).get("displayName", "") if version_info.get("by") else ""

        space_info = page.get("space", {})
        space_key_page = space_info.get("key", "") if space_info else ""
        space_name = space_info.get("name", "") if space_info else ""

        labels = []
        metadata_labels = page.get("metadata", {}).get("labels", {})
        if metadata_labels and "results" in metadata_labels:
            labels = [label.get("name", "") for label in metadata_labels["results"]]

        page_url = f"{CONFLUENCE_BASE_URL}/wiki/spaces/{space_key_page}/pages/{page_id}"

        runbook_entry = {
            "id": page_id,
            "title": title,
            "type": page_type,
            "url": page_url,
            "space": {
                "key": space_key_page,
                "name": space_name
            },
            "content": {
                "body": content,
                "representation": content_representation,
                "word_count": len(content.split()) if content else 0
            },
            "version": {
                "number": version_number,
                "when": version_when,
                "by": version_by
            },
            "labels": labels
        }

        processed.append(runbook_entry)
        print(f"✅ Processed runbook: {title} (ID: {page_id})")

    return processed

def main():
    # Load existing runbooks and IDs
    existing_runbooks = load_existing_runbooks()
    existing_ids = {rb["id"] for rb in existing_runbooks}

    # Fetch all pages from Confluence
    all_pages = fetch_all_pages(SPACE_KEY)

    # Filter pages for runbooks only
    runbook_pages = filter_runbooks(all_pages)

    # Process runbooks to structured form
    new_runbooks = process_runbooks(runbook_pages)

    # Filter only new unique runbooks by ID (exclude already saved)
    unique_new = [rb for rb in new_runbooks if rb["id"] not in existing_ids]

    print(f"➕ Adding {len(unique_new)} new unique runbooks to existing {len(existing_runbooks)}")

    combined = existing_runbooks + unique_new

    # Save combined runbooks back to file
    save_runbooks(combined)

if __name__ == "__main__":
    main()
