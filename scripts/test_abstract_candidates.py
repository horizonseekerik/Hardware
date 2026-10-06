import re, sys

sys.stdout.reconfigure(encoding='utf-8')

def count_words(text):
    # Strip basic LaTeX markup
    clean = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{([^}]*)\})?', r'\3', text)
    clean = re.sub(r'[\$\\]', '', clean)
    clean = clean.replace('~', ' ')
    simple = clean.split()
    strict = re.findall(r'[a-zA-Z0-9]+', clean)
    return len(simple), len(strict), clean

p1_cands = [
    "A 100-Gbaud Fermat-prime optical core bypasses ADCs via binary latching. Cloud HPC and SPICE verify +7.1-dB margin and zero errors across 100M cycles.",
    "Bypassing ADCs via Fermat modular optics, a 100-Gbaud processor achieves +7.1-dB link margin and error-free SPICE operation across 100M cycles.",
    "A 100-Gbaud Fermat optical processor replaces ADCs with binary latching, achieving +7.1-dB margin and error-free operation over 100M cycles."
]

p2_cands = [
    "Directly coupling a 105-GHz APD to a 7-nm StrongARM latch eliminates TIAs, achieving 95-aJ/bit energy and 0.12-dB drift across $3.16\\times 10^{19}$ cycles via auto-zero trimming.",
    "A TIA-free receiver couples a 105-GHz APD directly to a 7-nm StrongARM latch, achieving 95-aJ/bit energy and 0.12-dB penalty over $10^{19}$ cycles via auto-zero trimming.",
    "Directly coupling a 105-GHz APD to a StrongARM latch eliminates TIAs, yielding 95-aJ/bit energy and 0.12-dB drift across $10^{19}$ cycles via auto-zero calibration.",
    "Eliminating TIAs, a 105-GHz APD directly drives a StrongARM latch at 95-aJ/bit energy, with auto-zero trimming limiting drift across $10^{19}$ cycles to 0.12 dB."
]

p3_cands = [
    "A non-volatile Sb2S3 directional coupler achieves 0.057-dB insertion loss and 22.1-dB extinction ratio. Multiphysics models verify $10^8$ cycles; superlattice engineering projects $>10^{12}$ cycles.",
    "A non-volatile Sb2S3 directional coupler provides 0.057-dB loss and 22.1-dB extinction. Multiphysics verifies $10^8$ cycles, with superlattice hardening projecting $>10^{12}$ cycles.",
    "An Sb2S3 directional-coupler switch achieves 0.057-dB insertion loss and 22.1-dB extinction. Multiphysics confirms $10^8$ cycles, with superlattice hardening projecting $>10^{12}$ cycles."
]

print("=== PAPER 1 CANDIDATES ===")
for c in p1_cands:
    s, st, cl = count_words(c)
    print(f"Simple={s:2d}, Strict={st:2d} | {cl}")

print("\n=== PAPER 2 CANDIDATES ===")
for c in p2_cands:
    s, st, cl = count_words(c)
    print(f"Simple={s:2d}, Strict={st:2d} | {cl}")

print("\n=== PAPER 3 CANDIDATES ===")
for c in p3_cands:
    s, st, cl = count_words(c)
    print(f"Simple={s:2d}, Strict={st:2d} | {cl}")
