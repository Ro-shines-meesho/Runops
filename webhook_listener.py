
PARENT_PAGE_ID = "2678227022"
# webhook_listener.py

from flask import Flask, request, jsonify
import specific  # Your specify.py is reused here
from config import PARENT_PAGE_ID

app = Flask(__name__)

@app.route("/")
def health_check():
    return "✅ Runbook Webhook Listener Active"

@app.route("/webhook", methods=["POST"])
def confluence_webhook():
    data = request.get_json()
    event_type = data.get("webhookEvent", "")

    if event_type in ["page_created", "page_updated"]:
        print(f"📥 Webhook received: {event_type} — triggering specify.py run")
        pages = specific.fetch_child_pages(PARENT_PAGE_ID)
        existing = specific.load_existing_data()
        specific.save_combined_data(existing, pages)
        return jsonify({"status": "runbook file updated", "event": event_type}), 200

    print(f"⚠️ Ignored webhook: {event_type}")
    return jsonify({"status": "ignored", "event": event_type}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)