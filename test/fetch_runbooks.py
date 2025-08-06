import requests
import json
from datetime import datetime
from requests.auth import HTTPBasicAuth
from config import CONFLUENCE_BASE_URL, EMAIL, API_TOKEN, SPACE_KEY

def fetch_all_pages_in_space(space_key):
    base_url = f"{CONFLUENCE_BASE_URL}/rest/api/content/search"
    headers = {"Accept": "application/json"}
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)

    limit = 50
    start = 0
    all_results = []

    cql_query = f"space = {space_key} AND type = page"

    print(f"Requesting all pages in space '{space_key}' with CQL: {cql_query}")

    while True:
        params = {
            "cql": cql_query,
            "limit": limit,
            "start": start,
            "expand": "body.storage,version,metadata.labels,space,ancestors"
        }

        print(f"\n🔄 Fetching pages... start={start}")
        response = requests.get(base_url, headers=headers, params=params, auth=auth)

        print(f"Response Status: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ Failed to fetch content: {response.status_code} - {response.text}")
            break

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            print(f"Raw response content: {response.text}")
            break

        results = data.get("results", [])
        if not results:
            print("✅ No more results, finished pagination.")
            break

        all_results.extend(results)
        print(f"✅ Fetched {len(results)} pages (Total so far: {len(all_results)})")

        if len(results) < 14390:
            break  # No more pages

        start += limit

    print(f"\n🎯 Total pages fetched in space '{space_key}': {len(all_results)}")
    return all_results

def filter_runbooks(pages):
    runbooks = []
    for page in pages:
        title = page.get("title", "").lower()
        labels = []
        metadata_labels = page.get("metadata", {}).get("labels", {})
        if metadata_labels and "results" in metadata_labels:
            labels = [label.get("name", "").lower() for label in metadata_labels["results"]]

        # Filter if "runbook" is in title or any label
        if "runbook" in title or any("runbook" in label for label in labels):
            runbooks.append(page)

    print(f"\n🎯 Total filtered runbooks found: {len(runbooks)}")
    return runbooks

def process_and_save(runbooks, space_key):
    runbooks_data = {
        "metadata": {
            "fetched_at": datetime.now().isoformat(),
            "confluence_base_url": CONFLUENCE_BASE_URL,
            "space_key": space_key,
            "total_pages_fetched": len(runbooks)
        },
        "runbooks": []
    }

    for page in runbooks:
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

        runbooks_data["runbooks"].append(runbook_entry)
        print(f"✅ Processed: {title} (ID: {page_id})")

    output_filename = f"runbooks_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(runbooks_data, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Saved {len(runbooks_data['runbooks'])} runbooks to: {output_filename}")
        print(f"📊 Total words: {sum(rb['content']['word_count'] for rb in runbooks_data['runbooks'])}")

        print(f"\n📋 Summary:")
        for rb in runbooks_data["runbooks"]:
            print(f"  • {rb['title']} ({rb['content']['word_count']} words)")

    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")

def main():
    pages = fetch_all_pages_in_space(SPACE_KEY)
    runbooks = filter_runbooks(pages)
    process_and_save(runbooks, SPACE_KEY)

if __name__ == "__main__":
    main()
