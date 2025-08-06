import json
import re
from collections import defaultdict
from intelligent_runbook_creator import IntelligentRunbookCreator

# === Load Data ===
with open("dev-ops-buddy.Messages_replies.json") as f:
    messages_data = json.load(f)

with open("runbooks_data_20250606_123950.json") as f:
    runbooks_data = json.load(f)

# === Clean Utility ===
def clean_text(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text.lower()).strip()

def extract_query_from_message(msg_entry) -> str:
    parent = msg_entry.get("parent_msg", "")
    replies = msg_entry.get("replies", [])
    reply_texts = [reply.get("message", "") for reply in replies if isinstance(reply, dict)]
    return (parent + " " + " ".join(reply_texts)).strip()


# === Initialize ===
creator = IntelligentRunbookCreator()
runbook_titles = [clean_text(rb["title"]) for rb in runbooks_data["runbooks"]]

stats = {
    "summary": {
        "total_messages": 0,
        "covered_by_runbook": 0,
        "missing_runbooks": 0
    },
    "by_category": defaultdict(lambda: {"total": 0, "covered": 0, "missing": 0}),
    "missing_runbooks": []
}

# === Main Loop ===
for msg in messages_data:
    query = extract_query_from_message(msg)
    if not query:
        continue

    stats["summary"]["total_messages"] += 1

    analysis = creator.analyze_query(query)
    category = analysis["primary_category"]
    matched_keywords = analysis["matched_keywords"]

    stats["by_category"][category]["total"] += 1

    is_covered = any(any(kw in title for kw in matched_keywords) for title in runbook_titles)

    if is_covered:
        stats["summary"]["covered_by_runbook"] += 1
        stats["by_category"][category]["covered"] += 1
    else:
        stats["summary"]["missing_runbooks"] += 1
        stats["by_category"][category]["missing"] += 1
        stats["missing_runbooks"].append({
            "query_text": query,
            "category": category
        })

# === Save Output to JSON File ===
output_data = {
    "summary": stats["summary"],
    "by_category": stats["by_category"],
    "missing_runbooks": stats["missing_runbooks"]
}

with open("runbook_coverage_report.json", "w") as f:
    json.dump(output_data, f, indent=2)

print("\n✅ Saved report to 'runbook_coverage_report.json'")

