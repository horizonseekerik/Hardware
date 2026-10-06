import fitz
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect_pdf_equations(name, pdf_path):
    print(f"\n{'='*60}")
    print(f"INSPECTING EQUATIONS IN PDF: {name} ({pdf_path})")
    print(f"{'='*60}")
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")
        for b in blocks:
            text = b[4].strip()
            # Look for lines with equation numbers like (1), (2), etc.
            lines = text.splitlines()
            for line in lines:
                m = re.search(r'\((\d+)\)\s*$', line)
                if m:
                    print(f"Page {page_num+1} | BBox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) | Text: {line}")
                    # check if line reaches right margin
                    # Page width for 8.5x11 is 612 pt. Margins 1 in = 72 pt on each side. Text width = 468 pt. Right margin = 540 pt.
                    print(f"       Line width / position: block x0={b[0]:.1f}, x1={b[2]:.1f} (target right margin ~540)")

inspect_pdf_equations("Paper 1: JANUS ALU", "ofc_paper_latex/main.pdf")
inspect_pdf_equations("Paper 2: APD Receiver", "ofc_apd_paper_latex/main.pdf")
inspect_pdf_equations("Paper 3: Optical Switch", "ofc_switch_paper_latex/main.pdf")
