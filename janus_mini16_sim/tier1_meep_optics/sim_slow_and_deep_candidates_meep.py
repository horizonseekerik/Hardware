"""
MEEP FDTD SIMULATION OF 0.0471 dB AND 0.1008 dB SWITCH CANDIDATES
==================================================================
Simulates the two winning deeper/slow-mode candidates at lambda_0 = 1064 nm:

Candidate 1 (0.0471 dB):
  - 1x2 MMI with Deeper Mode (35 nm recess into Si core, Gamma = 24.1%)
  - Cavity width: W_mmi = 1.60 um, Cavity length: L_mmi = 3.84 um
  - Input port: 1 center lead (w = 400 nm)
  - Output ports: 2 symmetric leads (w = 400 nm, y = +/- 0.41 um)
  - Active upper half: delta_n_eff = 0.145 (L_pi = 3.68 um)
  
Candidate 2 (0.1008 dB):
  - 1x2 MMI with Pure Top-Clad Slow Light (S = 2.5x, Gamma = 9.0%, Zero core etching)
  - Cavity width: W_mmi = 1.60 um, Cavity length: L_mmi = 4.00 um
  - Input/output leads: w = 400 nm
  - Active upper half: effective phase shift Delta_phi = pi over L_pi = 3.94 um
"""

import math
import sys
import numpy as np
import meep as mp

LAMBDA_0 = 1.064
FCEN = 1.0 / LAMBDA_0
DF = 0.08 * FCEN

# 2D Effective index model for Silicon on Insulator:
# Fundamental TE mode effective index of 220 nm Si core on SiO2 cladding at 1064 nm
N_CLAD = 1.449
N_CORE = 2.850  # TE slab effective index

DPML = 0.8
RESOLUTION = 40  # 40 pixels/um (25 nm grid)
L_LEAD = 1.50   # 1.5 um port leads

def simulate_candidate(name, w_mmi, l_mmi, w_port, y_out_sep, delta_n_patch, k_am=1e-5, k_cr=1.8e-4):
    print("\n" + "=" * 80)
    print(f"RUNNING MEEP FDTD FOR: {name}")
    print(f"MMI Box: {w_mmi} um wide x {l_mmi} um long | Ports: {w_port} um wide, sep: {y_out_sep} um")
    print(f"Index Perturbation Delta_n = {delta_n_patch:.4f}")
    print("=" * 80)
    
    y_out_top =  y_out_sep / 2.0
    y_out_bot = -y_out_sep / 2.0
    
    sx = l_mmi + 2 * L_LEAD + 2 * DPML
    sy = w_mmi + 1.2 + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    results = {}
    
    # 1. First run a reference straight waveguide to normalize power
    print("  --> Step 1: Simulating Straight Reference Waveguide for Normalization...")
    ref_geom = [
        mp.Block(mp.Vector3(sx, w_port, mp.inf), center=mp.Vector3(0, 0, 0), material=mp.Medium(index=N_CORE))
    ]
    x_src = -l_mmi / 2.0 - L_LEAD * 0.6
    x_mon_in = -l_mmi / 2.0 - L_LEAD * 0.2
    x_mon_out =  l_mmi / 2.0 + L_LEAD * 0.4
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
        default_material=mp.Medium(index=N_CLAD)
    )
    
    m_ref_in = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_in, 0, 0), size=mp.Vector3(0, mon_w, 0)))
    m_ref_out = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, 0, 0), size=mp.Vector3(0, mon_w, 0)))
    
    sim_ref.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, 0, 0), 1e-5), until=100.0)
    
    res_ref_in = sim_ref.get_eigenmode_coefficients(m_ref_in, [1])
    res_ref_out = sim_ref.get_eigenmode_coefficients(m_ref_out, [1])
    
    # Power injected into forward fundamental mode:
    p_in_ref = abs(res_ref_in.alpha[0, 0, 0])**2
    p_out_ref = abs(res_ref_out.alpha[0, 0, 0])**2
    print(f"      Reference Injected Power = {p_in_ref:.5e}, Transmitted = {p_out_ref:.5e}")
    
    # 2. Now run the 1x2 MMI Switch in State 0 (Amorphous) and State 1 (Crystalline)
    for state in ["amorphous", "crystalline"]:
        print(f"\n  --> Step 2: Simulating Switch in {state.upper()} State...")
        
        # Upper patch index:
        # In amorphous state, base perturbation is small or zero
        # In crystalline state, patch index shifts by delta_n_patch
        n_upper = N_CORE if state == "amorphous" else (N_CORE + delta_n_patch)
        k_val = k_am if state == "amorphous" else k_cr
        cond = (2 * math.pi * FCEN * k_val / n_upper) if n_upper > 0 else 0.0
        
        mat_core = mp.Medium(index=N_CORE)
        mat_upper = mp.Medium(index=n_upper, D_conductivity=cond)
        
        geometry = []
        
        # Center Input lead
        ll = L_LEAD + DPML
        x_in = -(l_mmi / 2.0 + ll / 2.0)
        geometry.append(
            mp.Block(mp.Vector3(ll, w_port, mp.inf), center=mp.Vector3(x_in, 0, 0), material=mat_core)
        )
        
        # Dual Output leads
        x_out = (l_mmi / 2.0 + ll / 2.0)
        geometry += [
            mp.Block(mp.Vector3(ll, w_port, mp.inf), center=mp.Vector3(x_out,  y_out_top, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, w_port, mp.inf), center=mp.Vector3(x_out,  y_out_bot, 0), material=mat_core),
        ]
        
        # Lower half of MMI box (unchanged core)
        w_half = w_mmi / 2.0
        geometry.append(
            mp.Block(mp.Vector3(l_mmi, w_half, mp.inf), center=mp.Vector3(0, -w_half / 2.0, 0), material=mat_core)
        )
        
        # Upper half of MMI box (active phase shifting region)
        geometry.append(
            mp.Block(mp.Vector3(l_mmi, w_half, mp.inf), center=mp.Vector3(0,  w_half / 2.0, 0), material=mat_upper)
        )
        
        sim = mp.Simulation(
            cell_size=cell,
            boundary_layers=[mp.PML(DPML)],
            geometry=geometry,
            sources=[src],
            resolution=RESOLUTION,
            default_material=mp.Medium(index=N_CLAD)
        )
        
        m_in = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_in, 0, 0), size=mp.Vector3(0, mon_w, 0)))
        m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  y_out_top, 0), size=mp.Vector3(0, mon_w, 0)))
        m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  y_out_bot, 0), size=mp.Vector3(0, mon_w, 0)))
        
        sim.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, y_out_top, 0), 1e-5), until=100.0)
        
        res_in = sim.get_eigenmode_coefficients(m_in, [1])
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
        print(f"      {state.upper()}: P_top = {p_top*100:.2f}%, P_bot = {p_bot*100:.2f}%, P_tot = {p_tot*100:.2f}%")
        
    # Calculate performance metrics:
    # State 0 (Amorphous): Balanced 1x2 splitter or Port 1 state
    # State 1 (Crystalline): Switched to Port 2 state
    t_state0 = results["amorphous"]["p_tot"]
    t_state1 = results["crystalline"]["p_tot"]
    
    il_state0_dB = -10.0 * math.log10(max(t_state0, 1e-6))
    il_state1_dB = -10.0 * math.log10(max(t_state1, 1e-6))
    
    # Contrast / Extinction Ratio between states on Port 2 (Bottom):
    p_bot_on = results["crystalline"]["p_bot"]
    p_bot_off = results["amorphous"]["p_bot"]
    er_dB = 10.0 * math.log10(max(p_bot_on, 1e-6) / max(p_bot_off, 1e-6))
    
    print("\n" + "-" * 80)
    print(f"FINAL MEEP RESULTS FOR {name}:")
    print(f"  Total Transmission (Amorphous)  : {t_state0 * 100:.2f}% (Loss = {il_state0_dB:.4f} dB)")
    print(f"  Total Transmission (Crystalline): {t_state1 * 100:.2f}% (Loss = {il_state1_dB:.4f} dB)")
    print(f"  Port 1 / Port 2 Power Distribution:")
    print(f"    - Amorphous  : Top = {results['amorphous']['p_top']*100:.2f}%, Bottom = {results['amorphous']['p_bot']*100:.2f}%")
    print(f"    - Crystalline: Top = {results['crystalline']['p_top']*100:.2f}%, Bottom = {results['crystalline']['p_bot']*100:.2f}%")
    print(f"  Extinction Ratio                : {abs(er_dB):.2f} dB")
    print("-" * 80)
    
    return {
        "name": name,
        "t_amorphous_pct": round(t_state0 * 100, 2),
        "il_amorphous_dB": round(il_state0_dB, 4),
        "t_crystalline_pct": round(t_state1 * 100, 2),
        "il_crystalline_dB": round(il_state1_dB, 4),
        "er_dB": round(abs(er_dB), 2),
        "results": results
    }

def main():
    print("=" * 80)
    print("MEEP FULL-WAVE FDTD VERIFICATION OF TOP 2 CONTESTANTS")
    print("=" * 80)
    
    # Candidate 1: 0.0471 dB Deeper Mode Candidate
    # W_mmi = 1.60 um, L_mmi = 3.84 um, Delta_n_patch = 0.145 (35 nm recess)
    res1 = simulate_candidate(
        name="Candidate 1 (0.0471 dB Deeper Recessed Mode)",
        w_mmi=1.60,
        l_mmi=3.84,
        w_port=0.40,
        y_out_sep=0.80,
        delta_n_patch=0.145
    )
    
    # Candidate 2: 0.1008 dB Pure Top-Clad Slow Light Candidate
    # W_mmi = 1.60 um, L_mmi = 4.00 um, S = 2.5x -> equivalent Delta_n_eff = 0.054 * 2.5 = 0.135
    res2 = simulate_candidate(
        name="Candidate 2 (0.1008 dB Pure Top-Clad Slow Light)",
        w_mmi=1.60,
        l_mmi=4.00,
        w_port=0.40,
        y_out_sep=0.80,
        delta_n_patch=0.135
    )
    
    print("\n" + "=" * 80)
    print("SUMMARY COMPARISON OF MEEP SIMULATION RESULTS:")
    print("=" * 80)
    print(f"{'Candidate':<42}{'T_am(%)':<10}{'IL_am(dB)':<12}{'T_cr(%)':<10}{'IL_cr(dB)':<12}{'ER(dB)':<8}")
    print("-" * 80)
    print(f"{res1['name']:<42}{res1['t_amorphous_pct']:<10}{res1['il_amorphous_dB']:<12}{res1['t_crystalline_pct']:<10}{res1['il_crystalline_dB']:<12}{res1['er_dB']:<8}")
    print(f"{res2['name']:<42}{res2['t_amorphous_pct']:<10}{res2['il_amorphous_dB']:<12}{res2['t_crystalline_pct']:<10}{res2['il_crystalline_dB']:<12}{res2['er_dB']:<8}")
    print("=" * 80)

if __name__ == "__main__":
    main()
