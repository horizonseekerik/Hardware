import pymupdf as fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

targets = [
    ('Paper 1 (ALU)', 'ofc_paper_latex/main.pdf'),
    ('Paper 2 (APD)', 'ofc_apd_paper_latex/main.pdf'),
    ('Paper 3 (Switch)', 'ofc_switch_paper_latex/main.pdf')
]

for name, pdf_path in targets:
    print(f"\n==================================================")
    print(f"Checking {name}: {pdf_path}")
    print(f"==================================================")
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        continue

    for p_idx, page in enumerate(doc):
        blocks = page.get_text('dict')['blocks']
        lines = []
        for b in blocks:
            if 'lines' in b:
                for l in b['lines']:
                    text = ''.join(s['text'] for s in l['spans']).strip()
                    if text:
                        lines.append((fitz.Rect(l['bbox']), text))
        
        found = False
        for i in range(len(lines)):
            b1, t1 = lines[i]
            for j in range(i+1, len(lines)):
                b2, t2 = lines[j]
                y_overlap = min(b1.y1, b2.y1) - max(b1.y0, b2.y0)
                x_overlap = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
                # If vertical overlap is more than 3pt and horizontal overlap is more than 15pt
                if y_overlap > 3.0 and x_overlap > 15.0:
                    found = True
                    print(f"  P{p_idx+1} COLLISION (y_overlap={y_overlap:.1f}pt, x_overlap={x_overlap:.1f}pt):")
                    print(f"     Text 1 (y0={b1.y0:.1f}, y1={b1.y1:.1f}): {t1}")
                    print(f"     Text 2 (y0={b2.y0:.1f}, y1={b2.y1:.1f}): {t2}")
        if not found:
            print(f"  P{p_idx+1}: Clean!")
