"""
COMPACT 2x2 MMI SWITCH CELL — FULL-WAVE MEEP 2D FDTD
=====================================================
Target: Direct simulated Insertion Loss < 0.5 dB (Transmission > 90%)
        Area per cell <= 19.0 um^2 (Total die <= 75 mm^2)

Architecture:
  - 2x2 Multimode Interference (MMI) coupler in Silicon
  - Multimode width: W_mmi = 1.80 um
  - Multimode length: L_mmi = 6.40 um (paired self-imaging beat length)
  - Port access guides: W_port = 0.40 um, separated by 0.90 um
  - Active Phase-Change: Sb2S3 patch over one half of multimode box
  - Cell footprint: 1.80 um x 6.40 um = 11.52 um^2
    Total 3.93M die area = 45.3 mm^2 (well below 75 mm^2 limit!)
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

# MMI Box Dimensions
W_MMI = 1.800       # 1.8 um width
L_MMI = 6.400       # 6.4 um self-imaging length (3 * L_pi / 4)
W_PORT = 0.400      # 400 nm port waveguides
Y_PORT_SEP = 0.900  # 900 nm port separation
Y_PORT_TOP = Y_PORT_SEP / 2.0   # +0.45 um
Y_PORT_BOT = -Y_PORT_SEP / 2.0  # -0.45 um

L_LEAD = 1.500      # Straight input/output ports
RESOLUTION = 50     # 50 px/um (20 nm grid)
DPML = 0.8

def run_mmi_fdtd(state):
    print(f"\n--- Running MEEP 2D FDTD for MMI Switch: {state.upper()} State ---")
    
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
    
    # 1. Input/Output Port Leads (Top and Bottom)
    ll = L_LEAD + DPML
    x_lead_in = -(L_MMI / 2.0 + ll / 2.0)
    x_lead_out =  (L_MMI / 2.0 + ll / 2.0)
    
    geometry += [
        # Input Ports (Left)
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_lead_in,  Y_PORT_TOP, 0), material=si),
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_lead_in,  Y_PORT_BOT, 0), material=si),
        # Output Ports (Right)
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_lead_out, Y_PORT_TOP, 0), material=si),
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_lead_out, Y_PORT_BOT, 0), material=si),
    ]
    
    # 2. Central Silicon Multimode Box
    geometry.append(
        mp.Block(mp.Vector3(L_MMI, W_MMI, mp.inf), center=mp.Vector3(0, 0, 0), material=si)
    )
    
    # 3. Phase-Change Sb2S3 Patch (placed along upper half of multimode box to switch routing)
    w_patch = W_MMI / 2.0
    y_patch = W_MMI / 4.0
    geometry.append(
        mp.Block(mp.Vector3(L_MMI, w_patch, mp.inf), center=mp.Vector3(0, y_patch, 0), material=pcm)
    )
    
    # Launch Eigenmode into TOP input port
    x_src = -L_MMI / 2.0 - L_LEAD * 0.6
    src = mp.EigenModeSource(
        src=mp.GaussianSource(fcen, fwidth=df),
        center=mp.Vector3(x_src, Y_PORT_TOP, 0),
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
    
    m_in = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_in, Y_PORT_TOP, 0), size=mp.Vector3(0, mon_w, 0)))
    m_bar = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, Y_PORT_TOP, 0), size=mp.Vector3(0, mon_w, 0)))
    m_cross = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, Y_PORT_BOT, 0), size=mp.Vector3(0, mon_w, 0)))
    
    sim.run(mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(x_mon_out, Y_PORT_BOT, 0), 1e-5), until=120.0)
    
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
        # Cross routing
        IL_dB = -10.0 * np.log10(max(T_cross, 1e-12))
        XT_dB = 10.0 * np.log10(max(T_bar, 1e-12))
    else:
        # Bar routing
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
    cell_area = W_MMI * L_MMI
    tot_area = (3_932_160 * cell_area) / 1e6
    
    print("=" * 65)
    print(f"MMI SWITCH CELL: {W_MMI:.2f} um x {L_MMI:.2f} um = {cell_area:.2f} um^2")
    print(f"Total 3.93M Switch Die Area: {tot_area:.2f} mm^2 (Target <= 75.0 mm^2)")
    print("=" * 65)
    
    res_am = run_mmi_fdtd("amorphous")
    res_cr = run_mmi_fdtd("crystalline")
    
    print("\n" + "=" * 65)
    print("FINAL MMI FDTD SIMULATION RESULTS:")
    print("=" * 65)
    print(f"  Amorphous (Cross): IL = {res_am['IL_dB']:.3f} dB, XT = {res_am['XT_dB']:.2f} dB, Transmission = {res_am['T_cross']*100:.1f}%")
    print(f"  Crystalline (Bar): IL = {res_cr['IL_dB']:.3f} dB, XT = {res_cr['XT_dB']:.2f} dB, Transmission = {res_cr['T_bar']*100:.1f}%")
    print("=" * 65)

if __name__ == "__main__":
    main()
