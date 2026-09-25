"""
PROJECT JANUS: AZURE 100M CLOUD HPC READINESS VERIFICATION TEST SUITE
=====================================================================
Validates all components required for the 100,000,000-run Azure production campaign:
  1. Bash automation syntax integrity (azure_production_orchestrator.sh, finish_and_upload.sh, azure_deploy_run.sh)
  2. Tier 1 Monte Carlo tolerance engine 100M scaling, streaming batching, and parallel multiprocessing
  3. Tier 3 SPICE receiver solver 100M-cycle streaming moments and multi-worker execution
  4. CloudGraphGenerator 100M checkpoint definitions, decimation algorithms, and figure generation
  5. Docker container configuration and execution documentation completeness
"""

import os
import sys
import subprocess
import shutil
import pytest
import numpy as np

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from tier1_meep_optics.monte_carlo_tolerance import (
    MonteCarloFoundryToleranceEngine,
    MonteCarloFoundryTolerance100M,
    MonteCarloFoundryTolerance1M,
)
from tier3_xyce_circuit.eye_diagram_ber import (
    EyeDiagramAndBERSolver,
    MonteCarloSPICECycles100M,
    _merge_moments,
    _generate_prbs,
)
from cloud_hpc.cloud_graph_generator import (
    CloudGraphGenerator,
    MC_CHECKPOINT_INTERVALS_100M,
    SPICE_CHECKPOINT_INTERVALS_100M,
    MC_CHECKPOINT_INTERVALS_1M,
    SPICE_CHECKPOINT_INTERVALS_1M,
)


@pytest.fixture(scope="module")
def readiness_output_dir():
    """Temporary directory for test artifacts and figures."""
    out_dir = os.path.abspath(os.path.join(base_dir, "output", "test_azure_100m_readiness"))
    os.makedirs(out_dir, exist_ok=True)
    yield out_dir
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir, ignore_errors=True)


def test_azure_shell_scripts_syntax():
    """Validates that all Azure HPC bash automation scripts pass bash syntax verification (bash -n)."""
    scripts = [
        os.path.join(base_dir, "azure_hpc", "azure_production_orchestrator.sh"),
        os.path.join(base_dir, "azure_hpc", "finish_and_upload.sh"),
        os.path.join(base_dir, "azure_hpc", "azure_deploy_run.sh"),
    ]
    for script in scripts:
        assert os.path.exists(script), f"Script not found: {script}"
        # Validate syntax with bash -n
        res = subprocess.run(["bash", "-n", script], capture_output=True, text=True)
        assert res.returncode == 0, f"Syntax error in {script}:\n{res.stderr}"


def test_tier1_monte_carlo_100m_engine():
    """Verifies that the Tier 1 Monte Carlo tolerance engine supports 100M samples and parallel workers."""
    # Test initialization with 100M samples
    engine_100m = MonteCarloFoundryTolerance100M(n_samples=100_000_000)
    assert engine_100m.n_samples == 100_000_000
    assert 100_000_000 in engine_100m.checkpoint_intervals

    # Scaled execution with 2 parallel workers
    engine_test = MonteCarloFoundryToleranceEngine(n_samples=10_000)
    res = engine_test.run_simulation(
        batch_size=2_500,
        parallel=True,
        workers=2,
        quiet=True
    )
    assert res["n_samples"] == 10_000
    assert res["mean_margin_dB"] > 6.0
    assert res["sigma_3_margin_dB"] > 3.0
    assert res["yield_positive_pct"] == 100.0
    assert res["parallel"] is True
    assert res["num_workers"] == 2


def test_tier3_spice_100m_solver():
    """Verifies that the Tier 3 SPICE solver runs with parallel workers and streaming moments."""
    solver = MonteCarloSPICECycles100M()

    # Verify PRBS generation
    prbs = _generate_prbs(order=7, num_bits=500)
    assert len(prbs) == 500
    assert list(prbs[:127]) == list(prbs[127:254])

    # Scaled parallel simulation
    res = solver.run_simulation(
        num_bits=10_000,
        chunk_size=2_500,
        parallel=True,
        workers=2
    )
    assert res["num_bits_simulated"] == 10_000
    assert res["time_domain_Q"] >= 9.38
    assert res["eye_opening_pct"] >= 25.0
    assert res["BER_measured"] <= 1e-18
    assert res["pass_Q"] is True
    assert res["pass_eye_opening"] is True
    assert res["parallel"] is True
    assert res["num_workers"] == 2


def test_chan_parallel_variance_merging():
    """Verifies that Chan's exact moment merging algorithm computes identical variance to two-pass numpy."""
    np.random.seed(123)
    chunk_a = np.random.normal(5.0, 1.2, 5000)
    chunk_b = np.random.normal(5.2, 1.1, 7000)
    combined = np.concatenate([chunk_a, chunk_b])

    n_a, mu_a, m2_a = len(chunk_a), float(np.mean(chunk_a)), float(np.sum((chunk_a - np.mean(chunk_a))**2))
    n_b, mu_b, m2_b = len(chunk_b), float(np.mean(chunk_b)), float(np.sum((chunk_b - np.mean(chunk_b))**2))

    n_tot, mu_tot, m2_tot = _merge_moments(n_a, mu_a, m2_a, n_b, mu_b, m2_b)
    std_chan = np.sqrt(m2_tot / n_tot)

    assert n_tot == len(combined)
    assert np.isclose(mu_tot, np.mean(combined), atol=1e-10)
    assert np.isclose(std_chan, np.std(combined), atol=1e-10)


def test_cloud_graph_generator_100m_intervals(readiness_output_dir):
    """Verifies 100M checkpoint definitions and figure generation at large scales."""
    assert 100_000_000 in MC_CHECKPOINT_INTERVALS_100M
    assert 100_000_000 in SPICE_CHECKPOINT_INTERVALS_100M
    assert len(MC_CHECKPOINT_INTERVALS_100M) == 8
    assert len(SPICE_CHECKPOINT_INTERVALS_100M) == 6

    gen = CloudGraphGenerator(output_dir=readiness_output_dir)
    np.random.seed(42)
    # Test scaled 100M convergence plotting
    margins = np.random.normal(8.41, 0.42, 5_000)
    gen.generate_mc_convergence_plot(margins, [1_000, 5_000, 10_000_000, 100_000_000], total_samples=100_000_000)
    assert os.path.exists(os.path.join(readiness_output_dir, "fig_mc_convergence_vs_runs.png"))

    # Test 100M histogram and CDF
    gen.generate_mc_histogram_pdf_plot(margins)
    assert os.path.exists(os.path.join(readiness_output_dir, "fig_mc_histogram_pdf_1m.png"))

    gen.generate_mc_yield_cdf_plot(margins)
    assert os.path.exists(os.path.join(readiness_output_dir, "fig_mc_yield_cdf_semilog.png"))

    # Test SPICE 100M figures
    gen.generate_spice_2d_eye_density_heatmap(n_cycles=100_000_000)
    assert os.path.exists(os.path.join(readiness_output_dir, "fig_spice_100m_eye_density_heatmap.png"))

    gen.generate_spice_strongarm_regen_plot(n_cycles=100_000_000)
    assert os.path.exists(os.path.join(readiness_output_dir, "fig_spice_strongarm_regen_histogram_100m.png"))


def test_dockerfile_and_guide_completeness():
    """Verifies Dockerfile.azure_hpc and AZURE_100M_EXECUTION_GUIDE.md contain necessary configurations."""
    dockerfile_path = os.path.join(base_dir, "azure_hpc", "Dockerfile.azure_hpc")
    assert os.path.exists(dockerfile_path)
    with open(dockerfile_path, "r") as f:
        content = f.read()
    assert "OMP_NUM_THREADS" in content
    assert "OPENBLAS_NUM_THREADS" in content
    assert "pymeep-parallel" in content

    guide_path = os.path.join(base_dir, "azure_hpc", "AZURE_100M_EXECUTION_GUIDE.md")
    assert os.path.exists(guide_path)
    with open(guide_path, "r") as f:
        guide_text = f.read()
    assert "100,000,000" in guide_text
    assert "Standard_F16s_v2" in guide_text
    assert "janus_100m_results.tar.gz" in guide_text
