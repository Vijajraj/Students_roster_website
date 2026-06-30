import json
import os
import re
from pypdf import PdfReader

def cross_check_by_reg():
    # Load the saved badge holders
    with open("knights.json", "r", encoding="utf-8") as f:
        badge_holders = json.load(f)
    
    # Build a lookup: reg_number -> leetcode_username
    holder_lookup = {}
    for b in badge_holders:
        # We need to find the student in the PDF to get their registration number.
        # But wait! We can store registration number in knights.json as well if we saved it.
        # Let's check what fields are in knights.json.
        # Let's inspect the first element of badge_holders first.
        pass

    # Let's print the keys of the first badge holder to see if 'reg' is present.
    if badge_holders:
        print("Fields in knights.json:", badge_holders[0].keys())
        # Let's see if we saved 'reg' or not. If we didn't save 'reg', we can't lookup by reg unless we add it.
        # Wait, in scan_entire_college.py, did we include "reg" in the badge_holders dict?
        # Let's check scan_entire_college.py lines 270-295:
        # badge_holders.append({
        #             "name": s["name"],
        #             "dept": s["dept"],
        #             "sec": s["sec"],
        #             "leetcode_username": s["leetcode"],
        # ...
        # No 'reg' was saved! Let's verify.
        
if __name__ == "__main__":
    cross_check_by_reg()
