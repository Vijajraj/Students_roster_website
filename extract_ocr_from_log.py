import json
import os
import re

def extract_ocr():
    log_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5\.system_generated\logs"
    transcript_path = os.path.join(log_dir, "transcript_full.jsonl")
    
    if not os.path.exists(transcript_path):
        print(f"Error: Transcript log not found at {transcript_path}")
        return
        
    print(f"Reading conversation history transcript from {transcript_path}...")
    
    ocr_lines = []
    page_matches = 0
    
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                step = json.loads(line)
                # Look for user input messages containing the OCR text
                if step.get("source") == "USER_EXPLICIT" or step.get("type") == "USER_INPUT":
                    content = step.get("content", "")
                    if "==Start of OCR" in content:
                        # Extract all lines that look like: "1283 24AD0001 ..."
                        matches = re.findall(r"^\d+\s+\d{2}[A-Za-z]{2,4}\d{4,5}\s+.*$", content, re.MULTILINE)
                        if matches:
                            ocr_lines.extend(matches)
                            page_matches += 1
            except Exception as e:
                pass
                
    # Deduplicate lines by S.No
    unique_lines = {}
    for line in ocr_lines:
        tokens = line.split()
        if tokens:
            sno = tokens[0]
            unique_lines[sno] = line
            
    sorted_sno = sorted(unique_lines.keys(), key=lambda x: int(x) if x.isdigit() else 0)
    sorted_ocr = [unique_lines[sno] for sno in sorted_sno]
    
    # Save the consolidated OCR data
    with open("raw_ocr.txt", "w", encoding="utf-8") as f:
        for line in sorted_ocr:
            f.write(line + "\n")
            
    print(f"\nConsolidated OCR data: extracted {len(sorted_ocr)} student rows from conversation transcript across different pages!")

if __name__ == "__main__":
    extract_ocr()
