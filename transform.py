import csv
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

RAW_FILE = Path("raw/thread_50338728.json")
CLEAN_DIR = Path("clean")

# tool name -> pattern that finds it in the text
TOOLS = {
    "python": r"\bpython\b",
    "sql": r"\bsql\b",
    "airflow": r"\bairflow\b",
    "dbt": r"\bdbt\b",
    "spark": r"\bspark\b",
    "snowflake": r"\bsnowflake\b",
    "databricks": r"\bdatabricks\b",
    "kafka": r"\bkafka\b",
    "aws": r"\baws\b",
    "azure": r"\bazure\b",
    "gcp": r"\b(gcp|google cloud)\b",
    "postgres": r"\bpostgres(ql)?\b",
    "docker": r"\bdocker\b",
    "kubernetes": r"\bkubernetes\b",
}


def clean_text(raw_html):
    """Turn messy HTML into plain readable text."""
    text = raw_html.replace("<p>", "\n")   # paragraph breaks -> new lines
    text = re.sub(r"<[^>]+>", "", text)    # remove all other tags
    return html.unescape(text).strip()     # decode &#x27; etc.


def find_tools(text):
    """Return the list of tools mentioned in the text."""
    lowered = text.lower()
    return [name for name, pattern in TOOLS.items() if re.search(pattern, lowered)]


def transform_item(item):
    """Turn one raw comment into one clean row."""
    text = clean_text(item["text"])
    header = text.split("\n")[0]           # first line: Company | Location | ...
    return {
        "id": item["id"],
        "posted_on": datetime.fromtimestamp(item["time"], tz=timezone.utc).strftime("%Y-%m-%d"),
        "author": item.get("by", ""),
        "company": header.split("|")[0].strip(),
        "header": header,
        "is_remote": "remote" in header.lower(),
        "tools": ",".join(find_tools(text)),
        "text": text,
    }
def main():
    items = json.loads(RAW_FILE.read_text())

    rows = []
    skipped = 0
    for item in items:
        # skip deleted, dead, or empty comments
        if item.get("deleted") or item.get("dead") or not item.get("text"):
            skipped += 1
            continue
        rows.append(transform_item(item))

    CLEAN_DIR.mkdir(exist_ok=True)
    out_file = CLEAN_DIR / "jobs.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Kept {len(rows)} rows, skipped {skipped}. Saved to {out_file}")


if __name__ == "__main__":
    main()