import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

for path in ['ofc_paper_latex/main.tex', 'ofc_apd_paper_latex/main.tex', 'ofc_switch_paper_latex/main.tex']:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    print('Checking:', path)
    maths = re.findall(r'\$([^$]+)\$', content)
    for m in maths:
        if '/' in m:
            parts = m.split('/')
            for p in parts[1:]:
                p_clean = p.strip()
                if not p_clean.startswith('(') and not p_clean.startswith(r'\text') and not p_clean.startswith('{'):
                    tokens = p_clean.split()
                    if len(tokens) > 1:
                        # exclude units
                        if not any(u in tokens[0] for u in ['dB', 'cm', 'fF', 'aC', 'aJ', 'Gb', 'mV', 'ps', 'ns', 'W', 'K', 'cycle', 'cell', 'mol', 'stage', 'crossing', 'shifter', 'Box', 'MAC', 'mm']):
                            print('  Found:', m)
