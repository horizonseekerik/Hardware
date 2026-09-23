"""
MEEP FDTD VERIFICATION OF OPTIMAL 1x2 MMI SWITCH (lambda_0 = 1064 nm)
=====================================================================
Parameters from Analytical Optimization:
  - Silicon Core (n = 3.565) in SiO2 (n = 1.449)
  - Operating wavelength: lambda_0 = 1.064 um
  - Multimode box: W_mmi = 1.55 um, L_mmi = 4.88 um
  - Input port: 1 center port (W_port = 420 nm)
  - Output ports: 2 symmetric ports (W_port = 420 nm, separation = 825 nm)
  - Active Sb2S3 patch: n_am = 2.70, n_cr = 3.30
  - Cell Area: 12.7 um^2 (3.93M switches = 50.0 mm^2 <= 75.0 mm^2)
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

W_MMI = 1.550       # 1.55 um MMI width
L_MMI = 4.880       # 4.88 um MMI length (optimal self-imaging)
W_PORT = 0.420      # 420 nm port width
Y_OUT_SEP = 0.825   # 825 nm output separation
Y_OUT_TOP = Y_OUT_SEP / 2.0   # +0.4125 um
Y_OUT_BOT = -Y_OUT_SEP / 2.0  # -0.4125 um

L_LEAD = 1.500      # 1.5 um straight port leads
RESOLUTION = 50     # 50 px/um (20 nm grid)
DPML = 0.8

def run_simulation(state):
    print(f"\n--- Running MEEP 2D FDTD for {state.upper()} State ---")
    
    n_pcm = N_AM if state == "amorphous" else N_CR
    k_pcm = K_AM if state == "amorphous" else K_CR
    
    fcen = 1.0 / LAMBDA_UM
    df = 0.08 * fcen
    cond = (2 * math.pi * fcen * k_pcm / n_pcm) if n_pcm > 0 else 0.0
    
    si = mp.Medium(index=N_SI)
    sio2 = mp.Medium(index=N_SIO2)
    pcm = mp.Medium(index=n_pcm, D_conductivity=cond)
    
    sx = L_MMI + 2 * L_LEAD + 2 * DPML
    sy = W_MMI + 1.2 + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    geometry = []
    
    # 1. Center Input Port (Left)
    ll = L_LEAD + DPML
    x_lead_in = -(L_MMI / 2.0 + ll / 2.0)
    geometry.append(
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_lead_in, 0, 0), material=si)
    )
    
    # 2. Dual Output Ports (Right)
    x_lead_out = (L_MMI / 2.0 + ll / 2.0)
    geometry += [
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_lead_out,  Y_OUT_TOP, 0), material=si),
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_lead_out,  Y_OUT_BOT, 0), material=si),
    ]
    
    # 3. Multimode Silicon Box
    geometry.append(
        mp.Block(mp.Vector3(L_MMI, W_MMI, mp.inf), center=mp.Vector3(0, 0, 0), material=si)
    )
    
    # 4. Phase-Change Sb2S3 Patch (top quadrant of MMI box)
    w_patch = W_MMI / 2.0
    y_patch = W_MMI / 4.0
    geometry.append(
        mp.Block(mp.Vector3(L_MMI, w_patch, mp.inf), center=mp.Vector3(0, y_patch, 0), material=pcm)
    )
    
    # Launch Eigenmode into CENTER input
    x_src = -L_MMI / 2.0 - L_LEAD * 0.6
    src = mp.EigenModeSource(
        src=mp.GaussianSource(fcen, fwidth=df),
        center=mp.Vector3(x_src, 0, 0),
        size=mp.Vector3(0, W_PORT * 2.0, 0),
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
    
    mon_w = W_PORT * 2.0
    x_mon_in = -L_MMI / 2.0 - L_LEAD * 0.2
    x_mon_out =  L_MMI / 2.0 + L_LEAD * 0.4
    
    m_in = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_in, 0, 0), size=mp.Vector3(0, mon_w, 0)))
    m_top = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_OUT_TOP, 0), size=mp.Vector3(0, mon_w, 0)))
    m_bot = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_OUT_BOT, 0), size=mp.Vector3(0, mon_w, 0)))
    
    sim.run(mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(x_mon_out, Y_OUT_TOP, 0), 1e-5), until=120.0)
    
    res_in = sim.get_eigenmode_coefficients(m_in, [1])
    res_top = sim.get_eigenmode_coefficients(m_top, [1])
    res_bot = sim.get_eigenmode_coefficients(m_bot, [1])
    
    a_in = res_in.alpha[0, 0, 0]
    b_top = res_top.alpha[0, 0, 0]
    b_bot = res_bot.alpha[0, 0, 0]
    
    S_top = b_top / a_in if abs(a_in) > 0 else 0
    S_bot = b_bot / a_in if abs(a_in) > 0 else 0
    
    T_top = abs(S_top)**2
    T_bot = abs(S_bot)**2
    T_total = T_top + T_bot
    
    if state == "amorphous":
        IL_dB = -10.0 * np.log10(max(T_bot, 1e-12))
        XT_dB = 10.0 * np.log10(max(T_top, 1e-12))
    else:
        IL_dB = -10.0 * np.log10(max(T_top, 1e-12))
        XT_dB = 10.0 * np.log10(max(T_bot, 1e-12))
        
    print(f"  T_top (Output 1)     = {T_top:.4f} ({10*np.log10(max(T_top,1e-12)):.2f} dB)")
    print(f"  T_bot (Output 2)     = {T_bot:.4f} ({10*np.log10(max(T_bot,1e-12)):.2f} dB)")
    print(f"  Total Guided Power   = {T_total*100:.1f}%")
    print(f"  Insertion Loss (IL)  = {IL_dB:.3f} dB")
    print(f"  Crosstalk (XT)       = {XT_dB:.2f} dB")
    print(f"  Extinction Ratio     = {abs(IL_dB - XT_dB):.2f} dB")
    
    return {"state": state, "T_top": T_top, "T_bot": T_bot, "IL_dB": IL_dB, "XT_dB": XT_dB, "T_total": T_total}

def main():
    cell_w = W_MMI + 0.30
    cell_l = L_MMI + 2.0
    area = cell_w * cell_l
    tot_area = (3_932_160 * area) / 1e6
    
    print("=" * 70)
    print("VERIFYING OPTIMAL 1x2 MMI SWITCH CELL IN MEEP 2D FDTD")
    print(f"MMI Box: {W_MMI} um x {L_MMI} um | Ports: {W_PORT*1000:.0f} nm | λ: {LAMBDA_UM} um")
    print(f"Cell Area: {area:.2f} um^2 | Total 3.93M Die Area: {tot_area:.2f} mm^2 (Limit: 75 mm^2)")
    print("=" * 70)
    
    res_am = run_simulation("amorphous")
    res_cr = run_simulation("crystalline")
    
    print("\n" + "=" * 70)
    print("FINAL VERIFIED FDTD SIMULATION RESULTS:")
    print("=" * 70)
    print(f"  Amorphous (Port 2 Routing): IL = {res_am['IL_dB']:.3f} dB, XT = {res_am['XT_dB']:.2f} dB, Power = {res_am['T_total']*100:.1f}%")
    print(f"  Crystalline (Port 1 Routing): IL = {res_cr['IL_dB']:.3f} dB, XT = {res_cr['XT_dB']:.2f} dB, Power = {res_cr['T_total']*100:.1f}%")
    print("=" * 70)

if __name__ == "__main__":
    main()
