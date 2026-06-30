import json
import os
import re

log_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript_full.jsonl")

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            step = json.loads(line)
            content = step.get("content", "")
            if "==Start of OCR" in content:
                print(f"Step Index: {step.get('step_index')} | Type: {step.get('type')}")
                print(f"Content length: {len(content)}")
                # Print first 500 characters of the OCR block
                idx = content.find("==Start of OCR")
                print("Snippet from OCR block:")
                print(content[idx:idx+800])
                
                # Check regex matching
                matches = re.findall(r"^\d+\s+\d{2}[A-Za-z]{2,4}\d{4,5}\s+.*$", content, re.MULTILINE)
                print(f"Regex matches count: {len(matches)}")
                break
        except Exception as e:
            print("Error:", e)
