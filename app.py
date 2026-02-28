import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from db import init_db, upsert_webhook_event, find_events_paginated, count_events
from webhook_handler import parse_webhook

load_dotenv()

app = Flask(__name__)
init_db()
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json
    event_type = request.headers.get("X-GitHub-Event", "unknown")

    event = parse_webhook(event_type, payload)

    if event is None:
        print(f"[INFO] Received unhandled event: {event_type}")
        return jsonify({"status": "ignored", "event": event_type}), 200

    upsert_webhook_event(event)
    print(
        f"[OK] {event.action.value} event saved -- "
        f"{event.author} {event.from_branch} -> {event.to_branch}"
    )
    return jsonify({"status": "success", "event": event.action.value}), 200

@app.route("/events", methods=["GET"])
def get_events():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    events = find_events_paginated(page, per_page)
    total = count_events()

    return jsonify({
        "events": events,
        "page": page,
        "per_page": per_page,
        "total": total,
    })


if __name__ == "__main__":
    print("Flask server running on http://localhost:5000")
    print("  Webhook endpoint:  POST http://localhost:5000/webhook")
    print("  Events API:        GET  http://localhost:5000/events")
    print("  Frontend UI:       GET  http://localhost:5000/")
    app.run(debug=True, host="0.0.0.0", port=5000)
