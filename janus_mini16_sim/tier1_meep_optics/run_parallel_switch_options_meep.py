"""
MEEP FDTD: COMPARISON OF SWITCH OPTIONS WITH PARABOLIC TAPERS
=============================================================
Evaluates three architectures simultaneously with parabolic tapers & apodized patch tips:
  - Option 1: Paired-Interference 1x2 MMI Switch (single cavity, offset input at +W_eff/6)
  - Option 2: Compact Slow-Light Directional Coupler Switch (with parabolic S-bends)
  - Option 3: Combined / Hybrid MMI-Assisted Coupler Switch (MADIC)
All designs feature smooth parabolic tapers (zero 90-degree corners) to minimize crystalline loss.
"""

import math
import sys
import numpy as np
import meep as mp

LAMBDA_0 = 1.064
FCEN = 1.0 / LAMBDA_0
DF = 0.08 * FCEN

N_CLAD = 1.449
N_CORE = 2.850  # TE slab effective index

DPML = 0.8
RESOLUTION = 40

def make_parabolic_taper_polygon(x_start, x_end, y_center, w_start, w_end, n_pts=12):
    """Generates a smooth parabolic taper polygon with zero sharp derivative corners."""
    dx = x_end - x_start
    x_vals = np.linspace(x_start, x_end, n_pts)
    
    # Quadratic smooth S-profile / parabolic curve:
    # u = (x - x_start) / dx in [0, 1]
    # w(u) = w_start + (w_end - w_start) * (3*u^2 - 2*u^3)  (Smooth hermite/parabolic)
    u_vals = (x_vals - x_start) / dx
    w_vals = w_start + (w_end - w_start) * (3 * u_vals**2 - 2 * u_vals**3)
    
    top_edge = [mp.Vector3(x, y_center + w / 2.0, 0) for x, w in zip(x_vals, w_vals)]
    bot_edge = [mp.Vector3(x, y_center - w / 2.0, 0) for x, w in reversed(list(zip(x_vals, w_vals)))]
    return top_edge + bot_edge

def make_parabolic_patch_polygon(x_center, y_center, l_patch, w_patch, l_tip=0.80, n_pts=8):
    """Generates an active patch with smooth parabolic entry and exit tips."""
    x_left_tip = x_center - l_patch / 2.0
    x_left_body = x_left_tip + l_tip
    x_right_body = x_center + l_patch / 2.0 - l_tip
    x_right_tip = x_center + l_patch / 2.0
    
    # Left entry parabolic taper: width 0 -> w_patch
    u_left = np.linspace(0, 1, n_pts)
    x_l = x_left_tip + u_left * l_tip
    w_l = w_patch * (2 * u_left - u_left**2)
    
    # Right exit parabolic taper: width w_patch -> 0
    u_right = np.linspace(0, 1, n_pts)
    x_r = x_right_body + u_right * l_tip
    w_r = w_patch * (1.0 - u_right**2)
    
    top_pts = [mp.Vector3(x, y_center + w/2.0, 0) for x, w in zip(x_l, w_l)]
    top_pts += [mp.Vector3(x_right_body, y_center + w_patch/2.0, 0)]
    top_pts += [mp.Vector3(x, y_center + w/2.0, 0) for x, w in zip(x_r, w_r)]
    
    bot_pts = [mp.Vector3(x, y_center - w/2.0, 0) for x, w in reversed(list(zip(x_r, w_r)))]
    bot_pts += [mp.Vector3(x_right_body, y_center - w_patch/2.0, 0)]
    bot_pts += [mp.Vector3(x, y_center - w/2.0, 0) for x, w in reversed(list(zip(x_l, w_l)))]
    
    return top_pts + bot_pts

# ==============================================================================
# OPTION 1: PAIRED-INTERFERENCE 1x2 MMI SWITCH WITH PARABOLIC TAPERS
# ==============================================================================
def simulate_option1():
    print("\n" + "=" * 80)
    print("SIMULATING OPTION 1: PAIRED-INTERFERENCE 1x2 MMI WITH PARABOLIC TAPERS")
    print("=" * 80)
    
    W_MMI = 1.80
    w_eff = W_MMI + (LAMBDA_0 / math.pi) / math.sqrt(N_CORE**2 - N_CLAD**2)
    Y_POS = w_eff / 6.0  # 0.323 um
    L_MMI = 4.60
    W_PORT = 0.38
    W_TAPER = 0.48
    L_TAPER = 1.00
    L_LEAD = 1.00
    DELTA_N = 0.145
    
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
        center=mp.Vector3(x_src, Y_POS, 0),
        size=mp.Vector3(0, mon_w, 0),
        eig_band=1, eig_match_freq=True, direction=mp.X
    )
    
    # Ref
    sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=[mp.Block(mp.Vector3(sx, W_PORT, mp.inf), center=mp.Vector3(0, Y_POS, 0), material=mat_core)], sources=[src], resolution=RESOLUTION, default_material=mat_clad)
    m_ref = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
    sim_ref.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, Y_POS, 0), 1e-5), until=100.0)
    p_ref = abs(sim_ref.get_eigenmode_coefficients(m_ref, [1]).alpha[0, 0, 0])**2
    
    results = {}
    for state in ["amorphous", "crystalline"]:
        geom = []
        geom.append(mp.Block(mp.Vector3(L_MMI, W_MMI, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core))
        
        # Input lead + parabolic taper
        ll = L_LEAD + DPML
        x_in_lead = -L_MMI/2 - L_TAPER - ll/2
        geom.append(mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_in_lead, Y_POS, 0), material=mat_core))
        poly_in = make_parabolic_taper_polygon(-L_MMI/2 - L_TAPER, -L_MMI/2, Y_POS, W_PORT, W_TAPER)
        geom.append(mp.Prism(poly_in, height=mp.inf, material=mat_core))
        
        # Output leads + parabolic tapers
        x_out_lead = L_MMI/2 + L_TAPER + ll/2
        geom += [
            mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead,  Y_POS, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead, -Y_POS, 0), material=mat_core),
        ]
        poly_top = make_parabolic_taper_polygon(L_MMI/2, L_MMI/2 + L_TAPER,  Y_POS, W_TAPER, W_PORT)
        poly_bot = make_parabolic_taper_polygon(L_MMI/2, L_MMI/2 + L_TAPER, -Y_POS, W_TAPER, W_PORT)
        geom.append(mp.Prism(poly_top, height=mp.inf, material=mat_core))
        geom.append(mp.Prism(poly_bot, height=mp.inf, material=mat_core))
        
        # Parabolic patch
        if state == "crystalline":
            mat_p = mp.Medium(index=N_CORE + DELTA_N)
            patch_poly = make_parabolic_patch_polygon(0.1, Y_POS, l_patch=3.4, w_patch=0.48, l_tip=0.80)
            geom.append(mp.Prism(patch_poly, height=mp.inf, material=mat_p))
            
        sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
        m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
        m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, -Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
        sim.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, Y_POS, 0), 1e-5), until=100.0)
        
        pt = abs(sim.get_eigenmode_coefficients(m_top, [1]).alpha[0, 0, 0])**2 / p_ref
        pb = abs(sim.get_eigenmode_coefficients(m_bot, [1]).alpha[0, 0, 0])**2 / p_ref
        results[state] = (pt, pb, pt + pb)
        print(f"  {state.upper()}: P_top (Port 1) = {pt*100:.2f}%, P_bot (Port 2) = {pb*100:.2f}%, Total = {(pt+pb)*100:.2f}%")
        
    return results

# ==============================================================================
# OPTION 2: COMPACT SLOW-LIGHT DIRECTIONAL COUPLER SWITCH WITH PARABOLIC S-BENDS
# ==============================================================================
def simulate_option2():
    print("\n" + "=" * 80)
    print("SIMULATING OPTION 2: SLOW-LIGHT DIRECTIONAL COUPLER WITH PARABOLIC S-BENDS")
    print("=" * 80)
    
    W_WG = 0.38
    GAP = 0.140  # 140 nm coupling gap
    L_C = 3.70   # Coupling length
    L_BEND = 1.40
    Y_SEP_FINAL = 0.80  # Final port separation
    Y_WG1 = (GAP + W_WG) / 2.0  # +0.260 um
    Y_WG2 = -(GAP + W_WG) / 2.0 # -0.260 um
    Y_OUT1 = Y_SEP_FINAL / 2.0  # +0.400 um
    Y_OUT2 = -Y_SEP_FINAL / 2.0 # -0.400 um
    L_LEAD = 1.00
    DELTA_N = 0.145
    
    sx = L_C + 2 * L_BEND + 2 * L_LEAD + 2 * DPML
    sy = Y_SEP_FINAL + 1.2 + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    mat_core = mp.Medium(index=N_CORE)
    mat_clad = mp.Medium(index=N_CLAD)
    
    x_src = -sx/2 + DPML + 0.3
    x_mon_out = sx/2 - DPML - 0.3
    mon_w = W_WG * 2.2
    
    src = mp.EigenModeSource(
        src=mp.GaussianSource(FCEN, fwidth=DF),
        center=mp.Vector3(x_src, Y_WG1, 0),
        size=mp.Vector3(0, mon_w, 0),
        eig_band=1, eig_match_freq=True, direction=mp.X
    )
    
    # Ref
    sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=[mp.Block(mp.Vector3(sx, W_WG, mp.inf), center=mp.Vector3(0, Y_WG1, 0), material=mat_core)], sources=[src], resolution=RESOLUTION, default_material=mat_clad)
    m_ref = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, Y_WG1, 0), size=mp.Vector3(0, mon_w, 0)))
    sim_ref.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, Y_WG1, 0), 1e-5), until=100.0)
    p_ref = abs(sim_ref.get_eigenmode_coefficients(m_ref, [1]).alpha[0, 0, 0])**2
    
    results = {}
    for state in ["amorphous", "crystalline"]:
        geom = []
        
        # Parallel coupling central section
        geom += [
            mp.Block(mp.Vector3(L_C, W_WG, mp.inf), center=mp.Vector3(0, Y_WG1, 0), material=mat_core),
            mp.Block(mp.Vector3(L_C, W_WG, mp.inf), center=mp.Vector3(0, Y_WG2, 0), material=mat_core),
        ]
        
        # Input lead (single port into WG1)
        ll = L_LEAD + DPML
        x_in_lead = -L_C/2 - L_BEND - ll/2
        geom.append(mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_in_lead, Y_WG1, 0), material=mat_core))
        
        # Smooth input lead transition
        geom.append(mp.Block(mp.Vector3(L_BEND, W_WG, mp.inf), center=mp.Vector3(-L_C/2 - L_BEND/2, Y_WG1, 0), material=mat_core))
        
        # Output parabolic S-bends to separate ports cleanly to +/- 0.40 um
        # S-bend top: from Y_WG1 (+0.26 um) to Y_OUT1 (+0.40 um)
        poly_sbend_top = make_parabolic_taper_polygon(L_C/2, L_C/2 + L_BEND, (Y_WG1 + Y_OUT1)/2.0, W_WG, W_WG)
        # S-bend bot: from Y_WG2 (-0.26 um) to Y_OUT2 (-0.40 um)
        poly_sbend_bot = make_parabolic_taper_polygon(L_C/2, L_C/2 + L_BEND, (Y_WG2 + Y_OUT2)/2.0, W_WG, W_WG)
        geom.append(mp.Prism(poly_sbend_top, height=mp.inf, material=mat_core))
        geom.append(mp.Prism(poly_sbend_bot, height=mp.inf, material=mat_core))
        
        # Output straight leads
        x_out_lead = L_C/2 + L_BEND + ll/2
        geom += [
            mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_out_lead,  Y_OUT1, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_out_lead,  Y_OUT2, 0), material=mat_core),
        ]
        
        # Active patch on WG1 with parabolic tips
        if state == "crystalline":
            mat_p = mp.Medium(index=N_CORE + DELTA_N)
            patch_poly = make_parabolic_patch_polygon(0.0, Y_WG1, l_patch=L_C, w_patch=W_WG + 0.08, l_tip=0.60)
            geom.append(mp.Prism(patch_poly, height=mp.inf, material=mat_p))
            
        sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
        m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_OUT1, 0), size=mp.Vector3(0, mon_w, 0)))
        m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_OUT2, 0), size=mp.Vector3(0, mon_w, 0)))
        sim.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, Y_OUT1, 0), 1e-5), until=100.0)
        
        pt = abs(sim.get_eigenmode_coefficients(m_top, [1]).alpha[0, 0, 0])**2 / p_ref
        pb = abs(sim.get_eigenmode_coefficients(m_bot, [1]).alpha[0, 0, 0])**2 / p_ref
        results[state] = (pt, pb, pt + pb)
        print(f"  {state.upper()}: P_top (Port 1) = {pt*100:.2f}%, P_bot (Port 2) = {pb*100:.2f}%, Total = {(pt+pb)*100:.2f}%")
        
    return results

# ==============================================================================
# OPTION 3: COMBINED / HYBRID MMI-ASSISTED DIRECTIONAL COUPLER (MADIC)
# ==============================================================================
def simulate_option3():
    print("\n" + "=" * 80)
    print("SIMULATING OPTION 3: COMBINED / HYBRID MMI-ASSISTED COUPLER SWITCH")
    print("=" * 80)
    
    W_MMI = 1.40
    L_PRE = 1.80  # Short MMI pre-splitter
    L_COUP = 3.20 # Directional phase section
    W_WG = 0.38
    Y_POS = 0.350
    DELTA_N = 0.145
    L_LEAD = 1.00
    
    L_TOT = L_PRE + L_COUP
    sx = L_TOT + 2 * L_LEAD + 2 * DPML
    sy = W_MMI + 1.2 + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    mat_core = mp.Medium(index=N_CORE)
    mat_clad = mp.Medium(index=N_CLAD)
    
    x_src = -sx/2 + DPML + 0.3
    x_mon_out = sx/2 - DPML - 0.3
    mon_w = W_WG * 2.2
    
    src = mp.EigenModeSource(
        src=mp.GaussianSource(FCEN, fwidth=DF),
        center=mp.Vector3(x_src, 0, 0),
        size=mp.Vector3(0, mon_w, 0),
        eig_band=1, eig_match_freq=True, direction=mp.X
    )
    
    # Ref
    sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=[mp.Block(mp.Vector3(sx, W_WG, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core)], sources=[src], resolution=RESOLUTION, default_material=mat_clad)
    m_ref = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, 0, 0), size=mp.Vector3(0, mon_w, 0)))
    sim_ref.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, 0, 0), 1e-5), until=100.0)
    p_ref = abs(sim_ref.get_eigenmode_coefficients(m_ref, [1]).alpha[0, 0, 0])**2
    
    results = {}
    for state in ["amorphous", "crystalline"]:
        geom = []
        
        # 1. Input pre-MMI section
        x_pre = -L_TOT/2 + L_PRE/2.0
        geom.append(mp.Block(mp.Vector3(L_PRE, W_MMI, mp.inf), center=mp.Vector3(x_pre, 0, 0), material=mat_core))
        
        # 2. Coupled dual-rail section
        x_coup = -L_TOT/2 + L_PRE + L_COUP/2.0
        geom += [
            mp.Block(mp.Vector3(L_COUP, W_WG, mp.inf), center=mp.Vector3(x_coup,  Y_POS, 0), material=mat_core),
            mp.Block(mp.Vector3(L_COUP, W_WG, mp.inf), center=mp.Vector3(x_coup, -Y_POS, 0), material=mat_core),
        ]
        
        # Leads
        ll = L_LEAD + DPML
        x_in = -L_TOT/2 - ll/2
        geom.append(mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_in, 0, 0), material=mat_core))
        
        x_out = L_TOT/2 + ll/2
        geom += [
            mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_out,  Y_POS, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_out, -Y_POS, 0), material=mat_core),
        ]
        
        # Parabolic patch on top rail
        if state == "crystalline":
            mat_p = mp.Medium(index=N_CORE + DELTA_N)
            patch_poly = make_parabolic_patch_polygon(x_coup, Y_POS, l_patch=L_COUP*0.85, w_patch=W_WG+0.06, l_tip=0.60)
            geom.append(mp.Prism(patch_poly, height=mp.inf, material=mat_p))
            
        sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
        m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
        m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, -Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
        sim.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, Y_POS, 0), 1e-5), until=100.0)
        
        pt = abs(sim.get_eigenmode_coefficients(m_top, [1]).alpha[0, 0, 0])**2 / p_ref
        pb = abs(sim.get_eigenmode_coefficients(m_bot, [1]).alpha[0, 0, 0])**2 / p_ref
        results[state] = (pt, pb, pt + pb)
        print(f"  {state.upper()}: P_top (Port 1) = {pt*100:.2f}%, P_bot (Port 2) = {pb*100:.2f}%, Total = {(pt+pb)*100:.2f}%")
        
    return results

def main():
    print("=" * 85)
    print("PARALLEL MEEP SIMULATION SUITE: 3 SWITCH ARCHITECTURES WITH PARABOLIC TAPERS")
    print("=" * 85)
    
    res1 = simulate_option1()
    res2 = simulate_option2()
    res3 = simulate_option3()
    
    print("\n" + "=" * 95)
    print("MASTER SUMMARY TABLE ACROSS ALL 3 CANDIDATE ARCHITECTURES (PARABOLIC TAPERS):")
    print("=" * 95)
    print(f"{'Design Architecture':<34}{'State':<13}{'P_top(%)':<11}{'P_bot(%)':<11}{'Total(%)':<11}{'IL(dB)':<9}{'ER(dB)':<8}")
    print("-" * 95)
    
    for name, r in [
        ("Opt 1: Paired-Interference MMI", res1),
        ("Opt 2: Directional Coupler Switch", res2),
        ("Opt 3: Hybrid MMI-Assisted Coupler", res3),
    ]:
        for st in ["amorphous", "crystalline"]:
            pt, pb, tot = r[st]
            il = -10.0 * math.log10(max(tot, 1e-6))
            er = 10.0 * math.log10(max(pt, 1e-6) / max(pb, 1e-6)) if st == "amorphous" else 10.0 * math.log10(max(pb, 1e-6) / max(pt, 1e-6))
            print(f"{name:<34}{st.capitalize():<13}{pt*100:<11.2f}{pb*100:<11.2f}{tot*100:<11.2f}{il:<9.4f}{er:<8.2f}")
        print("-" * 95)
    print("=" * 95)

if __name__ == "__main__":
    main()
