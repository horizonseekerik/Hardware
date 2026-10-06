import re, sys, os
import pymupdf as fitz

sys.stdout.reconfigure(encoding='utf-8')

targets = [
    {
        'name': 'JANUS (100-Gbaud Optical Fermat ALU)',
        'tex': r'ofc_paper_latex/main.tex',
        'pdf': r'ofc_paper_latex/main.pdf',
        'bib': r'ofc_paper_latex/references.bib',
        'bbl': r'ofc_paper_latex/build_output.bbl'
    },
    {
        'name': 'OMI (Optical Memory Interconnect)',
        'tex': r'C:\Users\hp\Desktop\Optical interconnect\manuscript\OFC_2027_OMI_3PAGE_SUMMARY.tex',
        'pdf': r'C:\Users\hp\Desktop\Optical interconnect\manuscript\OFC_2027_OMI_3PAGE_SUMMARY.pdf',
        'bib': None,
        'bbl': None
    }
]

print("="*80)
print("COMPREHENSIVE OPTICA STYLE & TECHNICAL AUDIT SUITE: JANUS vs. OMI")
print("="*80)

for item in targets:
    name = item['name']
    tex_path = item['tex']
    pdf_path = item['pdf']

    print(f"\n{'#'*80}")
    print(f"AUDITING: {name}")
    print(f"TeX File: {tex_path}")
    print(f"PDF File: {pdf_path}")
    print(f"{'#'*80}")

    if not os.path.exists(tex_path):
        print(f"ERROR: TeX file not found: {tex_path}")
        continue
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF file not found: {pdf_path}")
        continue

    with open(tex_path, 'r', encoding='utf-8') as f:
        raw_tex = f.read()

    # Clean TeX comments
    lines = [re.split(r'(?<!\\)%', l)[0] for l in raw_tex.splitlines()]
    clean_tex = "\n".join(lines)

    # -------------------------------------------------------------
    # TEST 1: AUTHOR & AFFILIATION
    # -------------------------------------------------------------
    print("\n--- [TEST 1] AUTHOR & AFFILIATION ---")
    author_m = re.search(r'\\author\{([^}]+)\}', clean_tex)
    author_str = author_m.group(1).strip() if author_m else 'None'
    # remove macros
    clean_author = re.sub(r'\\authormark\{[^}]*\}', '', author_str).strip()
    first_name = clean_author.split()[0] if clean_author else ''
    full_first_name = len(first_name) > 1 and not first_name.endswith('.')
    print(f"  Author Name: \"{clean_author}\" (Full first name: {full_first_name}) -> {'PASS' if full_first_name else 'FAIL'}")

    addr_m = re.search(r'\\address\{([^}]+)\}', clean_tex)
    addr_str = addr_m.group(1).strip() if addr_m else 'None'
    clean_addr = re.sub(r'\\authormark\{[^}]*\}', '', addr_str).strip()
    print(f"  Affiliation: \"{clean_addr}\"")

    email_m = re.search(r'\\email\{([^}]+)\}', clean_tex)
    email_str = email_m.group(1).strip() if email_m else 'None'
    print(f"  Email: \"{email_str}\"")

    # -------------------------------------------------------------
    # TEST 2: ABSTRACT WORD COUNT (<= 35 WORDS)
    # -------------------------------------------------------------
    print("\n--- [TEST 2] ABSTRACT WORD COUNT (LIMIT <= 35) ---")
    abs_m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', clean_tex, re.DOTALL)
    if not abs_m:
        abs_m = re.search(r'\\textbf\{Abstract:\}\s*(.*?)(?=\\end\{minipage\}|\n\n)', clean_tex, re.DOTALL)
    
    if abs_m:
        abs_text = abs_m.group(1).strip()
        # Clean latex macros & math
        clean_abs = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{([^}]*)\})?', r'\3', abs_text)
        clean_abs = re.sub(r'[\$\\]', '', clean_abs)
        abs_words = clean_abs.split()
        count = len(abs_words)
        print(f"  Abstract Word Count: {count} words -> {'PASS' if count <= 35 else 'FAIL'}")
        print(f"  Abstract Text: \"{clean_abs}\"")
    else:
        print("  WARNING: Could not parse abstract block.")

    # -------------------------------------------------------------
    # TEST 3: COPYRIGHT STATEMENT ABSENT
    # -------------------------------------------------------------
    print("\n--- [TEST 3] COPYRIGHT STATEMENT ---")
    has_copyright = 'copyright' in raw_tex.lower() and ('©' in raw_tex or 'optica publishing group' in raw_tex.lower())
    print(f"  Copyright statement absent after abstract: {not has_copyright} -> {'PASS' if not has_copyright else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 4: CONSECUTIVE CALLOUTS (FIGS, TABLES, EQUATIONS)
    # -------------------------------------------------------------
    print("\n--- [TEST 4] CONSECUTIVE CALLOUTS ---")
    body_part = clean_tex
    if r'\begin{document}' in clean_tex:
        body_part = clean_tex.split(r'\begin{document}')[1]

    # Figures
    fig_labels = re.findall(r'\\label\{(fig:[^}]+)\}', body_part)
    fig_calls = re.findall(r'(?:Fig\.|Figure)[~\s]*\\ref\{([^}]+)\}', body_part)
    ordered_fig_calls = []
    for f in fig_calls:
        if f not in ordered_fig_calls:
            ordered_fig_calls.append(f)
    fig_consec = (ordered_fig_calls == fig_labels)
    print(f"  Figures Consecutive: {fig_consec} -> {'PASS' if fig_consec else 'FAIL'}")
    print(f"    Labels declared: {fig_labels}")
    print(f"    Order of call:   {ordered_fig_calls}")

    # Tables
    tab_labels = re.findall(r'\\label\{(tab:[^}]+)\}', body_part)
    tab_calls = re.findall(r'(?:Table|Tab\.)[~\s]*\\ref\{([^}]+)\}', body_part)
    ordered_tab_calls = []
    for t in tab_calls:
        if t not in ordered_tab_calls:
            ordered_tab_calls.append(t)
    tab_consec = (ordered_tab_calls == tab_labels)
    print(f"  Tables Consecutive: {tab_consec} -> {'PASS' if tab_consec else 'FAIL'}")
    print(f"    Labels declared: {tab_labels}")
    print(f"    Order of call:   {ordered_tab_calls}")

    # Equations
    eq_labels = re.findall(r'\\label\{(eq:[^}]+)\}', body_part)
    eq_calls = re.findall(r'(?:Eq\.|Equation|equation)[~\s]*(?:\\eqref\{([^}]+)\}|\(?(\d+)\)?)', body_part)
    print(f"  Equations declared: {eq_labels}")

    # -------------------------------------------------------------
    # TEST 5: NOTATION & MATH (1.5.1 & 1.5.2)
    # -------------------------------------------------------------
    print("\n--- [TEST 5] NOTATION & MATH RULES (1.5.1 & 1.5.2) ---")
    # Centered display equations & numbered right
    disp_eqs = re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}', clean_tex, re.DOTALL)
    print(f"  Total display equations (\\begin{{equation}}): {len(disp_eqs)}")
    for idx, de in enumerate(disp_eqs, 1):
        de_clean = " ".join(de.strip().split())
        print(f"    Eq ({idx}): {de_clean}")

    # Check for unparenthesized compound denominators: / A + B or / A - B
    math_tokens = re.findall(r'\$([^$]+)\$', clean_tex)
    ambiguous_slash = []
    for m in math_tokens:
        if '/' in m:
            parts = m.split('/')
            for p in parts[1:]:
                p_clean = p.strip()
                if not p_clean.startswith('(') and not p_clean.startswith(r'\text') and not p_clean.startswith('{'):
                    tokens = p_clean.split()
                    if len(tokens) > 1:
                        if not any(u in tokens[0] for u in ['dB', 'cm', 'fF', 'aC', 'aJ', 'Gb', 'mV', 'ps', 'ns', 'W', 'K', 'cycle', 'cell', 'mol', 'stage', 'crossing', 'shifter', 'Box', 'MAC', 'mm']):
                            ambiguous_slash.append(m)
    print(f"  Ambiguous inline slash denominators: {len(ambiguous_slash)} -> {'PASS' if len(ambiguous_slash)==0 else 'FAIL'}")
    for a in ambiguous_slash:
        print(f"    Warning: ${a}$")

    # In-line summations / integrals with limits
    inline_sums = [m for m in math_tokens if any(op in m for op in [r'\sum', r'\int', r'\prod'])]
    print(f"  Inline sums/integrals: {len(inline_sums)}")
    for s in inline_sums:
        has_forced_limits = r'\limits' in s
        print(f"    ${s}$ (limits forced: {has_forced_limits})")

    # Acronyms first use check
    raw_acronyms = re.findall(r'\b[A-Z][A-Z0-9\-]{1,5}[A-Z0-9]\b', body_part)
    ignore_set = {'THE', 'AND', 'FOR', 'WITH', 'FROM', 'THIS', 'THAT', 'NOT', 'ARE', 'BUT', 'ALL',
                  'CAN', 'HAS', 'HAD', 'WAS', 'ONE', 'TWO', 'NEW', 'FIG', 'REF', 'SEC', 'TAB',
                  'TABLE', 'IEEE', 'USA', 'OFC', 'JLT', 'OSA', 'OPTICA', 'ALU', 'P1', 'P2', 'P3',
                  'III', 'IV', 'VII', 'VIII', 'RMS', 'BER', 'SNR', 'DC', 'AC', 'TEM', 'TE', 'TM', 'HPC'}
    acronyms = []
    for a in raw_acronyms:
        if a not in ignore_set and a not in acronyms and not a.isdigit():
            acronyms.append(a)
    print(f"  Sample defined acronyms in body: {acronyms[:15]}")

    # -------------------------------------------------------------
    # TEST 6: REFERENCES & CITATIONS (1.6)
    # -------------------------------------------------------------
    print("\n--- [TEST 6] REFERENCES & IN-TEXT CITATIONS (1.6) ---")
    # Check if bibliography is bibitem or bbl
    bib_entries = []
    if r'\bibitem' in clean_tex:
        bib_entries = re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', clean_tex)
    elif item['bbl'] and os.path.exists(item['bbl']):
        with open(item['bbl'], 'r', encoding='utf-8') as bf:
            bib_entries = re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', bf.read())
    elif r'\noindent [' in clean_tex:
        bib_entries = re.findall(r'\\noindent\s*\[(\d+)\]', clean_tex)

    print(f"  Total bibliography references: {len(bib_entries)}")

    # Extract citations in body text
    body_no_bib = clean_tex
    if r'\begin{thebibliography}' in body_no_bib:
        body_no_bib = body_no_bib.split(r'\begin{thebibliography}')[0]
    elif r'\noindent\textbf{6. References}' in body_no_bib:
        body_no_bib = body_no_bib.split(r'\noindent\textbf{6. References}')[0]
    elif r'\bibliography' in body_no_bib:
        body_no_bib = body_no_bib.split(r'\bibliography')[0]

    cite_sequence = []
    for m in re.finditer(r'\\cite\{([^}]+)\}', body_no_bib):
        for k in m.group(1).split(','):
            k = k.strip()
            if k not in cite_sequence:
                cite_sequence.append(k)

    # For OMI with hardcoded brackets
    if not cite_sequence:
        in_text_brackets = re.findall(r'(?:~|\s)\[([0-9,\s\-–]+)\]', body_no_bib)
        for b in in_text_brackets:
            dash = '--' if '--' in b else ('–' if '–' in b else ('-' if '-' in b else None))
            if dash:
                parts = [p.strip() for p in b.split(dash) if p.strip()]
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    for n in range(int(parts[0]), int(parts[1]) + 1):
                        if str(n) not in cite_sequence:
                            cite_sequence.append(str(n))
            elif ',' in b:
                for p in b.split(','):
                    p = p.strip()
                    if p.isdigit() and p not in cite_sequence:
                        cite_sequence.append(p)
            elif b.strip().isdigit() and b.strip() not in cite_sequence:
                cite_sequence.append(b.strip())

    # Verify sequential ordering 1..N
    if bib_entries and bib_entries[0].isdigit():
        expected_seq = [str(i) for i in range(1, len(bib_entries)+1)]
        in_order = (cite_sequence == expected_seq)
    else:
        # map keys to indices in bib_entries
        mapped_indices = [bib_entries.index(k)+1 for k in cite_sequence if k in bib_entries]
        expected_indices = list(range(1, len(bib_entries)+1))
        in_order = (mapped_indices == expected_indices)

    print(f"  References citation order strictly consecutive in body: {in_order} -> {'PASS' if in_order else 'FAIL'}")

    # Check punctuation before citation
    punct_before = re.findall(r'[.,;:][~ ]*\\cite\{[^}]+\}', body_no_bib)
    print(f"  Punctuation before citation (e.g. .\\cite): {len(punct_before)} -> {'PASS' if len(punct_before)==0 else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 7: SINGLE-AUTHOR PHRASING
    # -------------------------------------------------------------
    print("\n--- [TEST 7] SINGLE-AUTHOR PRONOUN AUDIT ---")
    # Search for "we", "our", "us" as standalone words (case-insensitive) in body
    we_matches = []
    for line_idx, line in enumerate(body_no_bib.splitlines(), 1):
        # find \bwe\b, \bour\b, \bus\b
        m = re.findall(r'\b(we|our|us|ourselves)\b', line, re.IGNORECASE)
        if m:
            we_matches.append((line_idx, m, line.strip()))
    print(f"  Plural first-person pronouns found: {len(we_matches)} -> {'PASS' if len(we_matches)==0 else 'FAIL'}")
    for l_num, words_found, l_text in we_matches:
        print(f"    Line {l_num} {words_found}: \"{l_text[:80]}...\"")

    # -------------------------------------------------------------
    # TEST 8: PDF PAGE BUDGET & SLACK
    # -------------------------------------------------------------
    print("\n--- [TEST 8] PDF PAGE COUNT & SLACK ---")
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    print(f"  Total PDF Pages: {page_count} (Limit: exactly 3) -> {'PASS' if page_count == 3 else 'FAIL'}")
    for p_idx, page in enumerate(doc):
        words = page.get_text('words')
        y1_max = max([w[3] for w in words]) if words else 0
        margin = 792 - y1_max
        print(f"    Page {p_idx+1}: lowest content y1 = {y1_max:.2f} pt (Bottom margin: {margin:.2f} pt)")

    # -------------------------------------------------------------
    # TEST 9: FIGURE / TEXT OVERLAP CHECK
    # -------------------------------------------------------------
    print("\n--- [TEST 9] FIGURE CLEARANCE & OVERLAP ---")
    # Verify subpanel labels and captions
    for p_idx, page in enumerate(doc):
        text_page = page.get_text('dict')
        captions = []
        sublabels = []
        for b in text_page['blocks']:
            if 'lines' in b:
                for l in b['lines']:
                    txt = ''.join(s['text'] for s in l['spans']).strip()
                    bbox = l['bbox']
                    if txt.startswith("Fig.") or txt.startswith("Figure") or "Architecture and Optical" in txt:
                        captions.append((bbox, txt))
                    elif txt in ["(a)", "(b)", "(c)"]:
                        sublabels.append((bbox, txt))

        for cb, ct in captions:
            for sb, st in sublabels:
                if abs(sb[3] - cb[1]) < 30:
                    dist = cb[1] - sb[3]
                    if dist < 0:
                        print(f"    Page {p_idx+1}: COLLISION between '{st}' and caption!")
                    else:
                        print(f"    Page {p_idx+1}: Sublabel '{st}' to caption clearance: {dist:.2f} pt -> PASS")

print("\n" + "="*80)
print("AUDIT SUITE COMPLETE")
print("="*80)
