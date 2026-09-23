"""
MEEP FDTD SIMULATION: DECOUPLED 1x2 MZI SWITCH (CANDIDATES 1 & 2)
================================================================
Architecture:
  - Input: 1x2 MMI 3dB Splitter (W = 1.20 um, L = 2.40 um)
  - Decoupled Phase Arms (Gap = 349 nm, prevents inter-modal scattering):
      * Upper Arm (y = +0.334 um): Active phase shifter (L_pi = 3.68 - 3.94 um)
      * Lower Arm (y = -0.334 um): Passive reference waveguide
      * Fixed bias offset Delta_L0 = 93 nm (pi/2) for full constructive routing
  - Output: 2x2 MMI 3dB Combiner (W = 1.20 um, L = 3.20 um)
  - Output Ports: Port 1 (Top, y = +0.334 um) and Port 2 (Bottom, y = -0.334 um)
"""

import math
import sys
import numpy as np
import meep as mp

LAMBDA_0 = 1.064
FCEN = 1.0 / LAMBDA_0
DF = 0.08 * FCEN

N_CLAD = 1.449
N_CORE = 2.850  # Fundamental TE slab effective index

DPML = 0.8
RESOLUTION = 40  # 40 pixels/um (25 nm grid)
L_LEAD = 1.20   # Port leads

def simulate_mzi_candidate(name, l_arm, delta_n_patch, k_am=1e-5, k_cr=1.8e-4):
    print("\n" + "=" * 80)
    print(f"RUNNING FULL-WAVE MEEP FDTD FOR DECOUPLED 1x2 MZI: {name}")
    print(f"Arm Length L_pi = {l_arm:.2f} um, Index Perturbation Delta_n = {delta_n_patch:.4f}")
    print("=" * 80)
    
    w_mmi = 1.20
    l_mmi_in = 2.40
    l_mmi_out = 3.20
    w_port = 0.320
    y_sep = 0.668
    y_top =  y_sep / 2.0  # +0.334 um
    y_bot = -y_sep / 2.0  # -0.334 um
    
    # Total device length
    l_total = l_mmi_in + l_arm + l_mmi_out
    sx = l_total + 2 * L_LEAD + 2 * DPML
    sy = w_mmi + 1.2 + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    mat_core = mp.Medium(index=N_CORE)
    mat_clad = mp.Medium(index=N_CLAD)
    
    # Step 1: Reference Straight Waveguide for Normalization
    print("  --> Step 1: Running Straight Reference Waveguide Normalization...")
    ref_geom = [
        mp.Block(mp.Vector3(sx, w_port, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core)
    ]
    x_src = -l_total / 2.0 - L_LEAD * 0.6
    x_mon_in = -l_total / 2.0 - L_LEAD * 0.2
    x_mon_out =  l_total / 2.0 + L_LEAD * 0.4
    mon_w = w_port * 2.2
    
    src = mp.EigenModeSource(
        src=mp.GaussianSource(FCEN, fwidth=DF),
        center=mp.Vector3(x_src, 0, 0),
        size=mp.Vector3(0, mon_w, 0),
        eig_band=1,
        eig_match_freq=True,
        direction=mp.X
    )
    
    sim_ref = mp.Simulation(
        cell_size=cell,
        boundary_layers=[mp.PML(DPML)],
        geometry=ref_geom,
        sources=[src],
        resolution=RESOLUTION,
        default_material=mat_clad
    )
    
    m_ref_in = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_in, 0, 0), size=mp.Vector3(0, mon_w, 0)))
    m_ref_out = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, 0, 0), size=mp.Vector3(0, mon_w, 0)))
    
    sim_ref.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, 0, 0), 1e-5), until=120.0)
    
    res_ref_in = sim_ref.get_eigenmode_coefficients(m_ref_in, [1])
    res_ref_out = sim_ref.get_eigenmode_coefficients(m_ref_out, [1])
    p_in_ref = abs(res_ref_in.alpha[0, 0, 0])**2
    p_out_ref = abs(res_ref_out.alpha[0, 0, 0])**2
    print(f"      Reference Injected Power = {p_in_ref:.5e}, Transmitted = {p_out_ref:.5e}")
    
    # Step 2: Simulate Decoupled MZI in Amorphous and Crystalline States
    results = {}
    
    # Geometry coordinate layout:
    # Origin x=0 is at the center of the phase-shift arms
    x_arm_left = -l_arm / 2.0
    x_arm_right = l_arm / 2.0
    
    # Input MMI center:
    x_mmi_in = x_arm_left - l_mmi_in / 2.0
    # Output MMI center:
    x_mmi_out = x_arm_right + l_mmi_out / 2.0
    
    # Port leads:
    ll = L_LEAD + DPML
    x_in_lead = x_mmi_in - l_mmi_in / 2.0 - ll / 2.0
    x_out_lead = x_mmi_out + l_mmi_out / 2.0 + ll / 2.0
    
    for state in ["amorphous", "crystalline"]:
        print(f"\n  --> Step 2: Simulating 1x2 MZI in {state.upper()} State...")
        
        # Intrinsic -pi/2 phase bias required by 2x2 3dB MMI transfer matrix:
        # Delta_phi_bias = (2*pi/lambda_0) * delta_n_bias * l_arm = pi/2
        # ==> delta_n_bias = lambda_0 / (4 * l_arm)
        delta_n_bias = LAMBDA_0 / (4.0 * l_arm)
        n_lower = N_CORE + delta_n_bias
        mat_lower = mp.Medium(index=n_lower)
        
        # Upper arm material:
        # In amorphous state, relative phase is -pi/2 -> 100% into Port 1
        # In crystalline state, delta_n_patch adds +pi phase -> relative phase becomes +pi/2 -> 100% into Port 2
        n_upper = N_CORE if state == "amorphous" else (N_CORE + delta_n_patch)
        k_val = k_am if state == "amorphous" else k_cr
        cond = (2 * math.pi * FCEN * k_val / n_upper) if n_upper > 0 else 0.0
        mat_upper = mp.Medium(index=n_upper, D_conductivity=cond)
        
        geometry = []
        
        # 1. Input Lead (single center port at y=0)
        geometry.append(
            mp.Block(mp.Vector3(ll, w_port, mp.inf), center=mp.Vector3(x_in_lead, 0, 0), material=mat_core)
        )
        
        # 2. Input 1x2 MMI 3dB Splitter
        geometry.append(
            mp.Block(mp.Vector3(l_mmi_in, w_mmi, mp.inf), center=mp.Vector3(x_mmi_in, 0, 0), material=mat_core)
        )
        
        # 3. Decoupled Phase Arms:
        # Lower arm (Biased reference)
        geometry.append(
            mp.Block(mp.Vector3(l_arm, w_port, mp.inf), center=mp.Vector3(0, y_bot, 0), material=mat_lower)
        )
        # Upper arm (Active phase shifter)
        geometry.append(
            mp.Block(mp.Vector3(l_arm, w_port, mp.inf), center=mp.Vector3(0, y_top, 0), material=mat_upper)
        )
        
        # 4. Output 2x2 MMI 3dB Combiner
        geometry.append(
            mp.Block(mp.Vector3(l_mmi_out, w_mmi, mp.inf), center=mp.Vector3(x_mmi_out, 0, 0), material=mat_core)
        )
        
        # 5. Dual Output Leads (Port 1 at Top, Port 2 at Bottom)
        geometry += [
            mp.Block(mp.Vector3(ll, w_port, mp.inf), center=mp.Vector3(x_out_lead, y_top, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, w_port, mp.inf), center=mp.Vector3(x_out_lead, y_bot, 0), material=mat_core),
        ]
        
        sim = mp.Simulation(
            cell_size=cell,
            boundary_layers=[mp.PML(DPML)],
            geometry=geometry,
            sources=[src],
            resolution=RESOLUTION,
            default_material=mat_clad
        )
        
        m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_top, 0), size=mp.Vector3(0, mon_w, 0)))
        m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_bot, 0), size=mp.Vector3(0, mon_w, 0)))
        
        sim.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, y_top, 0), 1e-5), until=140.0)
        
        res_top = sim.get_eigenmode_coefficients(m_top, [1])
        res_bot = sim.get_eigenmode_coefficients(m_bot, [1])
        
        p_top = abs(res_top.alpha[0, 0, 0])**2 / p_in_ref
        p_bot = abs(res_bot.alpha[0, 0, 0])**2 / p_in_ref
        p_tot = p_top + p_bot
        
        results[state] = {
            "p_top": p_top,
            "p_bot": p_bot,
            "p_tot": p_tot
        }
        print(f"      {state.upper()}: P_top (Port 1) = {p_top*100:.2f}%, P_bot (Port 2) = {p_bot*100:.2f}%, P_total = {p_tot*100:.2f}%")
        
    t_state0 = results["amorphous"]["p_tot"]
    t_state1 = results["crystalline"]["p_tot"]
    il_state0_dB = -10.0 * math.log10(max(t_state0, 1e-6))
    il_state1_dB = -10.0 * math.log10(max(t_state1, 1e-6))
    
    # Switched Port Extinction:
    # Port 1 power in Amorphous vs Crystalline:
    er_p1_dB = 10.0 * math.log10(max(results["amorphous"]["p_top"], 1e-6) / max(results["crystalline"]["p_top"], 1e-6))
    # Port 2 power in Crystalline vs Amorphous:
    er_p2_dB = 10.0 * math.log10(max(results["crystalline"]["p_bot"], 1e-6) / max(results["amorphous"]["p_bot"], 1e-6))
    
    print("\n" + "-" * 80)
    print(f"RESULTS FOR {name}:")
    print(f"  Total Transmission (Amorphous)  : {t_state0*100:.2f}%  (IL = {il_state0_dB:.4f} dB)")
    print(f"  Total Transmission (Crystalline): {t_state1*100:.2f}%  (IL = {il_state1_dB:.4f} dB)")
    print(f"  Port 1 Extinction Ratio         : {er_p1_dB:.2f} dB")
    print(f"  Port 2 Extinction Ratio         : {er_p2_dB:.2f} dB")
    print("-" * 80)
    
    return {
        "name": name,
        "t_amorphous_pct": round(t_state0 * 100, 2),
        "il_amorphous_dB": round(il_state0_dB, 4),
        "t_crystalline_pct": round(t_state1 * 100, 2),
        "il_crystalline_dB": round(il_state1_dB, 4),
        "er_p1_dB": round(er_p1_dB, 2),
        "er_p2_dB": round(er_p2_dB, 2),
        "results": results
    }

def main():
    print("=" * 80)
    print("MEEP FDTD: DECOUPLED 1x2 MZI OPTICAL SWITCH VERIFICATION")
    print("=" * 80)
    
    # Candidate 1: Deeper Recessed Mode (L_arm = 3.68 um, Delta_n = 0.145)
    res1 = simulate_mzi_candidate(
        name="Candidate 1 (0.0471 dB Deeper Mode 1x2 MZI)",
        l_arm=3.68,
        delta_n_patch=0.145
    )
    
    # Candidate 2: Pure Top-Clad Slow Light (L_arm = 3.94 um, Delta_n = 0.135)
    res2 = simulate_mzi_candidate(
        name="Candidate 2 (0.1008 dB Top-Clad Slow Light 1x2 MZI)",
        l_arm=3.94,
        delta_n_patch=0.135
    )
    
    print("\n" + "=" * 80)
    print("SUMMARY COMPARISON OF DECOUPLED MZI SIMULATION RESULTS:")
    print("=" * 80)
    print(f"{'Candidate':<42}{'T_am(%)':<10}{'IL_am(dB)':<12}{'T_cr(%)':<10}{'IL_cr(dB)':<12}{'ER_P1(dB)':<10}{'ER_P2(dB)':<10}")
    print("-" * 80)
    print(f"{res1['name']:<42}{res1['t_amorphous_pct']:<10}{res1['il_amorphous_dB']:<12}{res1['t_crystalline_pct']:<10}{res1['il_crystalline_dB']:<12}{res1['er_p1_dB']:<10}{res1['er_p2_dB']:<10}")
    print(f"{res2['name']:<42}{res2['t_amorphous_pct']:<10}{res2['il_amorphous_dB']:<12}{res2['t_crystalline_pct']:<10}{res2['il_crystalline_dB']:<12}{res2['er_p1_dB']:<10}{res2['er_p2_dB']:<10}")
    print("=" * 80)

if __name__ == "__main__":
    main()
