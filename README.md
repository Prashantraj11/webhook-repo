# GitHub Webhook Event Receiver

A Flask application that listens for GitHub Webhook events (Push, Pull Request, Merge), stores them in MongoDB, and displays them in a real-time UI that auto-refreshes every 15 seconds.

## Application Flow

```
GitHub (action-repo)
  |  webhook POST  /webhook
  v
Flask Backend (app.py)
  |  parses payload via webhook_handler
  |  stores event via db service
  v
MongoDB (github_webhooks.github_events)
  |  queried by GET /events
  v
Frontend UI (index.html)  <-- polls /events every 15 seconds
```

## Project Structure

```
webhook-repo/
|-- app.py                        # Flask entry point (routes only)
|-- requirements.txt              # Python dependencies
|-- .env                          # Environment variables (MongoDB URI)
|
|-- models/
|   |-- __init__.py
|   |-- event.py                  # EventAction enum (PUSH, PULL, MERGE)
|                                 # Event dataclass with to_dict / from_dict
|
|-- db/
|   |-- __init__.py
|   |-- service.py                # MongoDB operations:
|                                 #   upsert_webhook_event(event)
|                                 #   find_all_events()
|                                 #   find_events_paginated(page, per_page)
|                                 #   find_events_by_action(action)
|                                 #   count_events()
|
|-- webhook_handler/
|   |-- __init__.py
|   |-- handler.py                # parse_webhook(event_type, payload) -> Event
|                                 #   Handles "push" and "pull_request" events
|                                 #   Detects merges (closed + merged = MERGE)
|
|-- templates/
    |-- index.html                # Frontend UI (table format, pagination,
                                  #   local timezone, 15s auto-refresh)
```

## Tech Stack

- **Backend:** Python 3, Flask
- **Database:** MongoDB (pymongo)
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Tunneling:** ngrok (to expose localhost to GitHub webhooks)

## Prerequisites

- Python 3.10+
- MongoDB Community Server (running locally on port 27017)
- Git
- ngrok (free account at https://ngrok.com)

## Setup & Run

### 1. Clone the repository

```bash
git clone https://github.com/Prashantraj11/webhook-repo.git
cd webhook-repo
```

### 2. Create virtual environment and install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Start MongoDB

Make sure MongoDB is running on `localhost:27017` (default port). If installed as a Windows service, it starts automatically.

### 4. Run the Flask server

```bash
python app.py
```

Server starts at `http://localhost:5000`

### 5. Expose with ngrok

Open a second terminal:

```bash
ngrok http 5000
```

Copy the HTTPS forwarding URL (e.g. `https://xxxx.ngrok-free.app`).

### 6. Configure GitHub Webhook on action-repo

1. Go to your **action-repo** on GitHub -> Settings -> Webhooks -> Add webhook
2. **Payload URL:** `https://xxxx.ngrok-free.app/webhook`
3. **Content type:** `application/json`
4. **Events:** Select "Let me select individual events" -> check **Pushes** and **Pull requests**
5. Click **Add webhook**

### 7. Test

- Push a commit to action-repo -> PUSH event appears in UI
- Create a Pull Request -> PULL event appears
- Merge the PR -> MERGE event appears

## API Endpoints

| Method | Path      | Description                              |
|--------|-----------|------------------------------------------|
| GET    | `/`       | Serves the frontend UI                   |
| POST   | `/webhook`| Receives GitHub webhook events           |
| GET    | `/events` | Returns paginated events as JSON         |

### GET /events query parameters

| Parameter  | Default | Description                  |
|------------|---------|------------------------------|
| `page`     | 1       | Page number                  |
| `per_page` | 10      | Number of events per page    |

### GET /events response example

```json
{
  "events": [
    {
      "request_id": "abc123...",
      "author": "Prashantraj11",
      "action": "PUSH",
      "from_branch": "",
      "to_branch": "main",
      "timestamp": "2026-02-28T03:16:00+05:30"
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 8
}
```

## MongoDB Schema

**Database:** `github_webhooks`
**Collection:** `github_events`

| Field        | Type   | Description                        |
|-------------|--------|------------------------------------|
| request_id  | string | Commit hash (push) or PR id       |
| author      | string | GitHub username                    |
| action      | string | PUSH, PULL, or MERGE (enum)       |
| from_branch | string | Source branch (empty for push)     |
| to_branch   | string | Target branch                      |
| timestamp   | string | ISO 8601 UTC timestamp             |

## UI Display Format

| Action | Format                                                         |
|--------|----------------------------------------------------------------|
| PUSH   | `{author} pushed to {to_branch} on {timestamp}`               |
| PULL   | `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}` |
| MERGE  | `{author} merged branch {from_branch} to {to_branch} on {timestamp}` |

## Environment Variables

| Variable    | Default                        | Description       |
|-------------|--------------------------------|-------------------|
| `MONGO_URI` | `mongodb://localhost:27017/`   | MongoDB connection URI |

## Related Repository

- **action-repo:** https://github.com/Prashantraj11/-action-repo
  This is the GitHub repository where pushes, pull requests, and merges are performed. GitHub webhooks on this repo send events to the Flask backend.
