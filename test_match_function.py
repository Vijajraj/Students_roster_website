import re

def clean_str(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

def is_name_handle_match(name, handle):
    name = name.lower()
    handle = handle.lower()
    
    # Extract all name parts
    parts = [p.strip(" .") for p in name.split()]
    parts = [p for p in parts if len(p) >= 2] # ignore single letter initials first
    
    clean_h = clean_str(handle)
    if not clean_h:
        return False
        
    for part in parts:
        clean_p = clean_str(part)
        if len(clean_p) >= 3:
            # 1. Direct substring
            if clean_p in clean_h or clean_h in clean_p:
                return True
            # 2. Prefix match (e.g. "sriram" and "sri_06btech" -> "sri" prefix of length >= 3)
            if len(clean_p) >= 4 and clean_h.startswith(clean_p[:3]):
                return True
            if len(clean_h) >= 4 and clean_p.startswith(clean_h[:3]):
                return True
                
    # Fallback to initials if name has multiple parts
    if len(parts) >= 2:
        initials = "".join([p[0] for p in parts])
        if len(initials) >= 3 and initials in clean_h:
            return True
            
    return False

# Test cases
test_cases = [
    ("Sriram R", "sri_06btech", True),
    ("Swathi S V", "swathi_shankar", True),
    ("Srivarshini R", "sudharsan_wnl", False),
    ("Srivarshini R", "srivarshini_r", True),
    ("Abishek K", "ryoUaQAKNN", False),
]

for name, handle, expected in test_cases:
    res = is_name_handle_match(name, handle)
    print(f"Name: {name:20s} | Handle: {handle:20s} | Match: {res} (Expected: {expected})")
