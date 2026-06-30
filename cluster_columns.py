import os
import re
from pypdf import PdfReader

def cluster_positions(positions, count=4):
    # Simple 1D clustering to find column start boundaries
    if not positions:
        return []
    positions = sorted(list(set(positions)))
    clusters = []
    current_cluster = [positions[0]]
    
    for pos in positions[1:]:
        if pos - current_cluster[-1] <= 8:  # Group positions within 8 chars
            current_cluster.append(pos)
        else:
            clusters.append(current_cluster)
            current_cluster = [pos]
    clusters.append(current_cluster)
    
    # Representative of each cluster is its minimum or average
    centers = [min(c) for c in clusters]
    return centers

def test_dynamic_columns():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    
    reader = PdfReader(pdf_path)
    row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
    
    for page_num in range(5):  # Check first 5 pages
        page = reader.pages[page_num]
        text = page.extract_text(extraction_mode="layout")
        if not text:
            continue
            
        lines = text.split("\n")
        
        # Collect all start indices of words after character index 120
        word_starts = []
        for line in lines:
            if not line.strip():
                continue
            stripped = line.strip()
            match = row_pattern.match(stripped)
            if not match:
                continue
                
            # Find start indices of words in the handles section
            # We look for non-space sequences starting after index 120
            for m in re.finditer(r"\S+", line):
                start = m.start()
                if start >= 120:
                    word_starts.append(start)
                    
        # Cluster the word starts to find the 4 handle columns
        centers = cluster_positions(word_starts)
        # We only want centers that correspond to the columns (should have about 3 or 4 centers)
        print(f"Page {page_num+1} detected column starts: {centers}")

if __name__ == "__main__":
    test_dynamic_columns()
