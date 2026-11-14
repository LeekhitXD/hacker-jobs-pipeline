import json

with open("raw/thread_50338728.json") as f:
    comments = json.load(f)

print("Total items:", len(comments))
print("First item:")
print(json.dumps(comments[0], indent=2))