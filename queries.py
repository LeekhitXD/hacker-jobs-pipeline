import sqlite3

conn = sqlite3.connect("hn_jobs.db")

print("--- Most mentioned tools ---")
for tool, count in conn.execute("""
    SELECT tool, COUNT(*) AS posts
    FROM job_tools
    GROUP BY tool
    ORDER BY posts DESC
"""):
    print(f"{tool:12} {count}")

print("\n--- Remote vs not ---")
for is_remote, count in conn.execute("""
    SELECT is_remote, COUNT(*) FROM jobs GROUP BY is_remote
"""):
    print("remote" if is_remote else "not marked remote", count)

print("\n--- Posts mentioning data engineering ---")
for company, header in conn.execute("""
    SELECT company, header FROM jobs
    WHERE LOWER(text) LIKE '%data engineer%'
"""):
    print(company, "|", header)