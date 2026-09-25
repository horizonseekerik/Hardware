# PROJECT JANUS: AZURE 100,000,000-RUN CLOUD HPC EXECUTION GUIDE
==============================================================================
**Document ID:** `JANUS-AZURE-100M-GUIDE-2026-V1`  
**Target Workload:** `100,000,000` Optical Monte Carlo + `100,000,000` SPICE Cycles  
**Estimated Budget:** `< $0.35` per 100M campaign run (from your **$200** Azure Credit)  
**Target Publication:** OFC 2027 / IEEE Journal of Lightwave Technology  
==============================================================================

---

## 1. Executive Summary

This guide provides step-by-step instructions to execute the **100,000,000-run production campaign** on Microsoft Azure Cloud Compute. The simulation suite executes:

1. **Tier 1 (3D Optics):** 100,000,000-sample stochastic foundry tolerance sweep across 13 MMI cascade stages ($1:8192$ split) and waveguide routing mesh ($32 \times 32$ crossing matrix).
2. **Tier 3 (SPICE Electronics):** 100,000,000-cycle $100\text{ GHz}$ optoelectronic StrongARM receiver dynamics, eye diagram persistence heatmap, and empirical bit-error-rate verification.
3. **5-Tier Co-Simulation:** Full-chip multi-physics decision tree sign-off ($16/16$ criteria passed).
4. **Cloud Visualization:** 19 publication-grade scientific figures (300-DPI PNG + vector PDF) and OFC 3-page composite dashboards.

---

## 2. Infrastructure & Cost Analysis

The simulation utilizes high-speed streaming vectorization and Chan's parallel variance reduction algorithm, capping memory consumption at **$< 1.5\text{ GB}$** and enabling high throughput ($> 300,000\text{ samples/s}$ per core).

| Azure VM Size | vCPU / RAM | Price / Hour | Est. 100M Runtime | Total Run Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Standard_F16s_v2** (Recommended) | 16 vCPU / 32 GB | ~$0.67 / hr | **15 - 20 min** | **~$0.22** |
| **Standard_D16s_v5** | 16 vCPU / 64 GB | ~$0.76 / hr | **15 - 20 min** | **~$0.25** |
| **Standard_D8s_v5** | 8 vCPU / 32 GB | ~$0.38 / hr | **30 - 35 min** | **~$0.22** |
| **Standard_HB120rs_v3** (Ultra HPC) | 120 vCPU / 456 GB | ~$3.60 / hr | **3 - 5 min** | **~$0.30** |
| **Standard_D4s_v5** (Fallback) | 4 vCPU / 16 GB | ~$0.19 / hr | ~60 - 75 min | ~$0.24 |

> **Budget Ceiling:** Even running multiple iterations, total cloud expenditure remains **$< $2.00**, leaving **$> $198.00** of your $200 Azure credit intact.

---

## 3. Pre-Requisites & Initial Setup

Ensure the Azure CLI is installed and authenticated:

```bash
# 1. Login to Microsoft Azure
az login

# 2. Check and set your active subscription (where the $200 credit is active)
az account list --output table
az account set --subscription "<YOUR_SUBSCRIPTION_ID_OR_NAME>"

# 3. Verify Azure CLI is operational
az group list -o table
```

---

## 4. One-Click Launch Workflow

To launch the campaign, navigate to the simulation directory and trigger the production orchestrator:

```bash
cd janus_mini16_sim

# Make deployment scripts executable
chmod +x azure_hpc/*.sh

# Launch the 100M production orchestrator
./azure_hpc/azure_production_orchestrator.sh
```

### What Happens Automatically:
1. **Resource Group Creation:** Provisions `janus-hpc-rg` in high-availability regions.
2. **Storage Provisioning:** Creates Azure Blob Storage container `results` and generates a 7-day secure SAS write token.
3. **VM Deployment with SKU Fallback:** Attempts deployment on `Standard_F16s_v2`, automatically falling back across `D16s_v5`, `D8s_v5`, `HB120rs_v3`, or `D4s_v5` across Indian (`centralindia`, `southindia`) and US regions (`eastus`, `centralus`).
4. **Hands-Free Background Execution:** The VM clones the repo, installs dependencies, runs the 100M Monte Carlo and 100M SPICE receiver simulations with multi-core parallelism, generates all 19 figures, compresses artifacts into `janus_100m_results.tar.gz`, uploads directly to Azure Storage, and **automatically executes `sudo shutdown -h now` to prevent any idle credit consumption**.

---

## 5. Monitoring Simulation Progress

You can monitor the running VM without maintaining an active SSH terminal:

```bash
# Check VM power state and provisioning
az vm get-instance-view --name <VM_NAME> --resource-group janus-hpc-rg --output table

# Check if results archive has been uploaded to Azure Blob
az storage blob list --container-name results --account-name <STORAGE_ACCOUNT> --output table
```

---

## 6. Downloading 100M Results & Figures

Once the VM completes its workload and powers down, run the download and verification script:

```bash
./azure_hpc/finish_and_upload.sh
```

This script will:
- Query the Azure storage account.
- Download `janus_100m_results.tar.gz` directly to your local workstation.
- Perform an integrity checksum and test unpack (`tar -tzf`).
- Unpack all 19 high-resolution figures in `output/cloud_figures/`.

---

## 7. Cleaning Up Cloud Resources

Once `janus_100m_results.tar.gz` is safely downloaded locally, delete the Azure resource group to eliminate storage retention charges:

```bash
az group delete --name janus-hpc-rg --yes --no-wait
```

---

## 8. Artifact Checklist

The downloaded `janus_100m_results.tar.gz` package contains:
- **Category A (Monte Carlo 100M):**
  - `fig_mc_convergence_vs_runs.png` / `.pdf`
  - `fig_mc_histogram_pdf_100m.png` / `.pdf`
  - `fig_mc_yield_cdf_semilog.png` / `.pdf`
  - `fig_mc_variance_decomposition.png` / `.pdf`
  - `fig_mc_process_window_2d.png` / `.pdf`
  - `fig_mc_cascaded_mmi_loss.png` / `.pdf`
  - `fig_mc_checkpoints_evolution.png` / `.pdf`
- **Category B (SPICE 100M):**
  - `fig_spice_100m_eye_density_heatmap.png` / `.pdf`
  - `fig_spice_ber_waterfall_curve.png` / `.pdf`
  - `fig_spice_strongarm_regen_histogram_100m.png` / `.pdf`
  - `fig_spice_jitter_distribution.png` / `.pdf`
  - `fig_spice_noise_psd_spectrum.png` / `.pdf`
  - `fig_spice_eye_checkpoints_evolution.png` / `.pdf`
- **Category C (Thermal 3D FEM & Foster RC):**
  - `fig_thermal_3d_stratum_slices.png` / `.pdf`
  - `fig_thermal_transient_step_5pole.png` / `.pdf`
  - `fig_thermal_lateral_crosstalk_decay.png` / `.pdf`
  - `fig_thermal_jir_clamping_dynamics.png` / `.pdf`
- **Category D (OFC 2027 Composite Dashboards):**
  - `fig_ofc_3page_hero_dashboard.png` / `.pdf`
  - `fig_ofc_radar_signoff_matrix.png` / `.pdf`
- **Simulation Logs:**
  - `mc_100m.log`
  - `spice_100m.log`
  - `full_cosim.log`
  - `cloud_graphs.log`
