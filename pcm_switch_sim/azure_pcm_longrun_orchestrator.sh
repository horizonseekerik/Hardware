#!/usr/bin/env bash
# ==============================================================================
# PROJECT JANUS: 1-TRILLION CYCLE PCM SWITCH AZURE CLOUD ORCHESTRATOR
# ==============================================================================
# Executes the long-duration 1-Trillion cycle Sb2S3 PCM switch simulation
# continuously in the background across available CPU cores/VMs.
#
# Usage:
#   chmod +x azure_pcm_longrun_orchestrator.sh
#   ./azure_pcm_longrun_orchestrator.sh --target 1000000000000 --node 0 --total-nodes 4
# ==============================================================================

set -euo pipefail

TARGET_CYCLES=1000000000000 # 1.0 Trillion cycles
NODE_ID=0
TOTAL_NODES=1
CORES=$(nproc)
STORAGE_ACCOUNT=""
STORAGE_CONTAINER="results"
CONFIG="trillion_superlattice"
CHECKPOINT_INTERVAL=300 # 5 minutes

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target) TARGET_CYCLES="$2"; shift 2 ;;
        --node) NODE_ID="$2"; shift 2 ;;
        --total-nodes) TOTAL_NODES="$2"; shift 2 ;;
        --cores) CORES="$2"; shift 2 ;;
        --config) CONFIG="$2"; shift 2 ;;
        --storage-account) STORAGE_ACCOUNT="$2"; shift 2 ;;
        --storage-container) STORAGE_CONTAINER="$2"; shift 2 ;;
        *) echo "[!] Unknown argument: $1"; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CP_DIR="${SCRIPT_DIR}/pcm_checkpoints"
OUT_DIR="${SCRIPT_DIR}/pcm_trillion_results"
LOG_FILE="${OUT_DIR}/simulation_pcm_node_${NODE_ID}.log"

mkdir -p "${CP_DIR}" "${OUT_DIR}"

echo "========================================================================"
echo "  PROJECT JANUS: 1-TRILLION CYCLE PCM SWITCH BACKGROUND RUNNER"
echo "  Configuration  : ${CONFIG}"
echo "  Global Target  : ${TARGET_CYCLES} Cycles (1 Trillion)"
echo "  Node Index     : ${NODE_ID} of ${TOTAL_NODES}"
echo "  Cores Assigned : ${CORES} vCPUs"
echo "  Log File       : ${LOG_FILE}"
echo "  Checkpoints    : ${CP_DIR}"
echo "========================================================================"

# 1. Performance CPU Governor Tuning
if [ "$(id -u)" -eq 0 ]; then
    echo "[*] Setting CPU scaling governor to performance..."
    for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        [ -f "$g" ] && echo "performance" > "$g" || true
    done
fi

# 2. Prevent duplicate execution
if pgrep -f "run_pcm_1trillion_azure_campaign.py.*--node-id ${NODE_ID}" > /dev/null; then
    echo "[!] Simulation is already actively running for Node ${NODE_ID}!"
    echo "[*] Monitor with: tail -f ${LOG_FILE}"
    exit 0
fi

# 3. Launch Simulation in background via nohup
echo "[*] Spawning 1-Trillion PCM simulation in background..."
nohup python3 "${SCRIPT_DIR}/run_pcm_1trillion_azure_campaign.py" \
    --target-cycles "${TARGET_CYCLES}" \
    --node-id "${NODE_ID}" \
    --total-nodes "${TOTAL_NODES}" \
    --cores "${CORES}" \
    --config "${CONFIG}" \
    --checkpoint-dir "${CP_DIR}" \
    --checkpoint-interval-s "${CHECKPOINT_INTERVAL}" \
    --export-dir "${OUT_DIR}" > "${LOG_FILE}" 2>&1 &

SIM_PID=$!
echo "[+] SUCCESS: Simulation launched with PID ${SIM_PID}!"
echo "${SIM_PID}" > "${OUT_DIR}/sim_pcm_node_${NODE_ID}.pid"

# 4. Background Sync Daemon to Azure Blob Storage (if storage account provided)
if [ -n "${STORAGE_ACCOUNT}" ]; then
    echo "[*] Starting background checkpoint sync daemon to ${STORAGE_ACCOUNT}/${STORAGE_CONTAINER}..."
    (
        while kill -0 "${SIM_PID}" 2>/dev/null; do
            sleep 900 # Sync every 15 minutes
            if command -v az > /dev/null; then
                TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
                ARCHIVE="${OUT_DIR}/pcm_cp_node_${NODE_ID}_${TIMESTAMP}.tar.gz"
                tar -czf "${ARCHIVE}" -C "${CP_DIR}" . 2>/dev/null || true
                if [ -f "${ARCHIVE}" ]; then
                    az storage blob upload \
                        --account-name "${STORAGE_ACCOUNT}" \
                        --container-name "${STORAGE_CONTAINER}" \
                        --name "pcm_checkpoints/$(basename "${ARCHIVE}")" \
                        --file "${ARCHIVE}" \
                        --overwrite true --output none 2>/dev/null || true
                    rm -f "${ARCHIVE}"
                fi
            fi
        done
        echo "[*] 1-Trillion simulation finished. Performing final upload..."
        if command -v az > /dev/null; then
            FINAL_ARCHIVE="${OUT_DIR}/pcm_1trillion_node_${NODE_ID}_final.tar.gz"
            tar -czf "${FINAL_ARCHIVE}" -C "${OUT_DIR}" . 2>/dev/null || true
            az storage blob upload \
                --account-name "${STORAGE_ACCOUNT}" \
                --container-name "${STORAGE_CONTAINER}" \
                --name "pcm_final/$(basename "${FINAL_ARCHIVE}")" \
                --file "${FINAL_ARCHIVE}" \
                --overwrite true --output none 2>/dev/null || true
        fi
    ) &
    SYNC_PID=$!
    echo "[+] Azure Blob sync daemon running with PID ${SYNC_PID}"
fi

echo "========================================================================"
echo "  [RUNNING IN BACKGROUND] Safe to close terminal or disconnect SSH."
echo "  To monitor progress live :"
echo "    tail -f ${LOG_FILE}"
echo "  To inspect latest checkpoint JSON:"
echo "    cat ${CP_DIR}/checkpoint_pcm_node_${NODE_ID}.json"
echo "========================================================================"
