import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

papers = [
    ("Paper 1: JANUS ALU", "ofc_paper_latex/main.tex"),
    ("Paper 2: APD Receiver", "ofc_apd_paper_latex/main.tex"),
    ("Paper 3: Optical Switch", "ofc_switch_paper_latex/main.tex")
]

for name, path in papers:
    print(f"\n{'='*60}")
    print(f"{name} ({path})")
    print(f"{'='*60}")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Strip comments
    lines = [line.split('%')[0] for line in content.splitlines()]
    clean_text = '\n'.join(lines)

    # 1. Equations check
    print("\n[1.5.2 MATH NOTATION] Numbered display equations:")
    eqs = re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}', clean_text, re.DOTALL)
    for i, eq in enumerate(eqs, 1):
        clean_eq = " ".join(eq.strip().split())
        print(f"  Eq ({i}): {clean_eq}")

    # 2. Check inline slash math
    print("\n[1.5.2 MATH NOTATION] Inline slash fractions ($.../...$):")
    maths = re.findall(r'\$([^$]+)\$', clean_text)
    slash_maths = [m.strip() for m in maths if '/' in m]
    for sm in slash_maths:
        # Check if units like Gb/s or actual math
        print(f"  ${sm}$")

    # 3. Check for any summation or integral in text
    print("\n[1.5.2 MATH NOTATION] Sums and Integrals:")
    sums_ints = [m.strip() for m in maths if any(k in m for k in [r'\sum', r'\int', r'\prod'])]
    if not sums_ints:
        print("  None found in inline math.")
    else:
        for si in sums_ints:
            print(f"  ${si}$")

    # 4. Acronyms & Abbreviations check
    print("\n[1.5.1 GENERAL NOTATION] Acronym check (First use analysis):")
    # Let's search for typical acronym patterns in the body text (excluding abstract and preamble)
    body_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', clean_text, re.DOTALL)
    if body_match:
        body = body_match.group(1)
    else:
        body = clean_text

    # Candidate acronyms (2 to 6 uppercase letters, possibly with digits or hyphens like SAC2M)
    raw_acronyms = re.findall(r'\b[A-Z][A-Z0-9\-]{1,5}[A-Z0-9]\b', body)
    
    # Common non-acronym words
    ignore = {
        'THE', 'AND', 'FOR', 'WITH', 'FROM', 'THIS', 'THAT', 'NOT', 'ARE', 'BUT', 'ALL',
        'CAN', 'HAS', 'HAD', 'WAS', 'ONE', 'TWO', 'NEW', 'FIG', 'REF', 'SEC', 'TAB',
        'TABLE', 'IEEE', 'USA', 'OFC', 'JLT', 'OSA', 'OPTICA', 'ALU', 'P1', 'P2', 'P3',
        'III', 'IV', 'VII', 'VIII', 'RMS', 'BER', 'SNR', 'DC', 'AC', 'TEM', 'TE', 'TM'
    }

    unique_acronyms = []
    for a in raw_acronyms:
        if a not in ignore and a not in unique_acronyms and not a.isdigit():
            unique_acronyms.append(a)

    for ac in unique_acronyms:
        # Check where it appears first and if it is defined (e.g., "Full Name (AC)" or "AC (Full Name)")
        pos = body.find(ac)
        snippet = body[max(0, pos-40):min(len(body), pos+len(ac)+40)].replace('\n', ' ')
        # Check if preceded or followed by parenthesis definition
        defined = False
        if f"({ac})" in body or f"({ac}," in body or f"({ac};" in body:
            defined = True
        print(f"  {ac:<10}: Defined with ({ac})? {defined} | First context: ...{snippet}...")
