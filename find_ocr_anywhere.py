import json
import os

log_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript_full.jsonl")

found_steps = []

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            step = json.loads(line)
            content = str(step.get("content", ""))
            thinking = str(step.get("thinking", ""))
            
            if "Start of OCR" in content or "1283 24AD0001" in content:
                found_steps.append((step.get("step_index"), "content", len(content)))
            if "Start of OCR" in thinking or "1283 24AD0001" in thinking:
                found_steps.append((step.get("step_index"), "thinking", len(thinking)))
        except Exception as e:
            pass

print(f"Found matches in the following steps: {found_steps}")
