import math
import numpy as np
import meep as mp
from dc_geom_utils import make_true_sbend_polygon, make_parabolic_patch_polygon

LAMBDA_0 = 1.064
FCEN = 1.0 / LAMBDA_0
DF = 0.08 * FCEN

N_CLAD = 1.449
N_CORE = 2.850  # TE slab effective index

DPML = 0.8
RESOLUTION = 40

def simulate_dc_switch(w_wg=0.28, gap=0.080, l_c=4.40, delta_n=0.22, l_bend=1.60):
    """
    Simulates a 1x2 Directional Coupler Switch in MEEP FDTD.
    Input enters WG1 (top).
    In Amorphous state: Light couples to WG2 (bottom, Cross Port).
    In Crystalline state: Phase mismatch detunes coupling, light stays in WG1 (top, Bar Port).
    """
    y_sep_coupler = w_wg + gap
    y_wg1 = y_sep_coupler / 2.0
    y_wg2 = -y_sep_coupler / 2.0
    
    y_sep_final = 0.80  # Final port separation for low crosstalk
    y_out1 = y_sep_final / 2.0
    y_out2 = -y_sep_final / 2.0
    
    l_lead = 1.00
    sx = l_c + 2 * l_bend + 2 * l_lead + 2 * DPML
    sy = y_sep_final + 1.2 + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    mat_core = mp.Medium(index=N_CORE)
    mat_clad = mp.Medium(index=N_CLAD)
    
    x_src = -sx/2 + DPML + 0.3
    x_mon_out = sx/2 - DPML - 0.3
    mon_w = w_wg * 2.5
    
    # Mode source at input on WG1
    src = mp.EigenModeSource(
        src=mp.GaussianSource(FCEN, fwidth=DF),
        center=mp.Vector3(x_src, y_wg1, 0),
        size=mp.Vector3(0, mon_w, 0),
        eig_band=1, eig_match_freq=True, direction=mp.X
    )
    
    # Reference simulation: single straight waveguide
    geom_ref = [mp.Block(mp.Vector3(sx, w_wg, mp.inf), center=mp.Vector3(0, y_wg1, 0), material=mat_core)]
    sim_ref = mp.Simulation(
        cell_size=cell, boundary_layers=[mp.PML(DPML)],
        geometry=geom_ref, sources=[src],
        resolution=RESOLUTION, default_material=mat_clad
    )
    m_ref = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_wg1, 0), size=mp.Vector3(0, mon_w, 0)))
    sim_ref.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, y_wg1, 0), 1e-5), until=100.0)
    p_ref = abs(sim_ref.get_eigenmode_coefficients(m_ref, [1]).alpha[0, 0, 0])**2
    
    res = {}
    for state in ["amorphous", "crystalline"]:
        geom = []
        
        # 1. Straight coupling region
        geom += [
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(0, y_wg1, 0), material=mat_core),
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(0, y_wg2, 0), material=mat_core),
        ]
        
        # 2. Input straight lead (single port on WG1)
        ll = l_lead + DPML
        x_in_lead = -l_c/2 - l_bend - ll/2
        geom.append(mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_in_lead, y_wg1, 0), material=mat_core))
        # Input section before coupling: WG1 straight
        geom.append(mp.Block(mp.Vector3(l_bend, w_wg, mp.inf), center=mp.Vector3(-l_c/2 - l_bend/2, y_wg1, 0), material=mat_core))
        
        # 3. Output true S-bends separating ports cleanly
        # Top S-bend: from (l_c/2, y_wg1) to (l_c/2 + l_bend, y_out1)
        poly_sbend_top = make_true_sbend_polygon(l_c/2, l_c/2 + l_bend, y_wg1, y_out1, w_wg)
        # Bottom S-bend: from (l_c/2, y_wg2) to (l_c/2 + l_bend, y_out2)
        poly_sbend_bot = make_true_sbend_polygon(l_c/2, l_c/2 + l_bend, y_wg2, y_out2, w_wg)
        geom.append(mp.Prism(poly_sbend_top, height=mp.inf, material=mat_core))
        geom.append(mp.Prism(poly_sbend_bot, height=mp.inf, material=mat_core))
        
        # 4. Output straight leads
        x_out_lead = l_c/2 + l_bend + ll/2
        geom += [
            mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_out_lead, y_out1, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_out_lead, y_out2, 0), material=mat_core),
        ]
        
        # 5. Active PCM patch on WG1 (with parabolic entry/exit tips)
        if state == "crystalline":
            mat_p = mp.Medium(index=N_CORE + delta_n)
            # Patch covers the coupling region with smooth tapered tips
            poly_patch = make_parabolic_patch_polygon(0.0, y_wg1, l_patch=l_c, w_patch=w_wg + 0.08, l_tip=0.60)
            geom.append(mp.Prism(poly_patch, height=mp.inf, material=mat_p))
            
        sim = mp.Simulation(
            cell_size=cell, boundary_layers=[mp.PML(DPML)],
            geometry=geom, sources=[src],
            resolution=RESOLUTION, default_material=mat_clad
        )
        m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_out1, 0), size=mp.Vector3(0, mon_w, 0)))
        m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_out2, 0), size=mp.Vector3(0, mon_w, 0)))
        sim.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, y_out1, 0), 1e-5), until=100.0)
        
        p_top = abs(sim.get_eigenmode_coefficients(m_top, [1]).alpha[0, 0, 0])**2 / p_ref
        p_bot = abs(sim.get_eigenmode_coefficients(m_bot, [1]).alpha[0, 0, 0])**2 / p_ref
        res[state] = (p_top, p_bot, p_top + p_bot)
        
        il_top = -10.0 * math.log10(p_top) if p_top > 1e-6 else 99.0
        il_bot = -10.0 * math.log10(p_bot) if p_bot > 1e-6 else 99.0
        print(f"  {state.upper()}: P_top (Bar, Port 1) = {p_top*100:6.2f}% ({il_top:.3f} dB), P_bot (Cross, Port 2) = {p_bot*100:6.2f}% ({il_bot:.3f} dB), Total = {(p_top+p_bot)*100:6.2f}%")
        
    return res

if __name__ == "__main__":
    print("Running DC Switch test with W=280 nm, Gap=80 nm, L_c=4.40 um...")
    simulate_dc_switch(w_wg=0.28, gap=0.080, l_c=4.40, delta_n=0.22, l_bend=1.60)
