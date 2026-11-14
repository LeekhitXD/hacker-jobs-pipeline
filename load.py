import csv
import sqlite3
from pathlib import Path

CSV_FILE = Path("clean/jobs.csv")
DB_FILE = Path("hn_jobs.db")


def create_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id        INTEGER PRIMARY KEY,
            posted_on TEXT,
            author    TEXT,
            company   TEXT,
            header    TEXT,
            is_remote INTEGER,
            text      TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_tools (
            job_id INTEGER,
            tool   TEXT,
            PRIMARY KEY (job_id, tool)
        )
    """)


def main():
    conn = sqlite3.connect(DB_FILE)
    create_tables(conn)

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        conn.execute(
            "INSERT OR REPLACE INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                int(row["id"]),
                row["posted_on"],
                row["author"],
                row["company"],
                row["header"],
                1 if row["is_remote"] == "True" else 0,
                row["text"],
            ),
        )

        # remove old tool rows for this job, then add the current ones
        conn.execute("DELETE FROM job_tools WHERE job_id = ?", (int(row["id"]),))
        for tool in filter(None, row["tools"].split(",")):
            conn.execute(
                "INSERT INTO job_tools VALUES (?, ?)", (int(row["id"]), tool)
            )

    conn.commit()
    conn.close()
    print(f"Loaded {len(rows)} jobs into {DB_FILE}")


if __name__ == "__main__":
    main()