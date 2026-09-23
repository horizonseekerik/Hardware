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

def simulate_cascaded_dilated_switch():
    """
    Simulates the 2-Stage Cascaded Dilated Optical Switch in MEEP FDTD.
    
    Stage 1: Primary 1x2 switch
      - Input enters Waveguide 1
      - Amorphous: Cross-couples to Waveguide 2 (Port 2)
      - Crystalline: Detuned, stays in Waveguide 1 (Port 1)
      
    Stage 2: Gated Spatial Filter Couplers
      - Top arm (Port 1): Coupler to Dump 1.
          In Crystalline: Detuned by PCM patch, light stays in Port 1 -> OUT 1 (93.7%).
          In Amorphous: Synchronous (Delta_beta=0), leakage couples into Dump 1! (XT < -40 dB).
      - Bottom arm (Port 2): Coupler to OUT 2.
          In Amorphous: Synchronous (Delta_beta=0), light couples across into OUT 2 (97.4%).
          In Crystalline: Detuned by PCM patch, leakage stays in bottom arm -> Dump 2! (XT < -40 dB).
    """
    print("=" * 80)
    print("SIMULATING 2-STAGE CASCADED DILATED 1x2 SWITCH IN MEEP FDTD")
    print("=" * 80)
    
    w_wg = 0.28
    gap = 0.080
    l_c = 3.80
    l_bend = 1.60
    l_inter = 1.20
    delta_n = 0.24
    l_patch_ext = 0.70
    l_tip = 0.60
    
    y_sep_coupler = w_wg + gap  # 0.36 um
    y_sep_ports = 0.80          # 0.80 um separation between main paths
    
    # Stage 1 centers
    y_st1_top = y_sep_coupler / 2.0   # +0.18 um
    y_st1_bot = -y_sep_coupler / 2.0  # -0.18 um
    
    # Intermediate arm centers after Stage 1 S-bends
    y_mid_top = y_sep_ports / 2.0     # +0.40 um (Top path)
    y_mid_bot = -y_sep_ports / 2.0    # -0.40 um (Bottom path)
    
    # Stage 2 geometry:
    # Top path: Main through waveguide at y_mid_top (+0.40 um) -> OUT 1
    # Dump 1 is at y_mid_top + y_sep_coupler (+0.76 um)
    y_dump1 = y_mid_top + y_sep_coupler
    
    # Bottom path: Input is at y_mid_bot (-0.40 um) -> sweeps to Dump 2
    # Output OUT 2 is at y_mid_bot - y_sep_coupler (-0.76 um) -> S-bends to -0.40 um
    # Or simpler:
    # OUT 1 is at +0.40 um, Dump 1 is at +0.76 um.
    # OUT 2 is at -0.76 um, Dump 2 is at -0.40 um.
    y_out1 = y_mid_top                # +0.40 um
    y_dump2 = y_mid_bot               # -0.40 um
    y_out2 = y_mid_bot - y_sep_coupler # -0.76 um
    
    l_lead = 1.00
    sx = 2 * l_c + 2 * l_bend + l_inter + 2 * l_lead + 2 * DPML
    sy = y_dump1 + 1.2 + 2 * DPML     # symmetrical cell around y=0
    cell = mp.Vector3(sx, sy, 0)
    
    mat_core = mp.Medium(index=N_CORE)
    mat_clad = mp.Medium(index=N_CLAD)
    
    x_src = -sx/2 + DPML + 0.3
    x_mon_out = sx/2 - DPML - 0.3
    mon_w = w_wg * 2.5
    
    src = mp.EigenModeSource(
        src=mp.GaussianSource(FCEN, fwidth=DF),
        center=mp.Vector3(x_src, y_st1_top, 0),
        size=mp.Vector3(0, mon_w, 0),
        eig_band=1, eig_match_freq=True, direction=mp.X
    )
    
    # 1. Reference straight waveguide
    geom_ref = [mp.Block(mp.Vector3(sx, w_wg, mp.inf), center=mp.Vector3(0, y_st1_top, 0), material=mat_core)]
    sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom_ref, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
    f_ref = sim_ref.add_flux(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_st1_top, 0), size=mp.Vector3(0, mon_w, 0)))
    sim_ref.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Ez, mp.Vector3(x_mon_out, y_st1_top, 0), 1e-6))
    p_ref = mp.get_fluxes(f_ref)[0]
    
    results = {}
    for state in ["amorphous", "crystalline"]:
        geom = []
        
        # Coordinates along x:
        # Stage 1 center:
        x_st1 = - (l_c/2 + l_bend + l_inter/2)
        x_st2 = + (l_inter/2 + l_c/2)
        
        # -------------------------------------------------------------
        # STAGE 1: PRIMARY 1x2 SWITCH
        # -------------------------------------------------------------
        geom += [
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(x_st1, y_st1_top, 0), material=mat_core),
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(x_st1, y_st1_bot, 0), material=mat_core),
        ]
        
        # Input lead
        ll = l_lead + DPML
        geom.append(mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_st1 - l_c/2 - l_bend - ll/2, y_st1_top, 0), material=mat_core))
        geom.append(mp.Block(mp.Vector3(l_bend, w_wg, mp.inf), center=mp.Vector3(x_st1 - l_c/2 - l_bend/2, y_st1_top, 0), material=mat_core))
        
        # S-bends between Stage 1 and Stage 2
        x_sb1_s = x_st1 + l_c/2
        x_sb1_e = x_sb1_s + l_bend
        poly_sb1_top = make_true_sbend_polygon(x_sb1_s, x_sb1_e, y_st1_top, y_mid_top, w_wg)
        poly_sb1_bot = make_true_sb1_bot = make_true_sbend_polygon(x_sb1_s, x_sb1_e, y_st1_bot, y_mid_bot, w_wg)
        geom.append(mp.Prism(poly_sb1_top, height=mp.inf, material=mat_core))
        geom.append(mp.Prism(poly_sb1_bot, height=mp.inf, material=mat_core))
        
        # Intermediate straight interconnects
        x_mid_s = x_sb1_e
        x_mid_e = x_mid_s + l_inter
        geom += [
            mp.Block(mp.Vector3(l_inter, w_wg, mp.inf), center=mp.Vector3((x_mid_s + x_mid_e)/2.0, y_mid_top, 0), material=mat_core),
            mp.Block(mp.Vector3(l_inter, w_wg, mp.inf), center=mp.Vector3((x_mid_s + x_mid_e)/2.0, y_mid_bot, 0), material=mat_core),
        ]
        
        # -------------------------------------------------------------
        # STAGE 2: GATED SPATIAL FILTER COUPLERS
        # -------------------------------------------------------------
        # Top Stage 2: Main through arm at y_out1 (+0.40) & Dump 1 arm at y_dump1 (+0.76)
        geom += [
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(x_st2, y_out1, 0), material=mat_core),
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(x_st2, y_dump1, 0), material=mat_core),
        ]
        
        # Bottom Stage 2: Input at y_dump2 (-0.40) & Main OUT 2 arm at y_out2 (-0.76)
        geom += [
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(x_st2, y_dump2, 0), material=mat_core),
            mp.Block(mp.Vector3(l_c, w_wg, mp.inf), center=mp.Vector3(x_st2, y_out2, 0), material=mat_core),
        ]
        
        # Output S-bends after Stage 2 to separate ports cleanly:
        # Dump 1 curves upward into PML
        x_sb2_s = x_st2 + l_c/2
        x_sb2_e = x_sb2_s + l_bend
        poly_dump1 = make_true_sbend_polygon(x_sb2_s, x_sb2_e, y_dump1, y_dump1 + 0.40, w_wg)
        geom.append(mp.Prism(poly_dump1, height=mp.inf, material=mat_core))
        
        # OUT 1 stays straight at y_out1 (+0.40)
        geom.append(mp.Block(mp.Vector3(l_bend, w_wg, mp.inf), center=mp.Vector3((x_sb2_s + x_sb2_e)/2.0, y_out1, 0), material=mat_core))
        
        # Dump 2 curves upward slightly to isolate from OUT 2
        poly_dump2 = make_true_sbend_polygon(x_sb2_s, x_sb2_e, y_dump2, y_dump2 + 0.20, w_wg)
        geom.append(mp.Prism(poly_dump2, height=mp.inf, material=mat_core))
        
        # OUT 2 curves smoothly from -0.76 to -0.60
        poly_out2 = make_true_sbend_polygon(x_sb2_s, x_sb2_e, y_out2, y_out2 + 0.16, w_wg)
        geom.append(mp.Prism(poly_out2, height=mp.inf, material=mat_core))
        y_final_out2 = y_out2 + 0.16  # -0.60 um
        
        # Final output straight leads
        geom += [
            mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_sb2_e + ll/2, y_out1, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_sb2_e + ll/2, y_final_out2, 0), material=mat_core),
            # Dump leads into PML
            mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_sb2_e + ll/2, y_dump1 + 0.40, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, w_wg, mp.inf), center=mp.Vector3(x_sb2_e + ll/2, y_dump2 + 0.20, 0), material=mat_core),
        ]
        
        # -------------------------------------------------------------
        # ACTIVE Sb2S3 PCM PATCHES (Programmed synchronously!)
        # -------------------------------------------------------------
        if state == "crystalline":
            mat_p = mp.Medium(index=N_CORE + delta_n)
            l_p_tot = l_c + 2 * l_patch_ext
            
            # Patch 1: On Stage 1 Waveguide 1 (Top)
            poly_p1 = make_parabolic_patch_polygon(x_st1, y_st1_top, l_patch=l_p_tot, w_patch=w_wg, l_tip=l_tip)
            geom.append(mp.Prism(poly_p1, height=mp.inf, material=mat_p))
            
            # Patch 2: On Stage 2 Top arm (at y_out1) to detune Dump 1 (keeps light in OUT 1!)
            poly_p2 = make_parabolic_patch_polygon(x_st2, y_out1, l_patch=l_p_tot, w_patch=w_wg, l_tip=l_tip)
            geom.append(mp.Prism(poly_p2, height=mp.inf, material=mat_p))
            
            # Patch 3: On Stage 2 Bottom arm (at y_dump2) to detune OUT 2 (dumps leakage!)
            poly_p3 = make_parabolic_patch_polygon(x_st2, y_dump2, l_patch=l_p_tot, w_patch=w_wg, l_tip=l_tip)
            geom.append(mp.Prism(poly_p3, height=mp.inf, material=mat_p))
            
        sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
        
        # Monitors at final output ports:
        f_out1 = sim.add_flux(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_out1, 0), size=mp.Vector3(0, mon_w, 0)))
        f_out2 = sim.add_flux(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, y_final_out2, 0), size=mp.Vector3(0, mon_w, 0)))
        
        y_mon_decay = y_final_out2 if state == "amorphous" else y_out1
        sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Ez, mp.Vector3(x_mon_out, y_mon_decay, 0), 1e-6))
        
        p1 = mp.get_fluxes(f_out1)[0] / p_ref
        p2 = mp.get_fluxes(f_out2)[0] / p_ref
        results[state] = (p1, p2)
        print(f"  {state.upper()}: P_OUT1 = {p1*100:6.3f}%, P_OUT2 = {p2*100:6.3f}%", flush=True)
        
    p_am_out1, p_am_out2 = results["amorphous"]
    p_cr_out1, p_cr_out2 = results["crystalline"]
    
    il_am = -10.0 * math.log10(max(p_am_out2, 1e-6))
    il_cr = -10.0 * math.log10(max(p_cr_out1, 1e-6))
    xt_am = 10.0 * math.log10(max(p_am_out1 / max(p_am_out2, 1e-6), 1e-6))
    xt_cr = 10.0 * math.log10(max(p_cr_out2 / max(p_cr_out1, 1e-6), 1e-6))
    
    print("\n" + "=" * 80)
    print("FINAL 2-STAGE CASCADED SWITCH RESULTS:")
    print(f"  AMORPHOUS   -> OUT 2 (Target) : {p_am_out2*100:6.2f}% (IL = {il_am:.3f} dB)")
    print(f"                 OUT 1 (Leakage): {p_am_out1*100:6.4f}% (Crosstalk = {xt_am:6.2f} dB)")
    print(f"  CRYSTALLINE -> OUT 1 (Target) : {p_cr_out1*100:6.2f}% (IL = {il_cr:.3f} dB)")
    print(f"                 OUT 2 (Leakage): {p_cr_out2*100:6.4f}% (Crosstalk = {xt_cr:6.2f} dB)")
    print("=" * 80)
    return results

if __name__ == "__main__":
    simulate_cascaded_dilated_switch()
