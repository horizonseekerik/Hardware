"""
MEEP FDTD: TAPERED PATCH TIPS & GEOMETRIC REJECTION IN 1x2 MMI SWITCH
======================================================================
Evaluates:
  1. Tapered Patch Tips (hexagonal/pointed apodized patch to eliminate boundary scattering)
  2. Case A: WITHOUT Geometric Rejection (standard symmetric adiabatic tapers)
  3. Case B: WITH Geometric Rejection (asymmetric mode filter on output ports)
"""

import math
import sys
import meep as mp

LAMBDA_0 = 1.064
FCEN = 1.0 / LAMBDA_0
DF = 0.08 * FCEN

N_CLAD = 1.449
N_CORE = 2.850

DPML = 0.8
RESOLUTION = 40

W_MMI = 1.60
L_MMI = 3.84
W_PORT = 0.40
W_TAPER = 0.55
L_TAPER = 1.00
Y_OUT = 0.40
L_LEAD = 1.20

# Active patch parameters:
Y_PATCH = 0.40
W_PATCH = 0.50
L_PATCH_MID = 1.80
L_PATCH_TIP = 0.60
L_PATCH_TOT = L_PATCH_MID + 2 * L_PATCH_TIP  # 3.0 um
DELTA_N = 0.145
K_CR = 1.8e-4

sx = L_MMI + 2 * L_TAPER + 2 * L_LEAD + 2 * DPML
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

def run_simulation(with_geom_rejection):
    mode_str = "WITH Geometric Rejection" if with_geom_rejection else "WITHOUT Geometric Rejection"
    print("\n" + "=" * 80)
    print(f"SIMULATION RUN: {mode_str}")
    print("=" * 80)
    
    # 1. Reference straight waveguide
    ref_geom = [mp.Block(mp.Vector3(sx, W_PORT, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core)]
    sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=ref_geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
    m_ref = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, 0, 0), size=mp.Vector3(0, mon_w, 0)))
    sim_ref.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, 0, 0), 1e-5), until=100.0)
    p_ref = abs(sim_ref.get_eigenmode_coefficients(m_ref, [1]).alpha[0, 0, 0])**2
    
    results = {}
    
    for state in ["amorphous", "crystalline"]:
        geom = []
        
        # MMI Box
        geom.append(mp.Block(mp.Vector3(L_MMI, W_MMI, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core))
        
        # Input Lead + Taper (left)
        ll = L_LEAD + DPML
        x_in_lead = -L_MMI/2 - L_TAPER - ll/2
        geom.append(mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_in_lead, 0, 0), material=mat_core))
        taper_in = [
            mp.Vector3(-L_MMI/2 - L_TAPER, -W_PORT/2, 0),
            mp.Vector3(-L_MMI/2, -W_TAPER/2, 0),
            mp.Vector3(-L_MMI/2,  W_TAPER/2, 0),
            mp.Vector3(-L_MMI/2 - L_TAPER,  W_PORT/2, 0),
        ]
        geom.append(mp.Prism(taper_in, height=mp.inf, material=mat_core))
        
        # Output Leads + Tapers
        x_out_lead = L_MMI/2 + L_TAPER + ll/2
        geom += [
            mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead,  Y_OUT, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead, -Y_OUT, 0), material=mat_core),
        ]
        
        if not with_geom_rejection:
            # Case A: Standard Symmetric Adiabatic Tapers
            taper_top = [
                mp.Vector3(L_MMI/2, Y_OUT - W_TAPER/2, 0),
                mp.Vector3(L_MMI/2 + L_TAPER, Y_OUT - W_PORT/2, 0),
                mp.Vector3(L_MMI/2 + L_TAPER, Y_OUT + W_PORT/2, 0),
                mp.Vector3(L_MMI/2, Y_OUT + W_TAPER/2, 0),
            ]
            geom.append(mp.Prism(taper_top, height=mp.inf, material=mat_core))
            
            taper_bot = [
                mp.Vector3(L_MMI/2, -Y_OUT - W_TAPER/2, 0),
                mp.Vector3(L_MMI/2 + L_TAPER, -Y_OUT - W_PORT/2, 0),
                mp.Vector3(L_MMI/2 + L_TAPER, -Y_OUT + W_PORT/2, 0),
                mp.Vector3(L_MMI/2, -Y_OUT + W_TAPER/2, 0),
            ]
            geom.append(mp.Prism(taper_bot, height=mp.inf, material=mat_core))
        else:
            # Case B: Asymmetric Taper Mode Filter (Geometric Rejection)
            # The top port taper incorporates a mode-filtering bottleneck (240 nm waist)
            # to reject unwanted leakage into radiation, while bottom port has smooth wide taper
            w_waist = 0.240
            l_t_half = L_TAPER / 2.0
            
            # Top port: Asymmetric rejection filter (550 nm -> 240 nm -> 400 nm)
            taper_top_p1 = [
                mp.Vector3(L_MMI/2, Y_OUT - W_TAPER/2, 0),
                mp.Vector3(L_MMI/2 + l_t_half, Y_OUT - w_waist/2, 0),
                mp.Vector3(L_MMI/2 + l_t_half, Y_OUT + w_waist/2, 0),
                mp.Vector3(L_MMI/2, Y_OUT + W_TAPER/2, 0),
            ]
            taper_top_p2 = [
                mp.Vector3(L_MMI/2 + l_t_half, Y_OUT - w_waist/2, 0),
                mp.Vector3(L_MMI/2 + L_TAPER, Y_OUT - W_PORT/2, 0),
                mp.Vector3(L_MMI/2 + L_TAPER, Y_OUT + W_PORT/2, 0),
                mp.Vector3(L_MMI/2 + l_t_half, Y_OUT + w_waist/2, 0),
            ]
            geom.append(mp.Prism(taper_top_p1, height=mp.inf, material=mat_core))
            geom.append(mp.Prism(taper_top_p2, height=mp.inf, material=mat_core))
            
            # Bottom port: Smooth adiabatic collector (550 nm -> 400 nm)
            taper_bot = [
                mp.Vector3(L_MMI/2, -Y_OUT - W_TAPER/2, 0),
                mp.Vector3(L_MMI/2 + L_TAPER, -Y_OUT - W_PORT/2, 0),
                mp.Vector3(L_MMI/2 + L_TAPER, -Y_OUT + W_PORT/2, 0),
                mp.Vector3(L_MMI/2, -Y_OUT + W_TAPER/2, 0),
            ]
            geom.append(mp.Prism(taper_bot, height=mp.inf, material=mat_core))
            
        # Active Patch with Tapered Tips:
        # In both states, geometry is identical; only index shifts
        # Apodized pointed hexagon:
        x_p_start = -L_PATCH_TOT / 2.0 + 0.15
        x_p_t1 = x_p_start + L_PATCH_TIP
        x_p_t2 = x_p_t1 + L_PATCH_MID
        x_p_end = x_p_t2 + L_PATCH_TIP
        
        patch_verts = [
            mp.Vector3(x_p_start, Y_PATCH, 0),                    # Left pointed tip
            mp.Vector3(x_p_t1,    Y_PATCH - W_PATCH / 2.0, 0),     # Bottom-left corner
            mp.Vector3(x_p_t2,    Y_PATCH - W_PATCH / 2.0, 0),     # Bottom-right corner
            mp.Vector3(x_p_end,   Y_PATCH, 0),                    # Right pointed tip
            mp.Vector3(x_p_t2,    Y_PATCH + W_PATCH / 2.0, 0),     # Top-right corner
            mp.Vector3(x_p_t1,    Y_PATCH + W_PATCH / 2.0, 0),     # Top-left corner
        ]
        
        if state == "crystalline":
            n_p = N_CORE + DELTA_N
            cond = (2 * math.pi * FCEN * K_CR / n_p) if n_p > 0 else 0.0
            mat_patch = mp.Medium(index=n_p, D_conductivity=cond)
            geom.append(mp.Prism(patch_verts, height=mp.inf, material=mat_patch))
            
        sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
        m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_OUT, 0), size=mp.Vector3(0, mon_w, 0)))
        m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, -Y_OUT, 0), size=mp.Vector3(0, mon_w, 0)))
        
        sim.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, Y_OUT, 0), 1e-5), until=110.0)
        
        pt = abs(sim.get_eigenmode_coefficients(m_top, [1]).alpha[0, 0, 0])**2 / p_ref
        pb = abs(sim.get_eigenmode_coefficients(m_bot, [1]).alpha[0, 0, 0])**2 / p_ref
        tot = pt + pb
        il = -10.0 * math.log10(max(tot, 1e-6))
        results[state] = {"p_top": pt, "p_bot": pb, "total": tot, "il_dB": il}
        print(f"  {state.upper()}: P_top = {pt*100:.2f}%, P_bot = {pb*100:.2f}%, Total = {tot*100:.2f}% (IL = {il:.4f} dB)")
        
    return results

def main():
    print("=" * 80)
    print("COMPARATIVE STUDY: TAPERED PATCH TIPS WITH & WITHOUT GEOMETRIC REJECTION")
    print("=" * 80)
    
    # Run Case A: WITHOUT Geometric Rejection
    resA = run_simulation(with_geom_rejection=False)
    
    # Run Case B: WITH Geometric Rejection
    resB = run_simulation(with_geom_rejection=True)
    
    print("\n" + "=" * 90)
    print("FULL SUMMARY COMPARISON TABLE:")
    print("=" * 90)
    print(f"{'Case':<32}{'State':<14}{'P_top(%)':<12}{'P_bot(%)':<12}{'Total(%)':<12}{'IL(dB)':<10}")
    print("-" * 90)
    print(f"{'Without Rejection':<32}{'Amorphous':<14}{resA['amorphous']['p_top']*100:<12.2f}{resA['amorphous']['p_bot']*100:<12.2f}{resA['amorphous']['total']*100:<12.2f}{resA['amorphous']['il_dB']:<10.4f}")
    print(f"{'Without Rejection':<32}{'Crystalline':<14}{resA['crystalline']['p_top']*100:<12.2f}{resA['crystalline']['p_bot']*100:<12.2f}{resA['crystalline']['total']*100:<12.2f}{resA['crystalline']['il_dB']:<10.4f}")
    print("-" * 90)
    print(f"{'With Geometric Rejection':<32}{'Amorphous':<14}{resB['amorphous']['p_top']*100:<12.2f}{resB['amorphous']['p_bot']*100:<12.2f}{resB['amorphous']['total']*100:<12.2f}{resB['amorphous']['il_dB']:<10.4f}")
    print(f"{'With Geometric Rejection':<32}{'Crystalline':<14}{resB['crystalline']['p_top']*100:<12.2f}{resB['crystalline']['p_bot']*100:<12.2f}{resB['crystalline']['total']*100:<12.2f}{resB['crystalline']['il_dB']:<10.4f}")
    print("=" * 90)

if __name__ == "__main__":
    main()
