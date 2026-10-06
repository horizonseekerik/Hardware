import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def audit_paper(name, path):
    print(f"\n=======================================================")
    print(f"AUDITING: {name}")
    print(f"=======================================================")
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract body between \begin{document} and \begin{thebibliography}
    doc_match = re.search(r'\\begin\{document\}(.*?)(?:\\begin\{thebibliography\}|\\end\{document\})', text, re.DOTALL)
    if not doc_match:
        print("Could not find document body!")
        return
    body = doc_match.group(1)

    # 1. Equations check
    print("\n--- 1.5.2 MATH: EQUATIONS ---")
    eqs = re.findall(r'(\\begin\{equation\}.*?\\end\{equation\})', body, re.DOTALL)
    for i, eq in enumerate(eqs, 1):
        one_line = " ".join(eq.split())
        print(f"  Eq ({i}): {one_line}")

    # 2. Inline math fractions check
    print("\n--- 1.5.2 MATH: INLINE FRACTIONS & DIVISIONS ---")
    inline_maths = re.findall(r'\$([^$]+)\$', body)
    for m in inline_maths:
        # Check if contains '/'
        if '/' in m:
            # Let's inspect
            print(f"  ${m.strip()}$")

    # 3. Check for any summation or integral in text
    print("\n--- 1.5.2 MATH: SUMS & INTEGRALS ---")
    sums_ints = [m.strip() for m in inline_maths if any(k in m for k in [r'\sum', r'\int', r'\prod'])]
    if not sums_ints:
        print("  None in inline math.")
    else:
        for si in sums_ints:
            print(f"  ${si}$")

    # 4. Acronyms check
    print("\n--- 1.5.1 GENERAL NOTATION: ACRONYMS ---")
    # Find all capitalized sequences of 2-6 chars
    words = re.findall(r'\b[A-Z0-9]{2,8}\b', body)
    ignore = {
        'THE', 'AND', 'FOR', 'WITH', 'FROM', 'THIS', 'THAT', 'NOT', 'ARE', 'BUT', 'ALL',
        'CAN', 'HAS', 'HAD', 'WAS', 'ONE', 'TWO', 'NEW', 'FIG', 'REF', 'SEC', 'TAB',
        'TABLE', 'IEEE', 'USA', 'OFC', 'JLT', 'OSA', 'OPTICA', 'ALU', 'P1', 'P2', 'P3',
        'III', 'IV', 'VII', 'VIII', 'RMS', 'BER', 'SNR', 'DC', 'AC', 'TEM', 'TE', 'TM',
        'PDF', 'BEGIN', 'END', 'TEXT', 'WIDTH', 'HFILL', 'VSPACE', 'HSPACE', 'LARGE',
        'SMALL', 'TINY', 'LARGE', 'HUGE', 'BF', 'IT', 'RM', 'SF', 'TT', 'CENTER',
        'MINIPAGE', 'TABULAR', 'GRAPHICS', 'INCLUDEGRAPHICS', 'CAPTION', 'LABEL',
        'REF', 'EQREF', 'CITE', 'MBOX', 'TEXTIT', 'TEXTBF', 'TEXTRM', 'TEXTSC',
        'MATHRM', 'MATHBF', 'TEXTWIDTH', 'COLUMNDIR', 'TOPRULE', 'MIDRULE', 'BOTTOMRULE'
    }
    
    # Track first appearance of each acronym and whether it is defined
    seen = {}
    for match in re.finditer(r'\b[A-Z][A-Z0-9]{1,7}\b', body):
        w = match.group(0)
        if w in ignore or w.isdigit():
            continue
        if w not in seen:
            seen[w] = match.start()

    # Sort by appearance in text
    sorted_acronyms = sorted(seen.keys(), key=lambda k: seen[k])
    for ac in sorted_acronyms:
        idx = seen[ac]
        context = body[max(0, idx-40):min(len(body), idx+len(ac)+40)].replace('\n', ' ')
        # Check if defined nearby (e.g. within 100 chars, either before or after)
        local_window = body[max(0, idx-100):min(len(body), idx+len(ac)+100)].replace('\n', ' ')
        is_def = (f"({ac})" in local_window or f"({ac}," in local_window)
        print(f"  {ac:<12} | Defined nearby? {is_def:<5} | Context: ...{context}...")

audit_paper('Paper 1: JANUS ALU', 'ofc_paper_latex/main.tex')
audit_paper('Paper 2: APD Receiver', 'ofc_apd_paper_latex/main.tex')
audit_paper('Paper 3: Optical Switch', 'ofc_switch_paper_latex/main.tex')
