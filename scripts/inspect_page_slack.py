import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect_paper(name, pdf_path):
    print(f"\n{'='*60}\n{name}\n{'='*60}")
    doc = pymupdf.open(pdf_path)
    for pno in range(len(doc)):
        p = doc[pno]
        blocks = p.get_text("blocks")
        content_blocks = [b for b in blocks if not (b[4].strip().isdigit() and b[3] > 740)]
        last_block = max(content_blocks, key=lambda b: b[3])
        print(f"Page {pno+1}: Total blocks={len(blocks)}, lowest content y1={last_block[3]:.2f} pt (Bottom margin: {p.rect.height - last_block[3]:.2f} pt)")
        last_lines = last_block[4].strip().splitlines()
        print(f"  Last line on page {pno+1}: {last_lines[-1] if last_lines else ''}")

inspect_paper("Paper 1: JANUS ALU", "ofc_paper_latex/main.pdf")
inspect_paper("Paper 2: APD Receiver", "ofc_apd_paper_latex/main.pdf")
inspect_paper("Paper 3: Optical Switch", "ofc_switch_paper_latex/main.pdf")
