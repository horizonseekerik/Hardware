import pymupdf as fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

targets = [
    ('Paper 1 (ALU)', 'ofc_paper_latex/main.pdf'),
    ('Paper 2 (APD)', 'ofc_apd_paper_latex/main.pdf'),
    ('Paper 3 (Switch)', 'ofc_switch_paper_latex/main.pdf')
]

for name, pdf_path in targets:
    print(f"\n==========================================")
    print(f"{name}: {pdf_path}")
    print(f"==========================================")
    doc = fitz.open(pdf_path)
    for p_idx, page in enumerate(doc):
        image_list = page.get_images()
        text_page = page.get_text('dict')
        
        fig_captions = []
        sublabels = []
        other_lines = []
        for b in text_page['blocks']:
            if 'lines' in b:
                for l in b['lines']:
                    txt = ''.join(s['text'] for s in l['spans']).strip()
                    bbox = l['bbox']
                    if (txt.startswith("Fig.") or txt.startswith("Figure") or 
                        "Architecture and Optical" in txt or "Cloud HPC 100M" in txt or 
                        "Optoelectronic Sign-Off" in txt or "Electro-thermal switching" in txt or 
                        "Thermal endurance" in txt or "Meep FDTD" in txt):
                        fig_captions.append((bbox, txt))
                    elif txt in ["(a)", "(b)", "(c)"]:
                        sublabels.append((bbox, txt))
                    else:
                        other_lines.append((bbox, txt))

        print(f"--- Page {p_idx+1} (Images: {len(image_list)}) ---")
        for cb, ct in fig_captions:
            print(f"  CAPTION at y0={cb[1]:.2f}, y1={cb[3]:.2f}: {ct[:60]}...")
            for sb, st in sublabels:
                if abs(sb[3] - cb[1]) < 30 or (sb[1] < cb[3] and sb[3] > cb[1]):
                    dist = cb[1] - sb[3]
                    print(f"    -> Sublabel '{st}' at y0={sb[1]:.2f}, y1={sb[3]:.2f}. Vertical clearance to caption: {dist:.2f} pt")
                    if dist < 0:
                        print(f"    *** OVERLAP DETECTED! ***")
            for ob, ot in other_lines:
                y_ov = min(cb[3], ob[3]) - max(cb[1], ob[1])
                x_ov = min(cb[2], ob[2]) - max(cb[0], ob[0])
                if y_ov > 0.5 and x_ov > 20:
                    print(f"    *** TEXT OVERLAP WITH CAPTION! ***")
                    print(f"        Overlap: y={y_ov:.2f}pt, x={x_ov:.2f}pt")
                    print(f"        Line: '{ot}' at y0={ob[1]:.2f}, y1={ob[3]:.2f}")
