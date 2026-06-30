import re, os
from pypdf import PdfReader

def check_corrected_handles():
    # Import the function from scan_entire_college
    import sys
    sys.path.append(".")
    from scan_entire_college import parse_roster_from_pdf
    
    students = parse_roster_from_pdf()
    
    # Find students in the range Sno 1563 to 1602
    for s in students:
        sno_int = int(s["reg"][-4:]) if s["reg"][-4:].isdigit() else 0 # wait, let's just print by name or reg
        # Let's print students whose name starts with S or V and dept is AIDS
        if s["dept"] == "AIDS" and s["name"][0] in {"S", "V", "U", "T", "Y"}:
            print(f"Name: {s['name']:25s} | Reg: {s['reg']} | LC: {s['leetcode']:20s} | CF: {s['codeforces']}")

if __name__ == "__main__":
    check_corrected_handles()
