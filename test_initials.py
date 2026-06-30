import re

def clean_str(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

def check_initial_mismatch(name, handle):
    name_parts = [p.strip(" .").lower() for p in name.split()]
    initials = [p for p in name_parts if len(p) == 1]
    if not initials:
        return False
    initial = initials[0]
    
    handle_clean = clean_str(handle)
    for p in name_parts:
        clean_p = clean_str(p)
        if len(clean_p) >= 3:
            if clean_p in handle_clean:
                handle_clean = handle_clean.replace(clean_p, "")
            elif handle_clean.startswith(clean_p[:4]):
                handle_clean = handle_clean[len(clean_p[:4]):]
            elif handle_clean.startswith(clean_p[:3]):
                handle_clean = handle_clean[len(clean_p[:3]):]
            elif clean_p.startswith(handle_clean):
                # Handle is entirely a prefix of the name (e.g. name "gajalakshmi", handle "gaja")
                handle_clean = ""
            
    handle_remaining_letters = re.sub(r'[^a-z]', '', handle_clean)
    if handle_remaining_letters:
        first_letter = handle_remaining_letters[0]
        if first_letter != initial:
            return True
    return False

def is_name_handle_match(name, handle):
    if check_initial_mismatch(name, handle):
        return False
        
    name = name.lower()
    handle = handle.lower()
    parts = [p.strip(" .") for p in name.split()]
    parts = [p for p in parts if len(p) >= 2 and p not in {"sri", "sai", "mr", "ms", "dr"}]
    
    clean_h = clean_str(handle)
    if not clean_h:
        return False
        
    for part in parts:
        clean_p = clean_str(part)
        if len(clean_p) >= 3:
            if clean_p in clean_h or clean_h in clean_p:
                return True
            if len(clean_p) >= 5 and clean_h.startswith(clean_p[:4]):
                return True
            if len(clean_h) >= 5 and clean_p.startswith(clean_h[:4]):
                return True
                
    if len(parts) >= 2:
        initials = "".join([p[0] for p in parts])
        if len(initials) >= 3 and initials in clean_h:
            return True
            
    return False

# Test cases
test_cases = [
    ("Gajalakshmi S", "gaja_56", True),
    ("Gayathri R", "Gayathri_R14", True),
    ("Gayathri S", "Gayathri_S_2006", True),
    ("Gayathri R", "Gayathri_S_2006", False),
    ("Gayathri S", "Gayathri_R14", False),
]

for name, handle, expected in test_cases:
    res = is_name_handle_match(name, handle)
    print(f"Name: {name:15s} | Handle: {handle:20s} | Match: {res} (Expected: {expected})")
