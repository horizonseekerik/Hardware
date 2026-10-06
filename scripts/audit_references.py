import re
import sys
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')

papers = [
    ("Paper 1 (JANUS ALU)", "ofc_paper_latex/main.tex", "ofc_paper_latex/main.pdf"),
    ("Paper 2 (APD Receiver)", "ofc_apd_paper_latex/main.tex", "ofc_apd_paper_latex/main.pdf"),
    ("Paper 3 (Sb2S3 Switch)", "ofc_switch_paper_latex/main.tex", "ofc_switch_paper_latex/main.pdf")
]

print("="*75)
print("AUDITING REFERENCES: OPTICA STYLE GUIDE COMPLIANCE")
print("="*75)

for name, tex_path, pdf_path in papers:
    print(f"\n{'='*70}\n{name} ({tex_path})\n{'='*70}")
    with open(tex_path, 'r', encoding='utf-8') as f:
        tex = f.read()

    # Strip comments (ignoring escaped \%)
    lines = [re.split(r'(?<!\\)%', l)[0] for l in tex.splitlines()]
    clean_tex = "\n".join(lines)

    # 1. Extract bibitems or bibtex keys in bibliography order
    bib_keys = []
    # If using \bibitem
    bibitems = re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', clean_tex)
    if bibitems:
        bib_keys = bibitems
    else:
        # Check .bbl file if exists
        bbl_path = tex_path.replace('.tex', '.bbl')
        try:
            with open(bbl_path, 'r', encoding='utf-8') as bf:
                bbl_text = bf.read()
            bib_keys = re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', bbl_text)
        except Exception as e:
            print("  Could not read bbl file:", e)

    print(f"Total bibliography entries: {len(bib_keys)}")
    for idx, k in enumerate(bib_keys, 1):
        print(f"  [{idx}] {k}")

    # 2. Extract citations from body in order of appearance
    # Find all \cite{...} in document body
    doc_body = clean_tex
    if r'\begin{document}' in clean_tex:
        doc_body = clean_tex.split(r'\begin{document}')[1]
    if r'\begin{thebibliography}' in doc_body:
        doc_body = doc_body.split(r'\begin{thebibliography}')[0]
    elif r'\bibliography' in doc_body:
        doc_body = doc_body.split(r'\bibliography')[0]

    cite_matches = re.finditer(r'\\cite\{([^}]+)\}', doc_body)
    first_citation_order = []
    all_citations = []
    for m in cite_matches:
        raw_keys = [k.strip() for k in m.group(1).split(',')]
        all_citations.append((m.start(), raw_keys, m.group(0)))
        for k in raw_keys:
            if k not in first_citation_order:
                first_citation_order.append(k)

    print(f"\nOrder of first citation in body text ({len(first_citation_order)} unique keys cited):")
    citation_order_indices = []
    out_of_order = []
    expected_idx = 1
    for k in first_citation_order:
        if k in bib_keys:
            b_idx = bib_keys.index(k) + 1
            citation_order_indices.append(b_idx)
            print(f"  Cites: [{b_idx}] '{k}'")
            if b_idx != expected_idx:
                out_of_order.append((k, b_idx, expected_idx))
            expected_idx += 1
        else:
            print(f"  WARNING: Cited key '{k}' not found in bibliography!")

    if not out_of_order:
        print("  --> PASS: References appear strictly in the order in which they are referenced in the body!")
    else:
        print(f"  --> FAIL: References are OUT OF ORDER in body! Out of order cases: {out_of_order}")

    # 3. Check for multiple citations syntax and adjacent cites
    print("\nCheck multiple citations syntax:")
    adjacent_cites = re.findall(r'\\cite\{[^}]+\}\s*\\cite\{[^}]+\}', doc_body)
    if adjacent_cites:
        print(f"  WARNING: Found separate adjacent \\cite calls (should be merged into \\cite{{a,b}}):")
        for ac in adjacent_cites:
            print(f"    {ac}")
    else:
        print("  --> PASS: All multiple citations are correctly grouped in single \\cite{a,b} commands.")

    # 4. Check punctuation placement relative to citations
    # "followed by a comma or period"
    print("\nCheck citation punctuation placement:")
    # Look for punctuation immediately BEFORE \cite, e.g., ".\cite" or ",\cite"
    punct_before = re.findall(r'[.,;:][~ ]*\\cite\{[^}]+\}', doc_body)
    if punct_before:
        print(f"  WARNING: Found punctuation BEFORE \\cite ({len(punct_before)} instances):")
        for pb in punct_before:
            print(f"    {pb}")
    else:
        print("  --> PASS: Zero instances of punctuation before \\cite (no .[1] or ,[1]).")

    # 5. Check font size in bibliography
    print("\nCheck bibliography font size and formatting in LaTeX:")
    bib_font = re.findall(r'(?:\\fontsize\{([^}]+)\}\{([^}]+)\}|\\(footnotesize|scriptsize|small))\s*(?:\\selectfont)?.*?(?:\\begin\{thebibliography\}|\\BIBdecl)', clean_tex, re.DOTALL)
    print(f"  Configured bib font settings: {bib_font}")

    # Inspect rendered PDF text font size for bibliography
    doc = pymupdf.open(pdf_path)
    p3 = doc[-1] # last page
    # Search for "References" block
    blocks = p3.get_text("dict")["blocks"]
    ref_spans = []
    found_ref = False
    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    if "References" in s["text"]:
                        found_ref = True
                    elif found_ref:
                        ref_spans.append((s["text"][:30], s["size"], s["font"]))
    if ref_spans:
        print(f"  Rendered PDF font size for references on last page: {ref_spans[0][1]:.2f} pt (font: {ref_spans[0][2]})")
        print(f"  Sample span text: '{ref_spans[0][0]}...'")
