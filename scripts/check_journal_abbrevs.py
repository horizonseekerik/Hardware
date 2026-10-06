import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_journals(name, path):
    print(f"\n{'='*60}\n{name} ({path})\n{'='*60}")
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # If bibtex (.bbl)
    if 'ofc_paper_latex' in path:
        bbl_path = 'ofc_paper_latex/main.bbl'
        with open(bbl_path, 'r', encoding='utf-8') as bf:
            bbl = bf.read()
        items = re.findall(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})', bbl, re.DOTALL)
        for k, content in items:
            j = re.findall(r'\\emph\{([^}]+)\}', content)
            print(f"  [{k}]: Journal/Venue = {j}")
    else:
        items = re.findall(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})', text, re.DOTALL)
        for k, content in items:
            j = re.findall(r'\\textit\{([^}]+)\}', content)
            print(f"  [{k}]: Journal/Venue = {j}")

check_journals("Paper 1 (JANUS ALU)", "ofc_paper_latex/main.tex")
check_journals("Paper 2 (APD Receiver)", "ofc_apd_paper_latex/main.tex")
check_journals("Paper 3 (Sb2S3 Switch)", "ofc_switch_paper_latex/main.tex")
