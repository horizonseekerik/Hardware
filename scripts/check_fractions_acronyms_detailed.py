import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def detailed_inspection(name, path):
    print(f"\n{'='*70}")
    print(f"DETAILED NOTATION AUDIT: {name}")
    print(f"{'='*70}")
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find where \begin{document} starts
    doc_start = 0
    for idx, l in enumerate(lines):
        if r'\begin{document}' in l:
            doc_start = idx
            break

    # 1. Inspect all inline fractions
    print("\n--- 1. INLINE SLASH EXPRESSIONS & PARENTHESIS CHECK ---")
    for line_idx, line in enumerate(lines[doc_start:], doc_start + 1):
        clean_l = line.split('%')[0]
        # find all $...$
        matches = re.findall(r'\$([^$]+)\$', clean_l)
        for m in matches:
            if '/' in m:
                # check if it is just a unit like dB/cm or a mathematical division
                is_unit = bool(re.search(r'\\text\{[a-zA-Z]+/|/(?:cm|stage|crossing|cell|cycle|bit|Box|mol|K|s|MAC|mm|shifter)\b', m))
                print(f"  Line {line_idx:4d} | {'[UNIT]' if is_unit else '[MATH]'}: ${m}$")

    # 2. Inspect acronyms in body text
    print("\n--- 2. ACRONYM FIRST-USE CHECK ---")
    body_text = "".join(lines[doc_start:])
    # Find all acronyms (2+ capital letters)
    # Exclude standard LaTeX commands and common non-acronyms
    exclude = {
        'THE', 'AND', 'FOR', 'WITH', 'FROM', 'THIS', 'THAT', 'NOT', 'ARE', 'BUT', 'ALL',
        'CAN', 'HAS', 'HAD', 'WAS', 'ONE', 'TWO', 'NEW', 'FIG', 'REF', 'SEC', 'TAB',
        'TABLE', 'IEEE', 'USA', 'OFC', 'JLT', 'OSA', 'OPTICA', 'ALU', 'P1', 'P2', 'P3',
        'III', 'IV', 'VII', 'VIII', 'RMS', 'BER', 'SNR', 'DC', 'AC', 'TEM', 'TE', 'TM',
        'PDF', 'BEGIN', 'END', 'TEXT', 'WIDTH', 'HFILL', 'VSPACE', 'HSPACE', 'LARGE',
        'SMALL', 'TINY', 'HUGE', 'BF', 'IT', 'RM', 'SF', 'TT', 'CENTER',
        'MINIPAGE', 'TABULAR', 'GRAPHICS', 'INCLUDEGRAPHICS', 'CAPTION', 'LABEL',
        'EQREF', 'CITE', 'MBOX', 'TEXTIT', 'TEXTBF', 'TEXTRM', 'TEXTSC',
        'MATHRM', 'MATHBF', 'TEXTWIDTH', 'COLUMNDIR', 'TOPRULE', 'MIDRULE', 'BOTTOMRULE',
        'AUTHOR', 'AFFIL', 'ADDRESS', 'EMAIL', 'TITLE', 'ABSTRACT', 'BIBITEM', 'THEBIBLIOGRAPHY'
    }

    # Find occurrences in lines
    first_seen = {}
    for line_idx, line in enumerate(lines[doc_start:], doc_start + 1):
        clean_l = line.split('%')[0]
        # remove math blocks to avoid counting math variables like XY, DR, etc.
        no_math = re.sub(r'\$[^$]+\$', ' ', clean_l)
        no_cmd = re.sub(r'\\[a-zA-Z]+', ' ', no_math)
        tokens = re.findall(r'\b[A-Z][A-Z0-9\-]{1,6}[A-Z0-9]\b', no_cmd)
        for t in tokens:
            if t not in exclude and not t.isdigit():
                if t not in first_seen:
                    first_seen[t] = (line_idx, clean_l.strip())

    for ac, (lno, text_line) in first_seen.items():
        # Check if definition exists in the whole document
        # Search for pattern: Full Name (AC) or AC (Full Name)
        # Or if AC is enclosed in parentheses
        has_paren = f"({ac})" in body_text or f"({ac}," in body_text
        print(f"  Line {lno:4d} | {ac:<10} | In Parens?: {has_paren:<5} | Context: {text_line[:90]}...")

if len(sys.argv) > 1:
    target = sys.argv[1]
    if target == '1':
        detailed_inspection('Paper 1: JANUS ALU', 'ofc_paper_latex/main.tex')
    elif target == '2':
        detailed_inspection('Paper 2: APD Receiver', 'ofc_apd_paper_latex/main.tex')
    elif target == '3':
        detailed_inspection('Paper 3: Optical Switch', 'ofc_switch_paper_latex/main.tex')
else:
    detailed_inspection('Paper 1: JANUS ALU', 'ofc_paper_latex/main.tex')
    detailed_inspection('Paper 2: APD Receiver', 'ofc_apd_paper_latex/main.tex')
    detailed_inspection('Paper 3: Optical Switch', 'ofc_switch_paper_latex/main.tex')
