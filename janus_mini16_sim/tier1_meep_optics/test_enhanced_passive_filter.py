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

def make_trench_polygon(x_start, x_end, y_start, y_end):
    """Air trench or deep cladding moat polygon to strip unguided radiation."""
    return [
        mp.Vector3(x_start, y_start, 0),
        mp.Vector3(x_end, y_start, 0),
        mp.Vector3(x_end, y_end, 0),
        mp.Vector3(x_start, y_end, 0),
    ]

def test_enhanced_passive_filters(filter_type="trench_plus_bottleneck"):
    """
    Tests enhanced passive spatial filters outside the switch:
      1. 'deep_bottleneck': Narrower adiabatic bottleneck (170 nm neck)
      2. 'isolation_trench': Air/SiO2 trench between arms to terminate evanescent radiation
      3. 'combined_trench_bottleneck': Air trench isolation + 180 nm adiabatic bottleneck
    """
    print("=" * 80)
    print(f"EVALUATING ENHANCED PASSIVE FILTER: {filter_type.upper()}")
    print("=" * 80)
    
    w_wg = 0.28
    gap = 0.080
    l_c = 3.80
    l_bend = 1.60
    l_filter = 1.80
    delta_n = 0.24
    l_patch_ext = 0.70
    
    y_sep_coupler = w_wg + gap
    y_wg1 = y_sep_coupler / 2.0
    y_wg2 = -y_sep_coupler / 2.0
    y_sep_final = 0.80
    y_out1 = y_sep_final / 2.0
    y_out2 = -y_sep_final / 2.0
    l_lead = 1.00
    
    sx = l_c + 2 * l_bend + l_filter + 2 * l_lead + 2 * DPML
    sy = y_sep_final + 1.4 + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    mat_core = mp.Medium(index=N_CORE)
    mat_clad = mp.Medium(index=N_CLAD)
    mat_air = mp.Medium(index=1.000) # Deep etched air trench
    
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
    f_ref = sim_ref.add_flux(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_wg1, 0), size=mp.Vector3(0, mon_w, 0)))
    sim_ref.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Ez, mp.Vector3(x_mon_out, y_wg1, 0), 1e-6))
    p_ref = mp.get_fluxes(f_ref)[0]
    
    res = {}
    for state in ["amorphous", "crystalline"]:
        geom = []
        x_c_sw = -l_filter / 2.0
        
        # Switch parallel coupling section
        geom += [
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(x_c_sw, y_wg1, 0), material=mat_core),
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(x_c_sw, y_wg2, 0), material=mat_core),
        ]
        
        # Input lead
        ll = l_lead + DPML
        geom.append(mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_c_sw - l_c/2 - l_bend - ll/2, y_wg1, 0), material=mat_core))
        geom.append(mp.Block(mp.Vector3(l_bend, w_wg, mp.inf), center=mp.Vector3(x_c_sw - l_c/2 - l_bend/2, y_wg1, 0), material=mat_core))
        
        # S-bends to separate ports to +/-0.40 um
        x_sb_s = x_c_sw + l_c/2
        x_sb_e = x_sb_s + l_bend
        poly_sb_top = make_true_sbend_polygon(x_sb_s, x_sb_e, y_wg1, y_out1, w_wg)
        poly_sb_bot = make_true_sbend_polygon(x_sb_s, x_sb_e, y_wg2, y_out2, w_wg)
        geom.append(mp.Prism(poly_sb_top, height=mp.inf, material=mat_core))
        geom.append(mp.Prism(poly_sb_bot, height=mp.inf, material=mat_core))
        
        # Passive Filter Section:
        x_f_s = x_sb_e
        x_f_e = x_f_s + l_filter
        
        w_neck = 0.18 if "bottleneck" in filter_type else w_wg
        u_vals = np.linspace(0, 1, 15)
        x_vals = x_f_s + u_vals * l_filter
        w_vals = w_wg - (w_wg - w_neck) * 4.0 * u_vals * (1.0 - u_vals)
        
        top_f1 = [mp.Vector3(x, y_out1 + w/2.0, 0) for x, w in zip(x_vals, w_vals)]
        bot_f1 = [mp.Vector3(x, y_out1 - w/2.0, 0) for x, w in reversed(list(zip(x_vals, w_vals)))]
        geom.append(mp.Prism(top_f1 + bot_f1, height=mp.inf, material=mat_core))
        
        top_f2 = [mp.Vector3(x, y_out2 + w/2.0, 0) for x, w in zip(x_vals, w_vals)]
        bot_f2 = [mp.Vector3(x, y_out2 - w/2.0, 0) for x, w in reversed(list(zip(x_vals, w_vals)))]
        geom.append(mp.Prism(top_f2 + bot_f2, height=mp.inf, material=mat_core))
        
        # Deep Isolation Air Trench between the two output ports (absorbs/scatters all stray inter-port radiation!)
        if "trench" in filter_type:
            # Trench spans y in [-0.20, +0.20], x from x_sb_s + 0.4 to x_f_e
            poly_tr = make_trench_polygon(x_sb_s + 0.40, x_f_e, -0.15, +0.15)
            geom.append(mp.Prism(poly_tr, height=mp.inf, material=mat_air))
            
        # Output leads
        geom += [
            mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_f_e + ll/2, y_out1, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_f_e + ll/2, y_out2, 0), material=mat_core),
        ]
        
        # Active patch on WG1 (Crystalline state) with 700 nm S-bend detuning extension
        if state == "crystalline":
            mat_p = mp.Medium(index=N_CORE + delta_n)
            l_p_tot = l_c + 2 * l_patch_ext
            poly_patch = make_parabolic_patch_polygon(x_c_sw, y_wg1, l_patch=l_p_tot, w_patch=w_wg, l_tip=0.60)
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
    
    il_am = -10.0 * math.log10(max(p_am_cross, 1e-6))
    il_cr = -10.0 * math.log10(max(p_cr_bar, 1e-6))
    xt_am = 10.0 * math.log10(max(p_am_bar / max(p_am_cross, 1e-6), 1e-6))
    xt_cr = 10.0 * math.log10(max(p_cr_cross / max(p_cr_bar, 1e-6), 1e-6))
    
    print(f"\nRESULTS FOR {filter_type.upper()}:")
    print(f"  AMORPHOUS   -> Port 2 (Cross): {p_am_cross*100:6.2f}% (IL = {il_am:.3f} dB), Port 1 (Bar): {p_am_bar*100:6.4f}%, Crosstalk = {xt_am:6.2f} dB")
    print(f"  CRYSTALLINE -> Port 1 (Bar)  : {p_cr_bar*100:6.2f}% (IL = {il_cr:.3f} dB), Port 2 (Cross): {p_cr_cross*100:6.4f}%, Crosstalk = {xt_cr:6.2f} dB")
    return res

if __name__ == "__main__":
    # Test 1: Deep Isolation Air Trench + 180 nm Adiabatic Bottleneck
    test_enhanced_passive_filters(filter_type="combined_trench_bottleneck")
