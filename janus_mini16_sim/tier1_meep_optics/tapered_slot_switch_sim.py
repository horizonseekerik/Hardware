"""
TAPERED SLOT-DIRECTIONAL COUPLER SWITCH — MEEP FDTD & MPB
==========================================================
Architecture:
  - Input/Output Ports: 800 nm Si3N4 strips (separated by 1.6 um gap)
  - Input Taper: 800 nm -> 300 nm rails (linear / raised-cosine) over L_taper
  - Interaction Region: Dual 300 nm rails with 100 nm Sb2S3 slot in between
  - Output Taper: 300 nm -> 800 nm rails over L_taper

Step 1: MPB eigensolve on the 300nm-rail + 100nm-slot interaction region to find:
        n_even, n_odd -> L_c = lambda / (2 * (n_even - n_odd))
Step 2: 2D FDTD simulation of the complete structure at the calculated L_c
        for both Amorphous and Crystalline Sb2S3 states.
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

# --- Physical Constants ---
LAMBDA_UM = 1.064
N_SIN = 2.016
N_SIO2 = 1.449
N_AM = 2.700
N_CR = 3.300
K_AM = 1.0e-5
K_CR = 1.8e-4
DELTA_N = N_CR - N_AM

# --- Geometry Dimensions ---
W_PORT_WG = 0.800   # 800 nm port waveguide width
W_RAIL = 0.300      # 300 nm narrow rail in interaction region
W_SLOT = 0.100      # 100 nm Sb2S3 slot width
H_WG = 0.300        # 300 nm Si3N4 height

Y_PORT_GAP = 1.600  # Port separation gap
Y_PORT = (W_PORT_WG + Y_PORT_GAP) / 2.0  # Port center y-position
Y_INT = (W_RAIL + W_SLOT) / 2.0          # Interaction center y-position (0.200 um)

L_TAPER = 3.0       # 3.0 um adiabatic transition length
L_LEAD = 1.0        # Straight lead length for monitors
RESOLUTION = 60     # px/um
DPML = 1.0

# -------------------------------------------------------------
# STEP 1: MPB Supermode Eigensolve for 300nm Rails + 100nm Slot
# -------------------------------------------------------------
def solve_mpb_supermodes():
    print("=" * 60)
    print("STEP 1: MPB Supermode Eigensolve (300nm Rails + 100nm Slot)")
    print("=" * 60)
    
    fcen = 1.0 / LAMBDA_UM
    sy = 4.0
    sz = 2.0
    cell = mp.Vector3(0, sy, sz)
    
    sin = mp.Medium(index=N_SIN)
    sio2 = mp.Medium(index=N_SIO2)
    sb_am = mp.Medium(index=N_AM)
    
    # Dual 300 nm rails + 100 nm Sb2S3 slot
    geom = [
        mp.Block(mp.Vector3(mp.inf, W_RAIL, H_WG), center=mp.Vector3(0, Y_INT, 0), material=sin),
        mp.Block(mp.Vector3(mp.inf, W_RAIL, H_WG), center=mp.Vector3(0, -Y_INT, 0), material=sin),
        mp.Block(mp.Vector3(mp.inf, W_SLOT, H_WG), center=mp.Vector3(0, 0, 0), material=sb_am),
    ]
    
    ms = mpb.ModeSolver(
        geometry_lattice=mp.Lattice(size=cell),
        geometry=geom,
        default_material=sio2,
        resolution=64
    )
    
    # Find k for band 1 (even) and band 2 (odd)
    k_res_even = ms.find_k(mp.NO_PARITY, fcen, 1, 1, mp.Vector3(1, 0, 0), 1e-5, 2.5*fcen, 1.2*fcen, 3.0*fcen)
    n_even = k_res_even[0] / fcen
    
    k_res_odd = ms.find_k(mp.NO_PARITY, fcen, 2, 2, mp.Vector3(1, 0, 0), 1e-5, 2.5*fcen, 1.2*fcen, 3.0*fcen)
    n_odd = k_res_odd[0] / fcen
    
    dn = n_even - n_odd
    L_c = LAMBDA_UM / (2.0 * dn) if dn > 0 else 10.0
    
    print(f"  n_even (symmetric)     = {n_even:.5f}")
    print(f"  n_odd  (antisymmetric) = {n_odd:.5f}")
    print(f"  dn (supermode beat)    = {dn:.5f}")
    print(f"  Exact Coupling Length L_c = {L_c:.3f} um")
    print("=" * 60)
    return L_c, n_even, n_odd

# -------------------------------------------------------------
# STEP 2: 2D FDTD Simulation with 800nm -> 300nm Tapered Ports
# -------------------------------------------------------------
def run_fdtd(state, L_c):
    print(f"\n--- Running 2D FDTD for {state.upper()} State (L = {L_c:.3f} um) ---")
    
    if state == "amorphous":
        n_pcm, k_pcm = N_AM, K_AM
    else:
        n_pcm, k_pcm = N_CR, K_CR
        
    fcen = 1.0 / LAMBDA_UM
    df = 0.08 * fcen
    cond = (2 * math.pi * fcen * k_pcm / n_pcm) if n_pcm > 0 else 0.0
    
    sin = mp.Medium(index=N_SIN)
    sio2 = mp.Medium(index=N_SIO2)
    pcm = mp.Medium(index=n_pcm, D_conductivity=cond)
    
    # Longitudinal Coordinates
    x_int_l = -L_c / 2.0
    x_int_r =  L_c / 2.0
    x_tap_l = x_int_l - L_TAPER
    x_tap_r = x_int_r + L_TAPER
    x_lead_l = x_tap_l - L_LEAD
    x_lead_r = x_tap_r + L_LEAD
    
    sx = x_lead_r - x_lead_l + 2 * DPML
    sy = 2 * (Y_PORT + W_PORT_WG / 2.0 + 0.6) + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    geometry = []
    
    # 1. Straight 800nm Port Leads
    ll = L_LEAD + DPML
    geometry += [
        # Left Ports
        mp.Block(mp.Vector3(ll, W_PORT_WG, mp.inf), center=mp.Vector3(x_tap_l - ll/2,  Y_PORT, 0), material=sin),
        mp.Block(mp.Vector3(ll, W_PORT_WG, mp.inf), center=mp.Vector3(x_tap_l - ll/2, -Y_PORT, 0), material=sin),
        # Right Ports
        mp.Block(mp.Vector3(ll, W_PORT_WG, mp.inf), center=mp.Vector3(x_tap_r + ll/2,  Y_PORT, 0), material=sin),
        mp.Block(mp.Vector3(ll, W_PORT_WG, mp.inf), center=mp.Vector3(x_tap_r + ll/2, -Y_PORT, 0), material=sin),
    ]
    
    # 2. Tapers (800nm @ Y_PORT -> 300nm @ Y_INT)
    N_SEG = 20
    dx_seg = L_TAPER / N_SEG
    for i in range(N_SEG):
        s_lo = i / N_SEG
        s_hi = (i + 1) / N_SEG
        s_c = (s_lo + s_hi) / 2.0
        
        # Linear/cosine interpolation of position and width
        # Left Taper (x: x_tap_l -> x_int_l)
        # s=0 at x_tap_l, s=1 at x_int_l
        w_curr = W_PORT_WG + s_c * (W_RAIL - W_PORT_WG)
        y_curr = Y_PORT + (1 - math.cos(math.pi * s_c)) / 2.0 * (Y_INT - Y_PORT)
        xc_left = x_tap_l + s_c * L_TAPER
        
        # Top and bottom rails on left taper
        geometry.append(mp.Block(mp.Vector3(dx_seg, w_curr, mp.inf), center=mp.Vector3(xc_left,  y_curr, 0), material=sin))
        geometry.append(mp.Block(mp.Vector3(dx_seg, w_curr, mp.inf), center=mp.Vector3(xc_left, -y_curr, 0), material=sin))
        
        # Right Taper (x: x_int_r -> x_tap_r)
        # s_c goes from 0 (at x_int_r) to 1 (at x_tap_r)
        w_curr_r = W_RAIL + s_c * (W_PORT_WG - W_RAIL)
        y_curr_r = Y_INT + (1 - math.cos(math.pi * s_c)) / 2.0 * (Y_PORT - Y_INT)
        xc_right = x_int_r + s_c * L_TAPER
        
        geometry.append(mp.Block(mp.Vector3(dx_seg, w_curr_r, mp.inf), center=mp.Vector3(xc_right,  y_curr_r, 0), material=sin))
        geometry.append(mp.Block(mp.Vector3(dx_seg, w_curr_r, mp.inf), center=mp.Vector3(xc_right, -y_curr_r, 0), material=sin))
        
    # 3. Central Interaction Region (300nm Rails + 100nm Sb2S3 Slot)
    geometry += [
        mp.Block(mp.Vector3(L_c, W_RAIL, mp.inf), center=mp.Vector3(0,  Y_INT, 0), material=sin),
        mp.Block(mp.Vector3(L_c, W_RAIL, mp.inf), center=mp.Vector3(0, -Y_INT, 0), material=sin),
        mp.Block(mp.Vector3(L_c, W_SLOT, mp.inf), center=mp.Vector3(0, 0, 0), material=pcm),
    ]
    
    # Source: Eigenmode in TOP 800nm Port
    x_src = x_tap_l - L_LEAD / 2.0
    src = mp.EigenModeSource(
        src=mp.GaussianSource(fcen, fwidth=df),
        center=mp.Vector3(x_src, Y_PORT, 0),
        size=mp.Vector3(0, W_PORT_WG * 2.5, 0),
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
    
    # Monitors at Ports
    mon_w = W_PORT_WG * 2.5
    x_mon_in = x_tap_l - L_LEAD * 0.2
    x_mon_out = x_tap_r + L_LEAD * 0.5
    
    m_in = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_in, Y_PORT, 0), size=mp.Vector3(0, mon_w, 0)))
    m_bar = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, Y_PORT, 0), size=mp.Vector3(0, mon_w, 0)))
    m_cross = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, -Y_PORT, 0), size=mp.Vector3(0, mon_w, 0)))
    
    # Run
    sim.run(mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(x_mon_out, -Y_PORT, 0), 1e-5), until=180.0)
    
    # Extraction
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
    print(f"  Insertion Loss (IL)  = {IL_dB:.3f} dB")
    print(f"  Crosstalk (XT)       = {XT_dB:.2f} dB")
    print(f"  Extinction Ratio     = {abs(IL_dB - XT_dB):.2f} dB")
    
    return {"state": state, "T_bar": T_bar, "T_cross": T_cross, "IL_dB": IL_dB, "XT_dB": XT_dB}

def main():
    L_c, n_even, n_odd = solve_mpb_supermodes()
    
    res_am = run_fdtd("amorphous", L_c)
    res_cr = run_fdtd("crystalline", L_c)
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS: TAPERED (800nm -> 300nm -> 800nm) SWITCH")
    print("=" * 60)
    print(f"Calculated Interaction Length L_c: {L_c:.3f} um")
    print(f"Amorphous State (Cross Port Routing):")
    print(f"  IL = {res_am['IL_dB']:.3f} dB | XT = {res_am['XT_dB']:.2f} dB | Cross Transmission = {res_am['T_cross']*100:.1f}%")
    print(f"Crystalline State (Bar Port Routing):")
    print(f"  IL = {res_cr['IL_dB']:.3f} dB | XT = {res_cr['XT_dB']:.2f} dB | Bar Transmission = {res_cr['T_bar']*100:.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()
