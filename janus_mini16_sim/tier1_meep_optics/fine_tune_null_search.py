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

def sweep_fine_tuning():
    """
    Fine sweep of L_patch_tip and L_c around 3.80 um to find the exact null
    where Crystalline crosstalk and Amorphous crosstalk drop to <= -30 dB.
    """
    w_wg = 0.28
    gap = 0.080
    delta_n = 0.24
    l_bend = 1.60
    
    # We test coupling lengths around 3.80 um with different taper tip lengths
    test_cases = [
        # (l_c, l_tip)
        (3.65, 0.50),
        (3.70, 0.50),
        (3.75, 0.50),
        (3.80, 0.50),
        (3.80, 0.60),
        (3.85, 0.50),
        (3.85, 0.60),
    ]
    
    y_sep_coupler = w_wg + gap
    y_wg1 = y_sep_coupler / 2.0
    y_wg2 = -y_sep_coupler / 2.0
    y_sep_final = 0.80
    y_out1 = y_sep_final / 2.0
    y_out2 = -y_sep_final / 2.0
    l_lead = 1.00
    
    for lc, l_tip in test_cases:
        sx = lc + 2 * l_bend + 2 * l_lead + 2 * DPML
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
        
        # Ref
        geom_ref = [mp.Block(mp.Vector3(sx, w_wg, mp.inf), center=mp.Vector3(0, y_wg1, 0), material=mat_core)]
        sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom_ref, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
        f_ref = sim_ref.add_flux(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_wg1, 0), size=mp.Vector3(0, mon_w, 0)))
        sim_ref.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Ez, mp.Vector3(x_mon_out, y_wg1, 0), 1e-6))
        p_ref = mp.get_fluxes(f_ref)[0]
        
        res = {}
        for state in ["amorphous", "crystalline"]:
            geom = [
                mp.Block(mp.Vector3(lc, w_wg, mp.inf), center=mp.Vector3(0, y_wg1, 0), material=mat_core),
                mp.Block(mp.Vector3(lc, w_wg, mp.inf), center=mp.Vector3(0, y_wg2, 0), material=mat_core),
            ]
            ll = l_lead + DPML
            geom.append(mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(-lc/2 - l_bend - ll/2, y_wg1, 0), material=mat_core))
            geom.append(mp.Block(mp.Vector3(l_bend, w_wg, mp.inf), center=mp.Vector3(-lc/2 - l_bend/2, y_wg1, 0), material=mat_core))
            
            poly_sbend_top = make_true_sbend_polygon(lc/2, lc/2 + l_bend, y_wg1, y_out1, w_wg)
            poly_sbend_bot = make_true_sbend_polygon(lc/2, lc/2 + l_bend, y_wg2, y_out2, w_wg)
            geom.append(mp.Prism(poly_sbend_top, height=mp.inf, material=mat_core))
            geom.append(mp.Prism(poly_sbend_bot, height=mp.inf, material=mat_core))
            
            geom += [
                mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(lc/2 + l_bend + ll/2, y_out1, 0), material=mat_core),
                mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(lc/2 + l_bend + ll/2, y_out2, 0), material=mat_core),
            ]
            
            if state == "crystalline":
                mat_p = mp.Medium(index=N_CORE + delta_n)
                poly_patch = make_parabolic_patch_polygon(0.0, y_wg1, l_patch=lc, w_patch=w_wg, l_tip=l_tip)
                geom.append(mp.Prism(poly_patch, height=mp.inf, material=mat_p))
                
            sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
            f_top = sim.add_flux(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_out1, 0), size=mp.Vector3(0, mon_w, 0)))
            f_bot = sim.add_flux(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_out2, 0), size=mp.Vector3(0, mon_w, 0)))
            
            y_decay = y_out2 if state == "amorphous" else y_out1
            sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Ez, mp.Vector3(x_mon_out, y_decay, 0), 1e-6))
            
            pt = mp.get_fluxes(f_top)[0] / p_ref
            pb = mp.get_fluxes(f_bot)[0] / p_ref
            res[state] = (pt, pb)
            
        p_am_bar, p_am_cross = res["amorphous"]
        p_cr_bar, p_cr_cross = res["crystalline"]
        
        xt_am = 10.0 * math.log10(max(p_am_bar / max(p_am_cross, 1e-6), 1e-6))
        xt_cr = 10.0 * math.log10(max(p_cr_cross / max(p_cr_bar, 1e-6), 1e-6))
        
        print(f"L_c={lc:.2f} um, L_tip={l_tip:.2f} um | AMORPH: Cross={p_am_cross*100:5.2f}%, Bar={p_am_bar*100:5.2f}%, XT={xt_am:6.2f} dB | CRYST: Bar={p_cr_bar*100:5.2f}%, Cross={p_cr_cross*100:5.2f}%, XT={xt_cr:6.2f} dB", flush=True)

if __name__ == "__main__":
    print("Testing fine-tuned null points...")
    sweep_fine_tuning()
