import requests
import json
import time
from pathlib import Path



BASE_URL = "https://hacker-news.firebaseio.com/v0"
RAW_DIR = Path("raw")


def fetch_item(item_id):
    """Ask the API for one item and return it as a Python dictionary."""
    response = requests.get(f"{BASE_URL}/item/{item_id}.json", timeout=10)
    response.raise_for_status()  # stops with an error if the request failed
    return response.json()


def extract_thread(thread_id):
    """Fetch a thread and all its comments, and save them as raw JSON."""
    thread = fetch_item(thread_id)
    comments = []

    for comment_id in thread.get("kids", []):
        comments.append(fetch_item(comment_id))
        time.sleep(0.1)  # small pause, be polite to the server

    RAW_DIR.mkdir(exist_ok=True)
    out_file = RAW_DIR / f"thread_{thread_id}.json"
    out_file.write_text(json.dumps(comments, indent=2))
    print(f"Saved {len(comments)} comments to {out_file}")


if __name__ == "__main__":
    extract_thread(50338728) 