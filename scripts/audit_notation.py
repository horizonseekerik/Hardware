import re, sys

sys.stdout.reconfigure(encoding='utf-8')

def audit_paper_notation(name, tex_path):
    print(f"\n=======================================================")
    print(f"AUDITING NOTATION FOR: {name} ({tex_path})")
    print(f"=======================================================")
    
    with open(tex_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    # Strip comments
    lines = [line.split('%')[0] for line in text.splitlines()]
    clean_text = '\n'.join(lines)
    
    # 1. Equations check
    print("\n--- 1.5.2 MATH NOTATION: EQUATIONS ---")
    eqs = re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}', clean_text, re.DOTALL)
    print(f"Total numbered equations: {len(eqs)}")
    for i, eq in enumerate(eqs, 1):
        has_label = bool(re.search(r'\\label\{eq:[^}]+\}', eq))
        eq_clean = re.sub(r'\\label\{[^}]+\}', '', eq).strip()
        print(f"  Eq ({i}): labeled={has_label} -> {eq_clean}")
    
    # Check for unnumbered displayed equations that might need numbering or centering
    dbl_dollar = re.findall(r'\$\$(.*?)\$\$', clean_text, re.DOTALL)
    if dbl_dollar:
        print(f"  WARNING: Found {len(dbl_dollar)} unnumbered display equations using $$...$$")
    else:
        print("  All display equations correctly use LaTeX \\begin{equation} ... \\end{equation}")

    # 2. Check inline fractions for ambiguity
    print("\n--- 1.5.2 MATH NOTATION: IN-LINE FRACTIONS ---")
    # Search for inline math expressions with slash
    inline_maths = re.findall(r'\$([^$]+)\$', clean_text)
    slash_instances = []
    for m in inline_maths:
        if '/' in m:
            slash_instances.append(m.strip())
    print(f"Total in-line math expressions with slashes: {len(slash_instances)}")
    
    # Check for potentially ambiguous slashes like A / B + C or A / B * C
    ambiguities = []
    for s in slash_instances:
        # Check if there is an unparenthesized addition/subtraction in denominator
        # e.g., / [a-zA-Z0-9]+ [+-] without parenthesis
        if re.search(r'/\s*[a-zA-Z0-9_]+(?:\s*[+\-]\s*[a-zA-Z0-9_]+)', s):
            ambiguities.append(s)
    if ambiguities:
        print(f"  POTENTIALLY AMBIGUOUS SLASHES FOUND ({len(ambiguities)}):")
        for a in ambiguities:
            print(f"    ${a}$")
    else:
        print("  All in-line slash fractions are properly parenthesized and unambiguous (e.g. 1/(n-1) or proper forms).")
        
    # 3. Check summations and integrals in text
    print("\n--- 1.5.2 MATH NOTATION: SUMS & INTEGRALS ---")
    sum_int = []
    for m in inline_maths:
        if any(op in m for op in [r'\sum', r'\int', r'\prod']):
            sum_int.append(m.strip())
    print(f"In-line sums/integrals/products found: {len(sum_int)}")
    for si in sum_int:
        has_limits = r'\limits' in si
        print(f"  ${si}$ -> limits forced above/below: {has_limits}")
        
    # 4. Check acronym definitions
    print("\n--- 1.5.1 GENERAL NOTATION: ACRONYMS ---")
    # Find capitalized words of 2-6 letters
    words = re.findall(r'\b[A-Z0-9]{2,6}\b', clean_text)
    # Filter common words or latex commands
    exclude = {'A', 'I', 'IN', 'ON', 'OR', 'AN', 'AT', 'BY', 'OF', 'TO', 'THE', 'AND', 'FOR', 'WITH', 'FROM',
               'FIG', 'TABLE', 'REF', 'EQ', 'CPO', 'BER', 'SNR', 'RMS', 'DC', 'AC', 'P1', 'P2', 'P3', 'WG'}
    acronyms = []
    for w in words:
        if w not in exclude and not w.isdigit():
            if w not in acronyms:
                acronyms.append(w)
    print(f"Identified acronyms: {acronyms[:25]}")
    
audit_paper_notation('Paper 1: JANUS ALU', 'ofc_paper_latex/main.tex')
audit_paper_notation('Paper 2: APD Receiver', 'ofc_apd_paper_latex/main.tex')
audit_paper_notation('Paper 3: Optical Switch', 'ofc_switch_paper_latex/main.tex')
