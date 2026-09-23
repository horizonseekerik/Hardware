"""
VERIFICATION OF OPTIMAL SILICON SWITCH DESIGN (MEEP 2D FDTD)
============================================================
Optimal parameters from design space explorer:
  - Material: Silicon core (n = 3.565) in SiO2 (n = 1.449)
  - Operating wavelength: lambda_0 = 1.064 um
  - Core width: W_wg = 380 nm (0.38 um)
  - Coupling gap: gap = 100 nm (0.10 um)
  - Interaction length: L_c = 3.95 um
  - Sb2S3 PCM: n_am = 2.70, n_cr = 3.30
  - Cell width: 1.36 um
  - Cell length: 8.37 um
  - Footprint: 11.4 um^2 (3.93M switches = 44.8 mm^2 <= 75 mm^2)
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

W_WG = 0.380       # 380 nm
GAP = 0.100        # 100 nm
L_C = 3.950        # 3.95 um
Y_INT = (W_WG + GAP) / 2.0  # 0.240 um

# Port geometry: S-bend flares ports out to 1.0 um gap to isolate ports
GAP_PORT = 1.000   # 1.0 um gap at ports
Y_PORT = (W_WG + GAP_PORT) / 2.0  # 0.690 um
L_TAPER = 2.200    # 2.2 um S-bend fanout (R ~ 6 um in Silicon, ultra-low loss)
L_LEAD = 1.000     # Straight port lead for monitors

RESOLUTION = 40    # 40 px/um (25 nm per pixel)
DPML = 0.8

def run_fdtd(state):
    print(f"\n--- Running 2D MEEP FDTD for {state.upper()} State ---")
    
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
    x_tap_l = x_int_l - L_TAPER
    x_tap_r = x_int_r + L_TAPER
    x_lead_l = x_tap_l - L_LEAD
    x_lead_r = x_tap_r + L_LEAD
    
    sx = x_lead_r - x_lead_l + 2 * DPML
    sy = 2 * (Y_PORT + W_WG / 2.0 + 0.4) + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    geometry = []
    
    # 1. Straight leads at ports
    ll = L_LEAD + DPML
    geometry += [
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_l - ll/2,  Y_PORT, 0), material=si),
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_l - ll/2, -Y_PORT, 0), material=si),
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_r + ll/2,  Y_PORT, 0), material=si),
        mp.Block(mp.Vector3(ll, W_WG, mp.inf), center=mp.Vector3(x_tap_r + ll/2, -Y_PORT, 0), material=si),
    ]
    
    # 2. S-bend tapers (raised-cosine profile in high-index Silicon)
    N_SEG = 20
    dx_seg = L_TAPER / N_SEG
    for i in range(N_SEG):
        s_c = (i + 0.5) / N_SEG
        
        # Left taper (Y_PORT -> Y_INT)
        y_c_l = Y_PORT + (1 - math.cos(math.pi * s_c)) / 2.0 * (Y_INT - Y_PORT)
        xc_l = x_tap_l + s_c * L_TAPER
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_l,  y_c_l, 0), material=si))
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_l, -y_c_l, 0), material=si))
        
        # Right taper (Y_INT -> Y_PORT)
        y_c_r = Y_INT + (1 - math.cos(math.pi * s_c)) / 2.0 * (Y_PORT - Y_INT)
        xc_r = x_int_r + s_c * L_TAPER
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_r,  y_c_r, 0), material=si))
        geometry.append(mp.Block(mp.Vector3(dx_seg, W_WG, mp.inf), center=mp.Vector3(xc_r, -y_c_r, 0), material=si))
        
    # 3. Central interaction region (380 nm Si strips + 100 nm Sb2S3 slot)
    geometry += [
        mp.Block(mp.Vector3(L_C, W_WG, mp.inf), center=mp.Vector3(0,  Y_INT, 0), material=si),
        mp.Block(mp.Vector3(L_C, W_WG, mp.inf), center=mp.Vector3(0, -Y_INT, 0), material=si),
        mp.Block(mp.Vector3(L_C, GAP,  mp.inf), center=mp.Vector3(0, 0, 0), material=pcm),
    ]
    
    # Source: Eigenmode in TOP Silicon waveguide
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
    
    sim.run(mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(x_mon_out, -Y_PORT, 0), 1e-5), until=120.0)
    
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
    print("=" * 65)
    print("MEEP FDTD VERIFICATION OF OPTIMAL SILICON SWITCH DESIGN")
    print(f"Core: 380 nm Si | Gap: 100 nm | L_c: {L_C} um | λ: {LAMBDA_UM} um")
    print(f"Cell Area: {1.36 * (L_C + 2*L_TAPER):.2f} um² (44.8 mm² for 3.93M switches)")
    print("=" * 65)
    
    res_am = run_fdtd("amorphous")
    res_cr = run_fdtd("crystalline")
    
    print("\n" + "=" * 65)
    print("FINAL SUMMARY:")
    print(f"  Amorphous (Cross): IL = {res_am['IL_dB']:.3f} dB, XT = {res_am['XT_dB']:.2f} dB")
    print(f"  Crystalline (Bar): IL = {res_cr['IL_dB']:.3f} dB, XT = {res_cr['XT_dB']:.2f} dB")
    print("=" * 65)

if __name__ == "__main__":
    main()
