import json

with open("knights_raw.json", "r", encoding="utf-8") as f:
    posts = json.load(f)

for idx, p in enumerate(posts):
    print(f"[{idx}] Title: {p.get('title')} | Source: {p.get('source')} | Link: {p.get('link')}")
