import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_pdf_layout(name, pdf_path):
    print(f"\n{'='*60}")
    print(f"LAYOUT AUDIT: {name} ({pdf_path})")
    print(f"{'='*60}")
    doc = pymupdf.open(pdf_path)
    print(f"Total pages: {len(doc)}")
    for i, page in enumerate(doc):
        rect = page.rect
        # find the lowest text/drawing y1 on this page
        blocks = page.get_text("blocks")
        if blocks:
            max_y1 = max(b[3] for b in blocks)
            min_y0 = min(b[1] for b in blocks)
            print(f"  Page {i+1}: min_y0={min_y0:.1f}, max_y1={max_y1:.1f}, page_height={rect.height:.1f} (bottom margin remaining: {rect.height - max_y1:.1f} pt)")
        else:
            print(f"  Page {i+1}: empty")

check_pdf_layout("Paper 1: JANUS ALU", "ofc_paper_latex/main.pdf")
check_pdf_layout("Paper 2: APD Receiver", "ofc_apd_paper_latex/main.pdf")
check_pdf_layout("Paper 3: Optical Switch", "ofc_switch_paper_latex/main.pdf")
