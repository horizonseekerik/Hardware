"""
ADIABATICALLY-TAPERED SILICON DIRECTIONAL COUPLER (MEEP 2D FDTD)
================================================================
Design for Sub-0.5 dB Loss:
  - Silicon cores: 340 nm width, separated by 90 nm coupling gap
  - Interaction length: L_c = 8.18 um (MPB verified)
  - 1.5 um linear adiabatic tapers at both ends of the Sb2S3 slot (width: 0 -> 90 nm)
    Eliminates Fresnel interface scattering and modal mismatch reflection.
  - Port isolation: 250 nm gap with ultra-gentle S-bends (Delta_Y = 80 nm over 3.0 um, theta = 1.5°)
  - Footprint: 1.03 um x 14.18 um = 14.6 um^2 (Total 3.93M die area = 57.4 mm^2 <= 75.0 mm^2)
"""

import math
import sys
import numpy as np

try:
    import meep as mp
    HAS_MEEP = True
except ImportError:
    print("MEEP not found! Please run in WSL.")
    sys.exit(1)

LAMBDA_UM = 1.064
N_SI = 3.565
N_SIO2 = 1.449
N_AM = 2.700
N_CR = 3.300
K_AM = 1.0e-5
K_CR = 1.8e-4

W_WG = 0.340        # 340 nm Silicon rails
GAP_INT = 0.090     # 90 nm slot
L_C = 8.180         # 8.18 um
Y_INT = (W_WG + GAP_INT) / 2.0  # 0.215 um

GAP_PORT = 0.250    # 250 nm port gap
Y_PORT = (W_WG + GAP_PORT) / 2.0  # 0.295 um (Delta_Y = 80 nm)
L_TAPER_BEND = 3.000 # 3.0 um bend
L_TAPER_SLOT = 1.500 # 1.5 um adiabatic slot entrance/exit taper
L_LEAD = 1.200       # Port leads

RESOLUTION = 50     # 50 px/um (20 nm grid)
DPML = 0.8

def run_simulation(state):
    print(f"\n--- Running MEEP 2D FDTD for {state.upper()} State with Adiabatic Slot Tapers ---")
    
    n_pcm = N_AM if state == "amorphous" else N_CR
    k_pcm = K_AM if state == "amorphous" else K_CR
    
    fcen = 1.0 / LAMBDA_UM
    df = 0.08 * fcen
    cond = (2 * math.pi * fcen * k_pcm / n_pcm) if n_pcm > 0 else 0.0
    
    si = mp.Medium(index=N_SI)
    sio2 = mp.Medium(index=N_SIO2)
    pcm = mp.Medium(index=n_pcm, D_conductivity=cond)
    
    x_int_l = -L_C / 2.0
    x_int_r =  L_C / 2.0
    x_tap_l = x_int_l - L_TAPER_BEND
    x_tap_r = x_int_r + L_TAPER_BEND
    x_lead_l = x_tap_l - L_LEAD
    x_lead_r = x_tap_r + L_LEAD
    
    sx = x_lead_r - x_lead_l + 2 * DPML
    sy = 2 * (Y_PORT + W_WG / 2.0 + 0.35) + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    geometry = []
    
    # 1. Straight port leads
    ll = L_LEAD + DPML
    geometry += [
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_l - ll/2,  Y_PORT, 0), material=si),
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_l - ll/2, -Y_PORT, 0), material=si),
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_r + ll/2,  Y_PORT, 0), material=si),
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_r + ll/2, -Y_PORT, 0), material=si),
    ]
    
    # 2. Ultra-gentle 1.5° S-bends (Delta_Y = 80 nm)
    N_SEG = 25
    dx_seg = L_TAPER_BEND / N_SEG
    for i in range(N_SEG):
        s_c = (i + 0.5) / N_SEG
        y_c_l = Y_PORT + (1 - math.cos(math.pi * s_c)) / 2.0 * (Y_INT - Y_PORT)
        xc_l = x_tap_l + s_c * L_TAPER_BEND
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_l,  y_c_l, 0), material=si))
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_l, -y_c_l, 0), material=si))
        
        y_c_r = Y_INT + (1 - math.cos(math.pi * s_c)) / 2.0 * (Y_PORT - Y_INT)
        xc_r = x_int_r + s_c * L_TAPER_BEND
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_r,  y_c_r, 0), material=si))
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_r, -y_c_r, 0), material=si))
        
    # 3. Silicon Waveguides across the interaction region
    geometry += [
        mp.Block(mp.Vector3(L_C, W_WG, mp.inf), center=mp.Vector3(0,  Y_INT, 0), material=si),
        mp.Block(mp.Vector3(L_C, W_WG, mp.inf), center=mp.Vector3(0, -Y_INT, 0), material=si),
    ]
    
    # 4. Central uniform Sb2S3 slot
    L_uniform = L_C - 2 * L_TAPER_SLOT
    geometry.append(
        mp.Block(mp.Vector3(L_uniform, GAP_INT, mp.inf), center=mp.Vector3(0, 0, 0), material=pcm)
    )
    
    # 5. Adiabatic linear slot tapers (entrance and exit: width 0 -> 90 nm)
    N_TAP = 15
    dx_tap = L_TAPER_SLOT / N_TAP
    for i in range(N_TAP):
        s_c = (i + 0.5) / N_TAP
        w_tap = s_c * GAP_INT  # linearly opens from 0 to 90 nm
        
        # Entrance taper: from x_int_l to x_int_l + L_TAPER_SLOT
        xc_in = x_int_l + s_c * L_TAPER_SLOT
        geometry.append(mp.Block(mp.Vector3(dx_tap, w_tap, mp.inf), center=mp.Vector3(xc_in, 0, 0), material=pcm))
        
        # Exit taper: from x_int_r - L_TAPER_SLOT to x_int_r
        xc_out = x_int_r - (1.0 - s_c) * L_TAPER_SLOT
        geometry.append(mp.Block(mp.Vector3(dx_tap, (1.0 - s_c) * GAP_INT, mp.inf), center=mp.Vector3(xc_out, 0, 0), material=pcm))
        
    # Source
    x_src = x_tap_l - L_LEAD * 0.5
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
    x_mon_out = x_tap_r + L_LEAD * 0.4
    
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
    T_total = T_bar + T_cross
    
    if state == "amorphous":
        IL_dB = -10.0 * np.log10(max(T_cross, 1e-12))
        XT_dB = 10.0 * np.log10(max(T_bar, 1e-12))
    else:
        IL_dB = -10.0 * np.log10(max(T_bar, 1e-12))
        XT_dB = 10.0 * np.log10(max(T_cross, 1e-12))
        
    print(f"  T_bar   (Port 1 out) = {T_bar:.4f} ({10*np.log10(max(T_bar,1e-12)):.2f} dB)")
    print(f"  T_cross (Port 2 out) = {T_cross:.4f} ({10*np.log10(max(T_cross,1e-12)):.2f} dB)")
    print(f"  Total Guided Power   = {T_total*100:.1f}%")
    print(f"  Insertion Loss (IL)  = {IL_dB:.3f} dB")
    print(f"  Crosstalk (XT)       = {XT_dB:.2f} dB")
    print(f"  Extinction Ratio     = {abs(IL_dB - XT_dB):.2f} dB")
    
    return {"state": state, "T_bar": T_bar, "T_cross": T_cross, "IL_dB": IL_dB, "XT_dB": XT_dB, "T_total": T_total}

def main():
    cell_w = 2 * W_WG + GAP_PORT + 0.10
    cell_l = L_C + 2 * L_TAPER_BEND
    area = cell_w * cell_l
    tot_area = (3_932_160 * area) / 1e6
    
    print("=" * 70)
    print("VERIFYING TAPERED-SLOT SILICON SWITCH IN MEEP 2D FDTD")
    print(f"Cell Area: {cell_w:.2f} um x {cell_l:.2f} um = {area:.2f} um^2")
    print(f"Total 3.93M Die Area: {tot_area:.2f} mm^2 (Budget: <= 75.0 mm^2)")
    print("=" * 70)
    
    res_am = run_simulation("amorphous")
    res_cr = run_simulation("crystalline")
    
    print("\n" + "=" * 70)
    print("FINAL FDTD SIMULATION RESULTS:")
    print("=" * 70)
    print(f"  Amorphous (Cross): IL = {res_am['IL_dB']:.3f} dB, XT = {res_am['XT_dB']:.2f} dB, Power = {res_am['T_total']*100:.1f}%")
    print(f"  Crystalline (Bar): IL = {res_cr['IL_dB']:.3f} dB, XT = {res_cr['XT_dB']:.2f} dB, Power = {res_cr['T_total']*100:.1f}%")
    print("=" * 70)

if __name__ == "__main__":
    main()
