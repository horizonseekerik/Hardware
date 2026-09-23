"""
ULTRA-COMPACT 1x2 MMI SWITCH CELL — FULL-WAVE MEEP 2D FDTD
===========================================================
Architecture:
  - 1 Center Input Port (W_port = 400 nm)
  - 1x2 Silicon Multimode Box (W_mmi = 1.60 um, L_mmi = 3.20 um)
  - 2 Symmetric Output Ports (W_port = 400 nm, separation = 800 nm)
  - Sb2S3 PCM switching patch over one arm
  - Cell footprint: 1.60 um x 3.20 um = 5.12 um^2
    Total 3.93M switch die area = 20.1 mm^2 (FAR below 75 mm^2 limit!)
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

# 1x2 MMI Box Dimensions
W_MMI = 1.600       # 1.6 um width
L_MMI = 3.200       # 3.2 um (3 * L_pi / 8 for 1x2 symmetric MMI)
W_PORT = 0.400      # 400 nm ports
Y_OUT_SEP = 0.800   # 800 nm output separation
Y_OUT_TOP = Y_OUT_SEP / 2.0   # +0.40 um
Y_OUT_BOT = -Y_OUT_SEP / 2.0  # -0.40 um

L_LEAD = 1.200      # Straight input/output port leads
RESOLUTION = 50     # 50 px/um (20 nm grid)
DPML = 0.8

def run_1x2_mmi(state):
    print(f"\n--- Running 1x2 MMI MEEP FDTD: {state.upper()} State ---")
    
    n_pcm = N_AM if state == "amorphous" else N_CR
    k_pcm = K_AM if state == "amorphous" else K_CR
    
    fcen = 1.0 / LAMBDA_UM
    df = 0.08 * fcen
    cond = (2 * math.pi * fcen * k_pcm / n_pcm) if n_pcm > 0 else 0.0
    
    si = mp.Medium(index=N_SI)
    sio2 = mp.Medium(index=N_SIO2)
    pcm = mp.Medium(index=n_pcm, D_conductivity=cond)
    
    sx = L_MMI + 2 * L_LEAD + 2 * DPML
    sy = W_MMI + 1.0 + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    geometry = []
    
    # 1. Single Center Input Lead (Left)
    ll = L_LEAD + DPML
    x_lead_in = -(L_MMI / 2.0 + ll / 2.0)
    geometry.append(
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_lead_in, 0, 0), material=si)
    )
    
    # 2. Dual Output Leads (Right)
    x_lead_out = (L_MMI / 2.0 + ll / 2.0)
    geometry += [
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_lead_out,  Y_OUT_TOP, 0), material=si),
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_lead_out,  Y_OUT_BOT, 0), material=si),
    ]
    
    # 3. Central 1x2 Silicon Multimode Box
    geometry.append(
        mp.Block(mp.Vector3(L_MMI, W_MMI, mp.inf), center=mp.Vector3(0, 0, 0), material=si)
    )
    
    # 4. Asymmetric Phase-Shifting Sb2S3 Patch (top half of MMI box)
    w_patch = W_MMI / 2.0
    y_patch = W_MMI / 4.0
    geometry.append(
        mp.Block(mp.Vector3(L_MMI, w_patch, mp.inf), center=mp.Vector3(0, y_patch, 0), material=pcm)
    )
    
    # Launch Eigenmode into CENTER input port
    x_src = -L_MMI / 2.0 - L_LEAD * 0.5
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
    
    sim.run(mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(x_mon_out, Y_OUT_TOP, 0), 1e-5), until=100.0)
    
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
        # Routes to bottom port
        IL_dB = -10.0 * np.log10(max(T_bot, 1e-12))
        XT_dB = 10.0 * np.log10(max(T_top, 1e-12))
    else:
        # Routes to top port
        IL_dB = -10.0 * np.log10(max(T_top, 1e-12))
        XT_dB = 10.0 * np.log10(max(T_bot, 1e-12))
        
    print(f"  T_top (Port 1 out)   = {T_top:.4f} ({10*np.log10(max(T_top,1e-12)):.2f} dB)")
    print(f"  T_bot (Port 2 out)   = {T_bot:.4f} ({10*np.log10(max(T_bot,1e-12)):.2f} dB)")
    print(f"  Total Guided Power   = {T_total*100:.1f}%")
    print(f"  Insertion Loss (IL)  = {IL_dB:.3f} dB")
    print(f"  Crosstalk (XT)       = {XT_dB:.2f} dB")
    print(f"  Extinction Ratio     = {abs(IL_dB - XT_dB):.2f} dB")
    
    return {"state": state, "T_top": T_top, "T_bot": T_bot, "IL_dB": IL_dB, "XT_dB": XT_dB, "T_total": T_total}

def main():
    cell_area = W_MMI * L_MMI
    tot_area = (3_932_160 * cell_area) / 1e6
    
    print("=" * 65)
    print(f"1x2 MMI SWITCH CELL: {W_MMI:.2f} um x {L_MMI:.2f} um = {cell_area:.2f} um^2")
    print(f"Total 3.93M Switch Die Area: {tot_area:.2f} mm^2 (Target <= 75.0 mm^2)")
    print("=" * 65)
    
    res_am = run_1x2_mmi("amorphous")
    res_cr = run_1x2_mmi("crystalline")
    
    print("\n" + "=" * 65)
    print("FINAL 1x2 MMI FDTD SIMULATION RESULTS:")
    print("=" * 65)
    print(f"  Amorphous (Port 2 Routing): IL = {res_am['IL_dB']:.3f} dB, XT = {res_am['XT_dB']:.2f} dB, Power = {res_am['T_total']*100:.1f}%")
    print(f"  Crystalline (Port 1 Routing): IL = {res_cr['IL_dB']:.3f} dB, XT = {res_cr['XT_dB']:.2f} dB, Power = {res_cr['T_total']*100:.1f}%")
    print("=" * 65)

if __name__ == "__main__":
    main()
