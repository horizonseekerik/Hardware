import pymupdf as fitz, sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect_lines(pdf_path):
    print(f"\n=== REAL VISUAL LINES IN {pdf_path} ===")
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Could not open {pdf_path}: {e}")
        return
    for p_idx, page in enumerate(doc):
        words = page.get_text('words')
        lines = {}
        for w in words:
            key = (w[5], w[6])
            if key not in lines:
                lines[key] = []
            lines[key].append(w[4])
        
        for key, w_list in lines.items():
            line_str = " ".join(w_list).strip()
            if not line_str:
                continue
            last = w_list[-1]
            bad_op = None
            for op in ['=', '+', '-', '—', '–', '<', '>', '≤', '≥', '≈']:
                if last == op or last.endswith(op):
                    bad_op = op
                    break
            is_lone_num = last.isdigit() and len(last) <= 3 and len(w_list) > 1 and not w_list[0].isdigit() and w_list[0] not in ['Fig.', 'Table', '[1]', '[2]', '[3]', '[4]', '[5]', '[6]', '[7]', '[8]', '[9]', '[10]', '[11]', '[12]', '[13]', '[14]']
            
            if bad_op or is_lone_num:
                reason = f"ends with '{bad_op}'" if bad_op else f"lone number '{last}'"
                print(f"P{p_idx+1} ({reason}): {line_str}")

if __name__ == '__main__':
    targets = sys.argv[1:] if len(sys.argv) > 1 else [
        'ofc_paper_latex/main.pdf',
        'ofc_apd_paper_latex/main.pdf',
        'ofc_switch_paper_latex/main.pdf'
    ]
    for target in targets:
        inspect_lines(target)

