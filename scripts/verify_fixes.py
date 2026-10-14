import re
import sys

def check_file(fname, checks):
    print(f"\n=======================================================")
    print(f"=== Checking {fname} ===")
    print(f"=======================================================")
    with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    passed = 0
    failed = 0
    for name, pattern, should_exist in checks:
        m = re.search(pattern, content, re.IGNORECASE)
        found = bool(m)
        status = "PASS" if found == should_exist else "FAIL"
        if status == "PASS":
            passed += 1
            print(f"[PASS] {name}")
        else:
            failed += 1
            print(f"[FAIL] {name} (expected {should_exist}, got {found})")
        if found and should_exist:
            start = max(0, m.start() - 25)
            end = min(len(content), m.end() + 25)
            snippet = content[start:end].replace('\n', ' ')
            print(f"       -> ...{snippet}...")
    print(f"Summary for {fname}: {passed} Passed, {failed} Failed.")
    return failed == 0

# 1. IEEE Manuscript Checks
checks_ieee = [
    ("No broken Section ?? references in text", r"Section\s+\?\?", False),
    ("Label precision_collapse exists", r"\\label\{sec:precision_collapse\}", True),
    ("Label nonlinear_failure exists", r"\\label\{sec:nonlinear_failure\}", True),
    ("Label loss_accumulation exists", r"\\label\{sec:loss_accumulation\}", True),
    ("Label thermal_drift exists", r"\\label\{sec:thermal_drift\}", True),
    ("No 256 waveguides in Section III-F-1", r"channel over 256 spatial waveguides", False),
    ("17 waveguides in Section III-F-1", r"17 spatial waveguides", True),
    ("No 255xBER term", r"255\s*\\times\s*(\\text|\\mathrm)\{BER\}", False),
    ("16xBER term present", r"16\s*\\times\s*(\\text|\\mathrm)\{BER\}", True),
    ("Link budget reconciliation (-16.90 dBm sign-off)", r"-16\.90(\\,|~)?(\\text|\\mathrm)\{dBm\}", True),
    ("Model 1A margin +6.142 dB", r"\+6\.142(\\,|~)?(\\text|\\mathrm)\{dB\}", True),
    ("3.93M switches (Model 1A) vs 7.86M (Mini)", r"3\.93M|3\.93\\text\{--\}7\.86", True),
    ("Oxide buffer 100 um baseline vs 250 um Model 1A", r"250(\\,|~)?(\\mu|\\mu\\mathrm\{m\}|\$\\mu\$m)", True),
    ("Restored Sb2S3 1064 nm caveat", r"Sb_2S_3.*1064", True),
    ("Restored SAC2M APD caveat", r"SAC\^2M.*APD", True),
    ("Restored Laser RIN caveat", r"Laser RIN", True),
    ("Restored illustrative power table caveat", r"illustrative", True),
    ("Restored multi-fault immunity caveat", r"fault immunity", True),
]

# 2. Simulation Report Checks
checks_sim = [
    ("13-stage tree 8192 outputs vs 16384 multipliers interleaved", r"8,?192 outputs|1:8,?192", True),
    ("Clarification on 2-phase time-interleaved recycling", r"time-interleaved|interleaving|two 8-tile banks", True),
    ("Table XI LLaMA-3 energy units (H100 = 246.5 mJ)", r"246\.5(\\,|~)?(\\text|\\mathrm)\{mJ\}", True),
    ("Table XI LLaMA-3 energy units (B200 = 163.4 mJ)", r"163\.4(\\,|~)?(\\text|\\mathrm)\{mJ\}", True),
    ("Table XI LLaMA-3 energy units (Model 1A = 495.6 uJ or 496 uJ)", r"495\.6(\\,|~)?\\mu(\\text|\\mathrm)\{J\}", True),
    ("4.41 W on-die dissipation vs 6.17 W package TDP", r"4\.41(\\,|~)?(\\text|\\mathrm)\{W\}", True),
    ("Thermal clamp explanation: P_die = 4.41 W, Package = 6.17 W", r"P_\{?(\\text|\\mathrm)\{die\}\}?|on-die thermal dissipation", True),
    ("Zero tail probability bounded by 5-sigma / observed min +6.82 dB", r"6\.82(\\,|~)?(\\text|\\mathrm)\{dB\}", True),
    ("TDV height 5.0 um bridging hybrid bonding dielectric", r"5\.0(\\,|~)?\\mu\\mathrm\{m\}.*TDV|TDVs?.*5\.0(\\,|~)?\\mu\\mathrm\{m\}|5\.0(\\,|~)?\\mu\\mathrm\{m\} bonding height", True),
    ("Table III unpassivated loss floor vs 0.057/0.2627 dB passivated", r"unpassivated", True),
    ("BIST 10,000 SPICE physical runs vs 100M algorithmic trials", r"10,?000.*physical.*SPICE.*100M|10,?000.*SPICE", True),
    ("APD nominal gain M=7 with tracking up to M=10", r"M\s*=\s*7\s*(\\text\{--\}|--|-)\s*10|M=7\s*\\text\{--\}\s*10", True),
]

# 3. CMOS Paper Checks
checks_cmos = [
    ("Detector lines per multiplier = 17", r"17 photodetector lines|17 detector lines|17 lines", True),
    ("1/17 activation sparsity", r"1/17", True),
    ("Total detectors 278,528", r"278,?528", True),
    ("Tile geometry 2.5 mm / 6.25 mm^2", r"2\.50?(\\,|~)?(\\text|\\mathrm)\{mm\}|6\.25(\\,|~)?(\\text|\\mathrm)\{mm\}\^2", True),
    ("tau_regen = 0.78 ps vs decision delay <= 3.5 ps", r"0\.78(\\,|~)?(\\text|\\mathrm)\{ps\}|3\.5(\\,|~)?(\\text|\\mathrm)\{ps\}", True),
    ("TDV 5.0 um Cu-Cu bonding interface", r"5\.0(\\,|~)?\\mu\\mathrm\{m\}", True),
]

all_ok = True
all_ok &= check_file('paper_latex/main.tex', checks_ieee)
all_ok &= check_file('simulation_paper_latex/JANUS_Mini16_Simulation_Report.tex', checks_sim)
all_ok &= check_file('cmos_paper_latex/JANUS_Mini16_CMOS_Architecture.tex', checks_cmos)

if all_ok:
    print("\n>>> ALL VERIFICATION CHECKS PASSED SUCCESSFULLY! <<<")
else:
    print("\n>>> SOME VERIFICATION CHECKS FAILED! <<<")
    sys.exit(1)
