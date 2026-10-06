import re, sys, os
import pymupdf as fitz

sys.stdout.reconfigure(encoding='utf-8')

tex_path = r'C:\Users\hp\Desktop\Optical interconnect\manuscript\OFC_2027_OMI_3PAGE_SUMMARY.tex'
pdf_path = r'C:\Users\hp\Desktop\Optical interconnect\manuscript\OFC_2027_OMI_3PAGE_SUMMARY.pdf'

print("="*75)
print("AUDITING OMI 3-PAGE SUMMARY (OFC_2027_OMI_3PAGE_SUMMARY.tex)")
print("="*75)

with open(tex_path, 'r', encoding='utf-8') as f:
    tex = f.read()

# Strip comments for clean body analysis
clean_tex_lines = []
for line in tex.splitlines():
    clean_line = re.split(r'(?<!\\)%', line)[0]
    clean_tex_lines.append(clean_line)
body_clean = "\n".join(clean_tex_lines)

# 1. Title, Author and Affiliation Check
print("\n--- 1. TITLE, AUTHOR & AFFILIATION ---")
title_m = re.search(r'\\textbf\{(Optical Memory Interconnect:[^}]+)\}', tex)
title_str = title_m.group(1).replace('\n', ' ').strip() if title_m else 'Not matched'
print(f"Title: \"{title_str}\"")

author = re.search(r'\\author\{([^}]+)\}', tex)
auth_str = author.group(1).replace(r'\authormark{1,*}', '').strip() if author else ''
first_initial_spelled = len(auth_str.split()[0]) > 1 if auth_str else False
print(f"Author: \"{auth_str}\" (Full first name spelled out: {first_initial_spelled})")

address = re.search(r'\\address\{([^}]+)\}', tex)
addr_str = address.group(1).replace(r'\authormark{1}', '').strip() if address else ''
print(f"Affiliation: \"{addr_str}\"")
has_full_address = any(c in addr_str for c in ['India', 'USA', 'Street', 'Road', 'PIN', 'Postal'])
print(f"  Complete postal info / Country included: {has_full_address}")

# 2. Abstract Word Count Check (Limit <= 35 words)
print("\n--- 2. ABSTRACT ---")
abs_m = re.search(r'\\textbf\{Abstract:\}\s*(.*?)(?=\\end\{minipage\})', tex, re.DOTALL)
abs_text = abs_m.group(1).strip() if abs_m else ''
clean_abs = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{([^}]*)\})?', r'\3', abs_text)
clean_abs = re.sub(r'[\$\\]', '', clean_abs)
words = clean_abs.split()
word_count = len(words)
print(f"Abstract Word Count: {word_count} words (Limit: <= 35) -> {'PASS' if word_count <= 35 else 'FAIL'}")
print(f"Abstract Text: \"{clean_abs}\"")

# 3. Copyright Statement Check
has_copyright = 'copyright' in abs_text.lower() or '©' in abs_text
print(f"\n--- 3. COPYRIGHT STATEMENT ---")
print(f"Copyright statement absent after abstract: {not has_copyright}")

# 4. Check consecutive callouts
print("\n--- 4. CONSECUTIVE CALLOUTS ---")
# Figures
fig_labels = re.findall(r'\\label\{(fig:[^}]+)\}', tex)
fig_refs = re.findall(r'(?:Fig\.|Figure)[~\s]*\\ref\{([^}]+)\}', body_clean)
fig_order = []
for r in fig_refs:
    if r not in fig_order:
        fig_order.append(r)
print(f"Figures consecutive callouts: {fig_order == fig_labels}")
print(f"  Figure Labels: {fig_labels}")
print(f"  Figure Order:  {fig_order}")

# Tables
tab_labels = re.findall(r'\\label\{(tab:[^}]+)\}', tex)
tab_refs = re.findall(r'(?:Table|Tab\.)[~\s]*\\ref\{([^}]+)\}', body_clean)
tab_order = []
for r in tab_refs:
    if r not in tab_order:
        tab_order.append(r)
print(f"Tables consecutive callouts: {tab_order == tab_labels}")
print(f"  Table Labels: {tab_labels}")
print(f"  Table Order:  {tab_order}")

# Equations
eq_labels = re.findall(r'\\label\{(eq:[^}]+)\}', tex)
# Check for \eqref or hardcoded (1)
eq_refs_macro = re.findall(r'(?:Eq\.|Equation)[~\s]*\\eqref\{([^}]+)\}', body_clean)
eq_refs_hard = re.findall(r'(?:equation|Eq\.|Equation)[~\s]*\((\d+)\)', body_clean)
print(f"Equations callouts:")
print(f"  Equation Labels: {eq_labels}")
print(f"  Macro callouts (\\eqref): {eq_refs_macro}")
print(f"  Hardcoded callouts (e.g. equation~(1)): {eq_refs_hard}")

# 5. References & In-Text Citations Audit
print("\n--- 5. REFERENCES & CITATIONS AUDIT ---")
# Extract references section
ref_sec_m = re.search(r'\\noindent\\textbf\{6\.\s*References\}(.*?)(?=\\end\{document\})', tex, re.DOTALL)
ref_sec_text = ref_sec_m.group(1).strip() if ref_sec_m else ''

# Extract bib items: \noindent [1] ... \\
ref_items = re.findall(r'\\noindent\s*\[(\d+)\]\s*(.*?)(?=\\noindent\s*\[\d+\]|\\end\{document\}|\Z)', ref_sec_text, re.DOTALL)
print(f"Total reference items in Section 6: {len(ref_items)}")
for num, content in ref_items:
    clean_c = content.replace('\\\\', '').strip()
    print(f"  [{num}] {clean_c[:90]}...")

# Extract in-text bracket citations: ~[1,2], ~[4--7], etc.
# Exclude math dimensions like 128 bytes, equation (1), etc.
in_text_cites = re.findall(r'(?:~|\s)\[([0-9,\s\-–]+)\]', body_clean[:body_clean.find(r'\textbf{6. References}')])
print(f"\nIn-text citation occurrences found ({len(in_text_cites)} total):")

# Decompose into sequential list of cited numbers
cite_sequence = []
two_cites = []
multi_cites = []
bad_formats = []

for c in in_text_cites:
    c_str = c.strip()
    # Check if range like 4--7 or 4–7 or comma like 1,2
    if '--' in c_str or '–' in c_str or '-' in c_str:
        multi_cites.append(f"[{c_str}]")
        dash = '--' if '--' in c_str else ('–' if '–' in c_str else '-')
        parts = [p.strip() for p in c_str.split(dash) if p.strip()]
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            for n in range(int(parts[0]), int(parts[1]) + 1):
                cite_sequence.append(str(n))
    elif ',' in c_str:
        parts = [p.strip() for p in c_str.split(',') if p.strip()]
        if len(parts) == 2:
            two_cites.append(f"[{c_str}]")
        else:
            multi_cites.append(f"[{c_str}]")
        for p in parts:
            if p.isdigit():
                cite_sequence.append(p)
    elif c_str.isdigit():
        cite_sequence.append(c_str)
    else:
        bad_formats.append(c_str)

first_seen_order = []
for n in cite_sequence:
    if n not in first_seen_order:
        first_seen_order.append(n)

print(f"Order of first citation appearance in body: {first_seen_order}")
expected_order = [str(i) for i in range(1, len(ref_items) + 1)]
is_strictly_ordered = (first_seen_order == expected_order)
print(f"Strict consecutive reference ordering [1..{len(ref_items)}]: {is_strictly_ordered} -> {'PASS' if is_strictly_ordered else 'FAIL'}")

print(f"\nMulti-citation formatting:")
print(f"  Two references cited together: {two_cites}")
print(f"  3+ consecutive references: {multi_cites}")

# Check punctuation placement before citation
punct_before = re.findall(r'([.,]\s*~?\[[0-9,\s\-–]+\])', body_clean[:body_clean.find(r'\textbf{6. References}')])
punct_before = [p for p in punct_before if not re.search(r'al\.\s*~?\[', p)]
print(f"\nPunctuation BEFORE citation (e.g. .[1]): {len(punct_before)}")
for p in punct_before:
    print(f"  Warning: {p}")

# 6. Journal Abbreviations in References
print("\n--- 6. JOURNAL ABBREVIATIONS IN OMI ---")
for num, content in ref_items:
    clean_c = content.replace('\\\\', '').strip()
    # Check journal/venue
    print(f"  [{num}] {clean_c}")

# 7. PDF Page Count & Layout Slack
print("\n--- 7. PDF PAGE COUNT & SLACK ---")
doc = fitz.open(pdf_path)
print(f"Total Pages: {len(doc)} pages (Limit: exactly 3) -> {'PASS' if len(doc) == 3 else 'FAIL'}")
for i, page in enumerate(doc):
    words = page.get_text('words')
    y1_max = max([w[3] for w in words]) if words else 0
    margin = 792 - y1_max
    print(f"  Page {i+1}: lowest content y1 = {y1_max:.2f} pt (Bottom margin: {margin:.2f} pt)")

# 8. Visual Line Endings
print("\n--- 8. VISUAL LINE ENDINGS ---")
bad_endings = []
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
        for op in ['=', '+', '-', '—', '–', '<', '>', '≤', '≥', '≈']:
            if last == op or (last.endswith(op) and len(last) > 1 and not last.startswith('(')):
                bad_endings.append((p_idx+1, op, line_str))
                break

print(f"Visual line endings ending with operator/dash: {len(bad_endings)}")
for p, op, l in bad_endings[:10]:
    print(f"  Page {p} (ends with '{op}'): {l}")
