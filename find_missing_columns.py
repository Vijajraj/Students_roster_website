import os
import re

def inspect_roster():
    depts = {"AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"}
    
    with open("raw_ocr.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    print(f"Total lines in raw_ocr.txt: {len(lines)}")
    
    # Analyze the number of tokens in each line
    token_counts = {}
    for idx, line in enumerate(lines, 1):
        tokens = line.strip().split()
        count = len(tokens)
        token_counts[count] = token_counts.get(count, 0) + 1
        
        # If the number of tokens is small, print it
        if count < 9:
            print(f"Row {idx} (Short, {count} tokens): {line.strip()}")
            
    print("\nToken counts distribution:")
    for count, freq in sorted(token_counts.items()):
        print(f"  {count} tokens: {freq} rows")
        
    print("\nChecking for potential mismatched IDs (e.g. LeetCode ID matches a department or section):")
    mismatches = 0
    for idx, line in enumerate(lines, 1):
        tokens = line.strip().split()
        if len(tokens) < 8:
            continue
            
        # Scan for department to find dept index
        dept_idx = -1
        for i, token in enumerate(tokens):
            if token.upper() in depts:
                dept_idx = i
                break
                
        if dept_idx == -1:
            continue
            
        # Try to parse the last columns
        # In a perfect row, LeetCode ID is at index -4
        leetcode = tokens[-4]
        codechef = tokens[-3]
        codeforces = tokens[-2]
        github = tokens[-1]
        
        # If any of the parsed IDs are in the departments, section letters, or training types, it's a mismatch!
        sec = tokens[dept_idx + 1] if dept_idx + 1 < len(tokens) else ""
        training = tokens[dept_idx + 2] if dept_idx + 2 < len(tokens) else ""
        
        invalid_ids = {sec.lower(), training.lower(), "training", "japanese", "german", "hs", "p", "nt"}
        for d in depts:
            invalid_ids.add(d.lower())
            
        if leetcode.lower() in invalid_ids or codeforces.lower() in invalid_ids or github.lower() in invalid_ids:
            print(f"Row {idx} mismatched! Tokens: {tokens}")
            print(f"  Parsed as -> LeetCode: {leetcode} | CodeChef: {codechef} | CodeForces: {codeforces} | GitHub: {github}")
            mismatches += 1
            if mismatches >= 10:
                print("  ... showing first 10 mismatches ...")
                break

if __name__ == "__main__":
    inspect_roster()
