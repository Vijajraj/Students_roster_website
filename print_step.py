import json
import os

log_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript_full.jsonl")

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            step = json.loads(line)
            if step.get("step_index") == 187:
                print(f"Step 187 content:")
                print(step.get("content"))
                break
        except Exception:
            pass
