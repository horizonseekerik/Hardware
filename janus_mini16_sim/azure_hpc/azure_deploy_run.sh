#!/usr/bin/env bash
# ==============================================================================
# PROJECT JANUS MINI (16-TILE): AZURE HPC ONE-CLICK EXECUTION SCRIPT (100M)
# ==============================================================================
# Usage:
#   chmod +x azure_deploy_run.sh
#   ./azure_deploy_run.sh --cores 16 --samples 100000000 --bits 100000000
# ==============================================================================

set -euo pipefail

CORES=${1:-$(nproc)}
SAMPLES=${2:-100000000}
BITS=${3:-100000000}
OUTPUT_DIR="./azure_simulation_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

export OMP_NUM_THREADS=${CORES}

echo "========================================================================"
echo "  PROJECT JANUS: AZURE HPC FULL-CHIP MULTI-PHYSICS 100M RUNNER"
echo "  Detected Cores     : ${CORES}"
echo "  Monte Carlo Samples: ${SAMPLES}"
echo "  SPICE Cycles       : ${BITS}"
echo "  Output Directory   : ${OUTPUT_DIR}"
echo "  Timestamp          : ${TIMESTAMP}"
echo "========================================================================"

mkdir -p "${OUTPUT_DIR}/cloud_figures" "${OUTPUT_DIR}/logs"

# 1. Activate conda Meep MPI environment if present
if [ -d "/opt/conda/envs/pmp" ]; then
    echo "[*] Activating parallel Meep conda environment..."
    source /opt/conda/bin/activate pmp
fi

# 2. Run Tier 1: 3D Vectorial Optics & 100M Monte Carlo Sweep
echo "[*] Step 1: Running Tier 1 3D Optics Solvers (MPI & Tolerance)..."
python3 janus_mini16_sim/tier1_meep_optics/test_tier1_all.py

echo "[*] Step 1b: Running 100M Monte Carlo Tolerance Engine (${CORES} workers)..."
python3 janus_mini16_sim/tier1_meep_optics/monte_carlo_tolerance.py \
    --samples "${SAMPLES}" \
    --batch-size 1000000 \
    --parallel \
    --workers "${CORES}" \
    --export-graphs \
    --graph-dir "${OUTPUT_DIR}/cloud_figures" > "${OUTPUT_DIR}/logs/mc_100m.log" 2>&1

# 3. Run Tier 2: 3D Elmer FEM Thermal Stack
echo "[*] Step 2: Running Tier 2 3D Multi-Physics Thermal..."
python3 janus_mini16_sim/tier2_elmer_thermal/test_tier2_all.py

# 4. Run Tier 3: Parallel SPICE Latch & 100M-Cycle Eye Diagrams
echo "[*] Step 3: Running Tier 3 Receiver SPICE Dynamics (${CORES} workers)..."
python3 janus_mini16_sim/tier3_xyce_circuit/test_tier3_all.py

echo "[*] Step 3b: Running 100M-Cycle 100 GHz SPICE Solver..."
python3 janus_mini16_sim/tier3_xyce_circuit/eye_diagram_ber.py \
    --bits "${BITS}" \
    --chunk-size 250000 \
    --parallel \
    --workers "${CORES}" \
    --export-graphs \
    --graph-dir "${OUTPUT_DIR}/cloud_figures" > "${OUTPUT_DIR}/logs/spice_100m.log" 2>&1

# 5. Run Tier 4 & 5: CRT Verification and Full Workload Benchmark
echo "[*] Step 4: Running Full End-to-End Co-Simulation Pipeline..."
python3 janus_mini16_sim/run_mini16_full_cosim.py --verbose

# 6. Generate All 19 Publication Figures
echo "[*] Step 5: Generating Publication Figures (19 figures & OFC dashboards)..."
python3 janus_mini16_sim/cloud_hpc/cloud_graph_generator.py \
    --output-dir "${OUTPUT_DIR}/cloud_figures" \
    --samples "${SAMPLES}" \
    --cycles "${BITS}" > "${OUTPUT_DIR}/logs/cloud_graphs.log" 2>&1

echo "[*] Packaging all results into archive..."
tar -czvf "${OUTPUT_DIR}/janus_100m_results.tar.gz" -C "${OUTPUT_DIR}" cloud_figures logs

echo "========================================================================"
echo "  [SUCCESS] All multi-physics simulation tiers completed successfully!"
echo "  Results archived in: ${OUTPUT_DIR}/janus_100m_results.tar.gz"
echo "========================================================================"
