import math
import numpy as np
import meep as mp
from dc_geom_utils import make_true_sbend_polygon, make_parabolic_patch_polygon

LAMBDA_0 = 1.064
FCEN = 1.0 / LAMBDA_0
DF = 0.08 * FCEN
N_CLAD = 1.449
N_CORE = 2.850
DPML = 0.8
RESOLUTION = 40

def simulate_dc_point(w_wg=0.28, gap=0.080, l_c=4.20, delta_n=0.24, l_bend=1.60):
    y_sep_coupler = w_wg + gap
    y_wg1 = y_sep_coupler / 2.0
    y_wg2 = -y_sep_coupler / 2.0
    
    y_sep_final = 0.80
    y_out1 = y_sep_final / 2.0
    y_out2 = -y_sep_final / 2.0
    
    l_lead = 1.00
    sx = l_c + 2 * l_bend + 2 * l_lead + 2 * DPML
    sy = y_sep_final + 1.4 + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    mat_core = mp.Medium(index=N_CORE)
    mat_clad = mp.Medium(index=N_CLAD)
    
    x_src = -sx/2 + DPML + 0.3
    x_mon_out = sx/2 - DPML - 0.3
    mon_w = w_wg * 2.5
    
    src = mp.EigenModeSource(
        src=mp.GaussianSource(FCEN, fwidth=DF),
        center=mp.Vector3(x_src, y_wg1, 0),
        size=mp.Vector3(0, mon_w, 0),
        eig_band=1, eig_match_freq=True, direction=mp.X
    )
    
    # 1. Reference straight waveguide
    geom_ref = [mp.Block(mp.Vector3(sx, w_wg, mp.inf), center=mp.Vector3(0, y_wg1, 0), material=mat_core)]
    sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom_ref, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
    mon_ref_flux = sim_ref.add_flux(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_wg1, 0), size=mp.Vector3(0, mon_w, 0)))
    sim_ref.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Ez, mp.Vector3(x_mon_out, y_wg1, 0), 1e-6))
    p_ref = mp.get_fluxes(mon_ref_flux)[0]
    
    results = {}
    for state in ["amorphous", "crystalline"]:
        geom = []
        
        # Coupling parallel guides
        geom += [
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(0, y_wg1, 0), material=mat_core),
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(0, y_wg2, 0), material=mat_core),
        ]
        
        # Input straight lead (single port on WG1)
        ll = l_lead + DPML
        x_in_lead = -l_c/2 - l_bend - ll/2
        geom.append(mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_in_lead, y_wg1, 0), material=mat_core))
        geom.append(mp.Block(mp.Vector3(l_bend, w_wg, mp.inf), center=mp.Vector3(-l_c/2 - l_bend/2, y_wg1, 0), material=mat_core))
        
        # Output true continuous S-bends
        poly_sbend_top = make_true_sbend_polygon(l_c/2, l_c/2 + l_bend, y_wg1, y_out1, w_wg)
        poly_sbend_bot = make_true_sbend_polygon(l_c/2, l_c/2 + l_bend, y_wg2, y_out2, w_wg)
        geom.append(mp.Prism(poly_sbend_top, height=mp.inf, material=mat_core))
        geom.append(mp.Prism(poly_sbend_bot, height=mp.inf, material=mat_core))
        
        # Output straight leads
        x_out_lead = l_c/2 + l_bend + ll/2
        geom += [
            mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_out_lead, y_out1, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_out_lead, y_out2, 0), material=mat_core),
        ]
        
        # Active patch on WG1 (Crystalline state)
        # CRITICAL: Keep patch width = w_wg and centered on WG1 so it NEVER overlaps the gap!
        if state == "crystalline":
            mat_p = mp.Medium(index=N_CORE + delta_n)
            # Patch covers coupling section with 0.5 um smooth parabolic tips
            poly_patch = make_parabolic_patch_polygon(0.0, y_wg1, l_patch=l_c, w_patch=w_wg, l_tip=0.50)
            geom.append(mp.Prism(poly_patch, height=mp.inf, material=mat_p))
            
        sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
        f_top = sim.add_flux(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_out1, 0), size=mp.Vector3(0, mon_w, 0)))
        f_bot = sim.add_flux(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_out2, 0), size=mp.Vector3(0, mon_w, 0)))
        
        # Monitor decay on the dominant port to avoid premature stop
        y_mon_decay = y_out2 if state == "amorphous" else y_out1
        sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Ez, mp.Vector3(x_mon_out, y_mon_decay, 0), 1e-6))
        
        p_top = mp.get_fluxes(f_top)[0] / p_ref
        p_bot = mp.get_fluxes(f_bot)[0] / p_ref
        results[state] = (p_top, p_bot, p_top + p_bot)
        
    return results

if __name__ == "__main__":
    print("=" * 80)
    print("DIRECTIONAL COUPLER 1x2 SWITCH: L_c SWEEP FOR >90% IN BOTH STATES")
    print("=" * 80)
    
    for lc in [3.80, 4.00, 4.20, 4.40]:
        res = simulate_dc_point(w_wg=0.28, gap=0.080, l_c=lc, delta_n=0.24, l_bend=1.60)
        p_am_bar, p_am_cross, p_am_tot = res["amorphous"]
        p_cr_bar, p_cr_cross, p_cr_tot = res["crystalline"]
        
        il_am = -10.0 * math.log10(max(p_am_cross, 1e-5))
        il_cr = -10.0 * math.log10(max(p_cr_bar, 1e-5))
        er_am = 10.0 * math.log10(max(p_am_cross, 1e-5) / max(p_am_bar, 1e-5))
        er_cr = 10.0 * math.log10(max(p_cr_bar, 1e-5) / max(p_cr_cross, 1e-5))
        
        print(f"\n--- L_c = {lc:.2f} um ---")
        print(f"  AMORPHOUS   -> Port 2 (Cross): {p_am_cross*100:5.2f}% (IL={il_am:.3f} dB), Port 1 (Bar): {p_am_bar*100:5.2f}%, ER={er_am:.2f} dB, Total={p_am_tot*100:5.2f}%")
        print(f"  CRYSTALLINE -> Port 1 (Bar)  : {p_cr_bar*100:5.2f}% (IL={il_cr:.3f} dB), Port 2 (Cross): {p_cr_cross*100:5.2f}%, ER={er_cr:.2f} dB, Total={p_cr_tot*100:5.2f}%")
