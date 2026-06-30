import json
import os

log_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript_full.jsonl")

with open(transcript_path, "r", encoding="utf-8") as f:
    for idx in range(10):
        line = f.readline()
        if not line:
            break
        try:
            step = json.loads(line)
            print(f"[{idx}] Type: {step.get('type')} | Source: {step.get('source')} | Keys: {list(step.keys())}")
            content = str(step.get('content', ''))
            print(f"      Content snippet: {content[:100]}")
        except Exception as e:
            print(f"Error parsing line {idx}: {e}")
