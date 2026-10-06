import re, sys
import pymupdf as fitz

sys.stdout.reconfigure(encoding='utf-8')

papers = [
    ('Paper 1 (JANUS ALU)', 'ofc_paper_latex/main.tex', 'ofc_paper_latex/main.pdf'),
    ('Paper 2 (APD Receiver)', 'ofc_apd_paper_latex/main.tex', 'ofc_apd_paper_latex/main.pdf'),
    ('Paper 3 (Sb2S3 Switch)', 'ofc_switch_paper_latex/main.tex', 'ofc_switch_paper_latex/main.pdf')
]

print('======================================================================')
print('COMPREHENSIVE OPTICA CONFERENCE STYLE & PUBLICATION CHECKLIST AUDIT')
print('======================================================================\n')

for name, tex_path, pdf_path in papers:
    print(f'*** {name} ***')
    with open(tex_path, 'r', encoding='utf-8') as f:
        tex = f.read()
    
    # 1. Author and Affiliation Check
    author = re.search(r'\\author\{([^}]+)\}', tex)
    auth_str = author.group(1).replace(r'\authormark{1,*}', '').strip() if author else ''
    first_initial_spelled = len(auth_str.split()[0]) > 1
    print(f'1. Author: "{auth_str}" (Full first name spelled out: {first_initial_spelled})')
    
    address = re.search(r'\\address\{([^}]+)\}', tex)
    addr_str = address.group(1).replace(r'\authormark{1}', '').strip() if address else ''
    print(f'   Affiliation: "{addr_str}"')
    
    # 2. Abstract Word Count Check (Limit <= 35 words)
    abs_m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.DOTALL)
    abs_text = abs_m.group(1).strip() if abs_m else ''
    clean_abs = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{([^}]*)\})?', r'\3', abs_text)
    clean_abs = re.sub(r'[\$\\]', '', clean_abs)
    words = clean_abs.split()
    word_count = len(words)
    print(f'2. Abstract word count: {word_count} words (Limit: <= 35) -> {"PASS" if word_count <= 35 else "FAIL"}')
    print(f'   Text: "{clean_abs}"')
    
    # 3. Copyright Statement Check (Must NOT be present after abstract)
    has_copyright = 'copyright' in abs_text.lower() or '©' in abs_text
    print(f'3. Copyright statement after abstract absent: {not has_copyright}')
    
    # 4. Check consecutive callouts
    # Figures
    fig_labels = re.findall(r'\\label\{(fig:[^}]+)\}', tex)
    fig_refs = re.findall(r'(?:Fig\.|Figure)[~\s]*\\ref\{([^}]+)\}', tex)
    fig_order = []
    for r in fig_refs:
        if r not in fig_order:
            fig_order.append(r)
    figs_consec = fig_order == fig_labels
    print(f'4. Figures consecutive callouts: {figs_consec} (Labels: {fig_labels}, Order: {fig_order})')
    
    # Tables
    tab_labels = re.findall(r'\\label\{(tab:[^}]+)\}', tex)
    tab_refs = re.findall(r'(?:Table|Tab\.)[~\s]*\\ref\{([^}]+)\}', tex)
    tab_order = []
    for r in tab_refs:
        if r not in tab_order:
            tab_order.append(r)
    tabs_consec = tab_order == tab_labels
    print(f'   Tables consecutive callouts: {tabs_consec} (Labels: {tab_labels}, Order: {tab_order})')
    
    # Equations
    eq_labels = re.findall(r'\\label\{(eq:[^}]+)\}', tex)
    eq_refs = re.findall(r'(?:Eq\.|Equation)[~\s]*\\eqref\{([^}]+)\}', tex)
    eq_order = []
    for r in eq_refs:
        if r not in eq_order:
            eq_order.append(r)
    eqs_consec = eq_order == eq_labels
    print(f'   Equations consecutive callouts: {eqs_consec} (Labels: {eq_labels}, Order: {eq_order})')
    
    # PDF Page count
    doc = fitz.open(pdf_path)
    pages = len(doc)
    print(f'5. PDF Page count: {pages} pages (Limit: exactly 3) -> {"PASS" if pages == 3 else "FAIL"}\n')
