"""
MEEP FDTD: TAPERED 1x2 MMI SWITCH WITH ADIABATIC PORT TAPERS
=============================================================
Architecture:
  - 1x2 MMI Multimode Cavity (W = 1.60 um, L = 3.84 um for Cand 1, 4.00 um for Cand 2)
  - Linear Adiabatic Port Tapers on ALL ports (1.0 um length, 400 nm <-> 550 nm):
      * Input center port: 400 nm -> 550 nm
      * Dual output ports: 550 nm -> 400 nm at y = +/- 0.40 um
  - Active Upper-Lobe Phase Patch (isolated from y=0 centerline to prevent inter-modal scattering):
      * y_center = +0.40 um, width = 0.50 um
      * Adiabatic entry/exit tapers on the patch
  - Simulates Candidate 1 (Deeper Mode, Delta_n = 0.145) and Candidate 2 (Slow Light, Delta_n = 0.135)
"""

import math
import sys
import meep as mp

LAMBDA_0 = 1.064
FCEN = 1.0 / LAMBDA_0
DF = 0.08 * FCEN

N_CLAD = 1.449
N_CORE = 2.850  # TE slab fundamental effective index

DPML = 0.8
RESOLUTION = 40

W_MMI = 1.60
W_PORT = 0.40
W_TAPER = 0.55
L_TAPER = 1.00
Y_OUT = 0.40
L_LEAD = 1.20

def simulate_tapered_1x2_mmi(name, l_mmi, delta_n_patch, k_am=1e-5, k_cr=1.8e-4):
    print("\n" + "=" * 80)
    print(f"RUNNING MEEP FDTD FOR: {name}")
    print(f"MMI: {W_MMI} um wide x {l_mmi} um long with Adiabatic Port Tapers")
    print(f"Active Patch Delta_n = {delta_n_patch:.4f}")
    print("=" * 80)
    
    sx = l_mmi + 2 * L_TAPER + 2 * L_LEAD + 2 * DPML
    sy = W_MMI + 1.2 + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    mat_core = mp.Medium(index=N_CORE)
    mat_clad = mp.Medium(index=N_CLAD)
    
    x_src = -sx/2 + DPML + 0.3
    x_mon_out = sx/2 - DPML - 0.3
    mon_w = W_PORT * 2.2
    
    src = mp.EigenModeSource(
        src=mp.GaussianSource(FCEN, fwidth=DF),
        center=mp.Vector3(x_src, 0, 0),
        size=mp.Vector3(0, mon_w, 0),
        eig_band=1, eig_match_freq=True, direction=mp.X
    )
    
    # 1. Reference straight waveguide
    print("  --> Step 1: Simulating Reference Waveguide for Normalization...")
    ref_geom = [mp.Block(mp.Vector3(sx, W_PORT, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core)]
    sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=ref_geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
    m_ref = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, 0, 0), size=mp.Vector3(0, mon_w, 0)))
    sim_ref.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, 0, 0), 1e-5), until=120.0)
    p_ref = abs(sim_ref.get_eigenmode_coefficients(m_ref, [1]).alpha[0, 0, 0])**2
    print(f"      Reference Injected Power = {p_ref:.5e}")
    
    results = {}
    
    for state in ["amorphous", "crystalline"]:
        print(f"\n  --> Step 2: Simulating 1x2 MMI in {state.upper()} State...")
        
        geom = []
        
        # 1. Main MMI Box
        geom.append(mp.Block(mp.Vector3(l_mmi, W_MMI, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core))
        
        # 2. Input Lead + Linear Adiabatic Taper
        ll = L_LEAD + DPML
        x_in_lead = -l_mmi/2 - L_TAPER - ll/2
        geom.append(mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_in_lead, 0, 0), material=mat_core))
        taper_in = [
            mp.Vector3(-l_mmi/2 - L_TAPER, -W_PORT/2, 0),
            mp.Vector3(-l_mmi/2, -W_TAPER/2, 0),
            mp.Vector3(-l_mmi/2,  W_TAPER/2, 0),
            mp.Vector3(-l_mmi/2 - L_TAPER,  W_PORT/2, 0),
        ]
        geom.append(mp.Prism(taper_in, height=mp.inf, material=mat_core))
        
        # 3. Output Leads + Linear Adiabatic Tapers
        x_out_lead = l_mmi/2 + L_TAPER + ll/2
        geom += [
            mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead,  Y_OUT, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead, -Y_OUT, 0), material=mat_core),
        ]
        taper_top = [
            mp.Vector3(l_mmi/2, Y_OUT - W_TAPER/2, 0),
            mp.Vector3(l_mmi/2 + L_TAPER, Y_OUT - W_PORT/2, 0),
            mp.Vector3(l_mmi/2 + L_TAPER, Y_OUT + W_PORT/2, 0),
            mp.Vector3(l_mmi/2, Y_OUT + W_TAPER/2, 0),
        ]
        geom.append(mp.Prism(taper_top, height=mp.inf, material=mat_core))
        taper_bot = [
            mp.Vector3(l_mmi/2, -Y_OUT - W_TAPER/2, 0),
            mp.Vector3(l_mmi/2 + L_TAPER, -Y_OUT - W_PORT/2, 0),
            mp.Vector3(l_mmi/2 + L_TAPER, -Y_OUT + W_PORT/2, 0),
            mp.Vector3(l_mmi/2, -Y_OUT + W_TAPER/2, 0),
        ]
        geom.append(mp.Prism(taper_bot, height=mp.inf, material=mat_core))
        
        # 4. Active Upper-Lobe Phase-Shifting Patch
        # Isolated over the upper lobe (y in [0.15, 0.65] um) with smooth transitions
        if state == "crystalline":
            w_patch = 0.50
            y_patch = 0.40
            l_patch = l_mmi * 0.85
            x_patch = l_mmi * 0.05
            
            k_val = k_cr
            n_p = N_CORE + delta_n_patch
            cond = (2 * math.pi * FCEN * k_val / n_p) if n_p > 0 else 0.0
            mat_patch = mp.Medium(index=n_p, D_conductivity=cond)
            
            geom.append(
                mp.Block(mp.Vector3(l_patch, w_patch, mp.inf), center=mp.Vector3(x_patch, y_patch, 0), material=mat_patch)
            )
            
        sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
        m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_OUT, 0), size=mp.Vector3(0, mon_w, 0)))
        m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, -Y_OUT, 0), size=mp.Vector3(0, mon_w, 0)))
        
        sim.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, Y_OUT, 0), 1e-5), until=120.0)
        
        res_top = sim.get_eigenmode_coefficients(m_top, [1])
        res_bot = sim.get_eigenmode_coefficients(m_bot, [1])
        
        p_top = abs(res_top.alpha[0, 0, 0])**2 / p_ref
        p_bot = abs(res_bot.alpha[0, 0, 0])**2 / p_ref
        p_tot = p_top + p_bot
        
        results[state] = {
            "p_top": p_top,
            "p_bot": p_bot,
            "p_tot": p_tot
        }
        print(f"      {state.upper()}: P_top = {p_top*100:.2f}%, P_bot = {p_bot*100:.2f}%, P_total = {p_tot*100:.2f}%")
        
    t_am = results["amorphous"]["p_tot"]
    t_cr = results["crystalline"]["p_tot"]
    il_am_dB = -10.0 * math.log10(max(t_am, 1e-6))
    il_cr_dB = -10.0 * math.log10(max(t_cr, 1e-6))
    
    # On/Off contrast for Port 1 (Top) and Port 2 (Bottom):
    er_p1_dB = 10.0 * math.log10(max(results["crystalline"]["p_top"], 1e-6) / max(results["amorphous"]["p_top"], 1e-6))
    er_p2_dB = 10.0 * math.log10(max(results["amorphous"]["p_bot"], 1e-6) / max(results["crystalline"]["p_bot"], 1e-6))
    
    print("\n" + "-" * 80)
    print(f"RESULTS FOR {name}:")
    print(f"  Amorphous State  : P_top = {results['amorphous']['p_top']*100:.2f}%, P_bot = {results['amorphous']['p_bot']*100:.2f}%, Total = {t_am*100:.2f}% (IL = {il_am_dB:.4f} dB)")
    print(f"  Crystalline State: P_top = {results['crystalline']['p_top']*100:.2f}%, P_bot = {results['crystalline']['p_bot']*100:.2f}%, Total = {t_cr*100:.2f}% (IL = {il_cr_dB:.4f} dB)")
    print(f"  Port Contrast    : ER_P1 = {er_p1_dB:.2f} dB, ER_P2 = {er_p2_dB:.2f} dB")
    print("-" * 80)
    
    return {
        "name": name,
        "t_am": round(t_am * 100, 2),
        "il_am": round(il_am_dB, 4),
        "t_cr": round(t_cr * 100, 2),
        "il_cr": round(il_cr_dB, 4),
        "er_p1": round(er_p1_dB, 2),
        "er_p2": round(er_p2_dB, 2),
        "results": results
    }

def main():
    print("=" * 80)
    print("MEEP FULL-WAVE FDTD: 1x2 MMI SWITCH WITH ADIABATIC PORT TAPERS")
    print("=" * 80)
    
    # Candidate 1: Deeper Mode (L = 3.84 um, Delta_n = 0.145)
    res1 = simulate_tapered_1x2_mmi(
        name="Candidate 1 (Deeper Recessed Mode, L = 3.84 um)",
        l_mmi=3.84,
        delta_n_patch=0.145
    )
    
    # Candidate 2: Pure Top-Clad Slow Light (L = 4.00 um, Delta_n = 0.135)
    res2 = simulate_tapered_1x2_mmi(
        name="Candidate 2 (Pure Top-Clad Slow Light, L = 4.00 um)",
        l_mmi=4.00,
        delta_n_patch=0.135
    )
    
    print("\n" + "=" * 80)
    print("FINAL SUMMARY: 1x2 MMI WITH ADIABATIC PORT TAPERS")
    print("=" * 80)
    print(f"{'Candidate':<42}{'T_am(%)':<10}{'IL_am(dB)':<12}{'T_cr(%)':<10}{'IL_cr(dB)':<12}")
    print("-" * 80)
    print(f"{res1['name']:<42}{res1['t_am']:<10}{res1['il_am']:<12}{res1['t_cr']:<10}{res1['il_cr']:<12}")
    print(f"{res2['name']:<42}{res2['t_am']:<10}{res2['il_am']:<12}{res2['t_cr']:<10}{res2['il_cr']:<12}")
    print("=" * 80)

if __name__ == "__main__":
    main()
