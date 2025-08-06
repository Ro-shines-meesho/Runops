from flask import Flask, request
from specific import fetch_child_pages, load_existing_runbooks, save_runbooks

app = Flask(__name__)
PARENT_PAGE_ID = "2678227022"

@app.route('/runbook-notify', methods=['POST'])
def handle_webhook():
    print("📩 Webhook received for page creation.")
    new_pages = fetch_child_pages(PARENT_PAGE_ID)
    existing_data = load_existing_runbooks()
    save_runbooks(existing_data, new_pages)
    return {"status": "success"}, 200

if __name__ == '__main__':
    app.run(port=8080)
