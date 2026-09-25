"""
Automated Pytest Suite for First-Principles Power & Physical Area Calculator.
Verifies device-level mathematical derivations, zero-base component counts,
and physical footprint conservation across both strata of Project Janus Mini-16.
"""

import os
import sys
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from benchmarks.first_principles_power_and_area import (
    FirstPrinciplesPowerAndAreaAnalyzer,
    run_first_principles_audit,
)


def test_first_principles_power_calculation():
    """Verifies that power calculations strictly adhere to first-principles device physics."""
    analyzer = FirstPrinciplesPowerAndAreaAnalyzer(activity_factor=1.0)
    res = analyzer.calculate_power()

    assert res["activity_factor"] == 1.0
    assert res["total_power_mW"] > 3000.0  # Total chip power ~3.25 W
    assert res["total_power_W"] == pytest.approx(3.25, abs=0.05)

    subsystems = res["subsystems_mW"]
    # Laser: 2.21 W opt / 0.75 WPE = 2.9467 W elec = 2946.67 mW
    assert subsystems["Optical Source"] == pytest.approx(2946.67, rel=1e-2)

    # 512x LiTaO3 modulators: capacitive lumped drive = 36.86 mW
    assert subsystems["Electro-Optics"] == pytest.approx(36.86, rel=1e-2)

    # SAC2M APDs: receiverless gate charge = 37.91 mW
    assert subsystems["Optoelectronics"] == pytest.approx(37.91, rel=1e-2)

    # 65nm CMOS digital logic
    assert subsystems["65nm CMOS Digital"] > 150.0  # Latches, Deser, SIMD, CSA, Clock

    # 1.5 MB SRAM & Central ROM
    assert subsystems["65nm CMOS Memory"] == pytest.approx(59.4, rel=1e-2)

    # Verify all individual components have non-negative power
    for comp in res["components"]:
        assert comp["total_power_mW"] >= 0.0
        assert comp["unit_count"] >= 1
        assert len(comp["derivation_notes"]) > 0


def test_first_principles_power_scaling():
    """Verifies dynamic power scaling across different activity factors."""
    p_0 = FirstPrinciplesPowerAndAreaAnalyzer(activity_factor=0.0).calculate_power()
    p_50 = FirstPrinciplesPowerAndAreaAnalyzer(activity_factor=0.5).calculate_power()
    p_100 = FirstPrinciplesPowerAndAreaAnalyzer(activity_factor=1.0).calculate_power()

    # Laser & thermal sensing are continuous; dynamic logic scales
    assert p_0["total_power_mW"] < p_50["total_power_mW"] < p_100["total_power_mW"]
    assert p_0["total_power_mW"] >= 2946.0  # Laser remains on


def test_first_principles_area_calculation():
    """Verifies zero-base physical area calculations and die footprint conservation."""
    analyzer = FirstPrinciplesPowerAndAreaAnalyzer()
    res = analyzer.calculate_area()

    # Die dimensions: 10.0 mm x 10.0 mm = 100.0 mm^2
    assert res["total_die_area_mm2"] == pytest.approx(100.00, abs=1e-3)
    assert res["die_dimensions_mm"] == "10.00 x 10.00"

    # Active 16-tile core array: 16 * (2500 um x 2500 um) = 100.0 mm^2 (100.0%)
    assert res["tile_array_core_mm2"] == pytest.approx(100.0, abs=1e-3)
    assert res["tile_array_core_pct"] == pytest.approx(100.0, abs=0.1)

    # Verify individual component counts and areas
    comp_map = {c["name"]: c for c in res["components"]}

    # Optical stratum components
    assert comp_map["Talbot 1:2 MMI Splitters"]["unit_count"] == 8191
    assert comp_map["LiTaO3 Pockels Modulator Envelopes"]["unit_count"] == 512
    assert comp_map["Sb2S3 Directional Coupler Switches"]["unit_count"] == 122880
    assert comp_map["Talbot-Focused Waveguide Crossings"]["unit_count"] == 16384
    assert comp_map["SAC2M Ge/Si APD Mesas & Contacts"]["unit_count"] == 8192
    assert comp_map["Vertical Cu TDV Pillars (8 um diam)"]["unit_count"] == 8192
    assert comp_map["2nd-Order Si3N4 Grating Couplers"]["unit_count"] == 32

    # CMOS base stratum components
    assert comp_map["16x Active Tile Core Modules (65nm CMOS)"]["unit_count"] == 16
    assert comp_map["1.5 MB Central ROM & JIR FSM Macro"]["unit_count"] == 1
    assert comp_map["Wire-Bond & Micro-Bump I/O Pad Array"]["unit_count"] == 64


def test_export_reports(tmp_path):
    """Verifies that markdown and JSON reports export cleanly."""
    analyzer = FirstPrinciplesPowerAndAreaAnalyzer(activity_factor=1.0)
    reports = analyzer.export_report(output_dir=str(tmp_path))

    assert os.path.exists(reports["json_path"])
    assert os.path.exists(reports["md_path"])

    with open(reports["json_path"], "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["power_audit"]["total_power_W"] > 3.0
        assert data["area_audit"]["total_die_area_mm2"] == 100.0

    with open(reports["md_path"], "r", encoding="utf-8") as f:
        content = f.read()
        assert "Project Janus Mini (16-Tile): First-Principles Power & Area Audit" in content
        assert "100.0 mm²" in content or "100.00 mm²" in content
        assert "Talbot 1:2 MMI Splitters" in content


def test_run_first_principles_audit():
    """Verifies the top-level convenience runner."""
    res = run_first_principles_audit(activity_factor=1.0)
    assert "power" in res
    assert "area" in res
    assert "reports" in res
    assert res["power"]["total_power_W"] > 0
    assert res["area"]["total_die_area_mm2"] == 100.0
