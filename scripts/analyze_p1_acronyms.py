import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('ofc_paper_latex/main.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's see the text between \maketitle and \begin{thebibliography}
body = text.split(r'\end{abstract}')[1].split(r'\begin{thebibliography}')[0]

# List of acronyms to check
acronyms = [
    'TIA', 'ADC', 'HPC', 'SPICE', 'RNS', 'DR', 'CMOS', 'CRT', 'HBT', 'RZ', 'MMI',
    'ER', 'PVT', 'MPI', 'APD', 'SAC', 'PRBS', 'ODE', 'RIN', 'RDF', 'DAC', 'CML',
    'PEX', 'JIR', 'GDS', 'CPW', 'LC', 'WPE', 'INT4', 'PMAC', 'TMAC', 'MAC', 'INT64',
    'PRNS', 'AI', 'TOPS', 'INT8', 'BEOL'
]

print("=== PAPER 1 ACRONYMS ===")
for ac in acronyms:
    # find all occurrences
    matches = list(re.finditer(r'\b' + re.escape(ac) + r'\b', body))
    if not matches:
        print(f"{ac}: Not found in body")
        continue
    first_m = matches[0]
    start = max(0, first_m.start() - 60)
    end = min(len(body), first_m.end() + 60)
    snip = body[start:end].replace('\n', ' ')
    print(f"{ac} ({len(matches)} occurrences):")
    print(f"   First occurrence: ...{snip}...")
