"""
TOP CONTESTANT MEEP VERIFICATION (340nm Si, 90nm Gap, 4.86° S-Bend)
====================================================================
Parameters:
  - Material: Silicon core (n = 3.565) in SiO2 (n = 1.449)
  - Core width: W_wg = 340 nm (0.34 um)
  - Coupling gap: gap = 90 nm (0.09 um)
  - Port separation: gap_port = 600 nm (0.60 um)
  - S-bend transition: L_taper = 3.0 um (Delta_Y = 0.255 um -> theta = 4.86°)
  - Resolution: 50 px/um (20 nm per grid cell)
"""

import math
import sys
import numpy as np

try:
    import meep as mp
    from meep import mpb
    HAS_MEEP = True
except ImportError:
    HAS_MEEP = False
    print("MEEP not found! Please run in WSL environment.")
    sys.exit(1)

LAMBDA_UM = 1.064
N_SI = 3.565
N_SIO2 = 1.449
N_AM = 2.700
N_CR = 3.300
K_AM = 1.0e-5
K_CR = 1.8e-4

W_WG = 0.340        # 340 nm
GAP = 0.090         # 90 nm
Y_INT = (W_WG + GAP) / 2.0  # 0.215 um

GAP_PORT = 0.600    # 600 nm port gap (isolates uncoupled leads)
Y_PORT = (W_WG + GAP_PORT) / 2.0  # 0.470 um (Delta_Y = 0.255 um)
L_TAPER = 3.000     # 3.0 um S-bend fanout (theta = 4.86 deg)
L_LEAD = 1.200      # 1.2 um straight lead for mode monitors

RESOLUTION = 50     # 50 px/um (20 nm per cell)
DPML = 0.8

# Step 1: MPB Supermode Calibration for Exact L_c
def get_exact_Lc():
    fcen = 1.0 / LAMBDA_UM
    sy = 4.0
    cell = mp.Vector3(0, sy, 0)
    si = mp.Medium(index=N_SI)
    sio2 = mp.Medium(index=N_SIO2)
    sb_am = mp.Medium(index=N_AM)
    
    geom = [
        mp.Block(mp.Vector3(mp.inf, W_WG, mp.inf), center=mp.Vector3(0,  Y_INT, 0), material=si),
        mp.Block(mp.Vector3(mp.inf, W_WG, mp.inf), center=mp.Vector3(0, -Y_INT, 0), material=si),
        mp.Block(mp.Vector3(mp.inf, GAP,  mp.inf), center=mp.Vector3(0, 0, 0), material=sb_am),
    ]
    
    ms = mpb.ModeSolver(geometry_lattice=mp.Lattice(size=cell), geometry=geom, default_material=sio2, resolution=64)
    k1 = ms.find_k(mp.NO_PARITY, fcen, 1, 1, mp.Vector3(1, 0, 0), 1e-5, 3.0*fcen, 2.0*fcen, 3.5*fcen)
    k2 = ms.find_k(mp.NO_PARITY, fcen, 2, 2, mp.Vector3(1, 0, 0), 1e-5, 3.0*fcen, 2.0*fcen, 3.5*fcen)
    
    n_even = k1[0] / fcen
    n_odd = k2[0] / fcen
    dn = abs(n_even - n_odd)
    L_c = LAMBDA_UM / (2.0 * dn) if dn > 0 else 3.62
    print(f"MPB Eigensolve -> n_even = {n_even:.5f}, n_odd = {n_odd:.5f}, Delta_n = {dn:.5f}")
    print(f"Calibrated Exact L_c = {L_c:.3f} um")
    return L_c

def run_fdtd(state, L_c):
    print(f"\n--- Running 2D MEEP FDTD for {state.upper()} State (L_c = {L_c:.3f} um) ---")
    
    n_pcm = N_AM if state == "amorphous" else N_CR
    k_pcm = K_AM if state == "amorphous" else K_CR
    
    fcen = 1.0 / LAMBDA_UM
    df = 0.08 * fcen
    cond = (2 * math.pi * fcen * k_pcm / n_pcm) if n_pcm > 0 else 0.0
    
    si = mp.Medium(index=N_SI)
    sio2 = mp.Medium(index=N_SIO2)
    pcm = mp.Medium(index=n_pcm, D_conductivity=cond)
    
    x_int_l = -L_c / 2.0
    x_int_r =  L_c / 2.0
    x_tap_l = x_int_l - L_TAPER
    x_tap_r = x_int_r + L_TAPER
    x_lead_l = x_tap_l - L_LEAD
    x_lead_r = x_tap_r + L_LEAD
    
    sx = x_lead_r - x_lead_l + 2 * DPML
    sy = 2 * (Y_PORT + W_WG / 2.0 + 0.4) + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    geometry = []
    
    # 1. Port leads
    ll = L_LEAD + DPML
    geometry += [
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_l - ll/2,  Y_PORT, 0), material=si),
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_l - ll/2, -Y_PORT, 0), material=si),
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_r + ll/2,  Y_PORT, 0), material=si),
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_r + ll/2, -Y_PORT, 0), material=si),
    ]
    
    # 2. Gentle 4.86° S-bends
    N_SEG = 25
    dx_seg = L_TAPER / N_SEG
    for i in range(N_SEG):
        s_c = (i + 0.5) / N_SEG
        y_c_l = Y_PORT + (1 - math.cos(math.pi * s_c)) / 2.0 * (Y_INT - Y_PORT)
        xc_l = x_tap_l + s_c * L_TAPER
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_l,  y_c_l, 0), material=si))
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_l, -y_c_l, 0), material=si))
        
        y_c_r = Y_INT + (1 - math.cos(math.pi * s_c)) / 2.0 * (Y_PORT - Y_INT)
        xc_r = x_int_r + s_c * L_TAPER
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_r,  y_c_r, 0), material=si))
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_r, -y_c_r, 0), material=si))
        
    # 3. Interaction region
    geometry += [
        mp.Block(mp.Vector3(L_c, W_WG, mp.inf), center=mp.Vector3(0,  Y_INT, 0), material=si),
        mp.Block(mp.Vector3(L_c, W_WG, mp.inf), center=mp.Vector3(0, -Y_INT, 0), material=si),
        mp.Block(mp.Vector3(L_c, GAP,  mp.inf), center=mp.Vector3(0, 0, 0), material=pcm),
    ]
    
    # Source
    x_src = x_tap_l - L_LEAD / 2.0
    src = mp.EigenModeSource(
        src=mp.GaussianSource(fcen, fwidth=df),
        center=mp.Vector3(x_src, Y_PORT, 0),
        size=mp.Vector3(0, W_WG * 2.0, 0),
        eig_band=1,
        eig_match_freq=True,
        direction=mp.X
    )
    
    sim = mp.Simulation(
        cell_size=cell,
        boundary_layers=[mp.PML(DPML)],
        geometry=geometry,
        sources=[src],
        resolution=RESOLUTION,
        default_material=sio2
    )
    
    mon_w = W_WG * 2.0
    x_mon_in = x_tap_l - L_LEAD * 0.2
    x_mon_out = x_tap_r + L_LEAD * 0.5
    
    m_in = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_in, Y_PORT, 0), size=mp.Vector3(0, mon_w, 0)))
    m_bar = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, Y_PORT, 0), size=mp.Vector3(0, mon_w, 0)))
    m_cross = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, -Y_PORT, 0), size=mp.Vector3(0, mon_w, 0)))
    
    sim.run(mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(x_mon_out, -Y_PORT, 0), 1e-5), until=140.0)
    
    res_in = sim.get_eigenmode_coefficients(m_in, [1])
    res_bar = sim.get_eigenmode_coefficients(m_bar, [1])
    res_cross = sim.get_eigenmode_coefficients(m_cross, [1])
    
    a_in = res_in.alpha[0, 0, 0]
    b_bar = res_bar.alpha[0, 0, 0]
    b_cross = res_cross.alpha[0, 0, 0]
    
    S21 = b_bar / a_in if abs(a_in) > 0 else 0
    S31 = b_cross / a_in if abs(a_in) > 0 else 0
    
    T_bar = abs(S21)**2
    T_cross = abs(S31)**2
    
    if state == "amorphous":
        IL_dB = -10.0 * np.log10(max(T_cross, 1e-12))
        XT_dB = 10.0 * np.log10(max(T_bar, 1e-12))
    else:
        IL_dB = -10.0 * np.log10(max(T_bar, 1e-12))
        XT_dB = 10.0 * np.log10(max(T_cross, 1e-12))
        
    print(f"  T_bar   (Port 1 out) = {T_bar:.4f} ({10*np.log10(max(T_bar,1e-12)):.2f} dB)")
    print(f"  T_cross (Port 2 out) = {T_cross:.4f} ({10*np.log10(max(T_cross,1e-12)):.2f} dB)")
    print(f"  Total Guided Power   = {(T_bar + T_cross)*100:.1f}%")
    print(f"  Insertion Loss (IL)  = {IL_dB:.3f} dB")
    print(f"  Crosstalk (XT)       = {XT_dB:.2f} dB")
    print(f"  Extinction Ratio     = {abs(IL_dB - XT_dB):.2f} dB")
    
    return {"state": state, "T_bar": T_bar, "T_cross": T_cross, "IL_dB": IL_dB, "XT_dB": XT_dB}

def main():
    L_c = get_exact_Lc()
    
    cell_w = 2 * W_WG + GAP_PORT + 0.20
    cell_l = L_c + 2 * L_TAPER
    area = cell_w * cell_l
    tot_area = (3_932_160 * area) / 1e6
    
    print("=" * 65)
    print(f"Cell Dimensions: {cell_w:.2f} um x {cell_l:.2f} um = {area:.2f} um^2")
    print(f"Total 3.93M Switch Die Area: {tot_area:.2f} mm^2 (Target <= 75.0 mm^2)")
    print("=" * 65)
    
    res_am = run_fdtd("amorphous", L_c)
    res_cr = run_fdtd("crystalline", L_c)
    
    print("\n" + "=" * 65)
    print("FINAL FDTD SIMULATION RESULTS:")
    print("=" * 65)
    print(f"  Amorphous (Cross Port Routing): IL = {res_am['IL_dB']:.3f} dB, XT = {res_am['XT_dB']:.2f} dB, Power = {(res_am['T_bar']+res_am['T_cross'])*100:.1f}%")
    print(f"  Crystalline (Bar Port Routing): IL = {res_cr['IL_dB']:.3f} dB, XT = {res_cr['XT_dB']:.2f} dB, Power = {(res_cr['T_bar']+res_cr['T_cross'])*100:.1f}%")
    print("=" * 65)

if __name__ == "__main__":
    main()
