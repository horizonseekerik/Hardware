"""
MEEP FDTD: ACTIVE PAIRED-INTERFERENCE 1x2 MMI SWITCH
====================================================
Structure:
  - 1 Input Port at y = +W_eff/6 (with adiabatic taper)
  - 1x2 MMI Cavity: W = 1.80 um, L = 4.60 um
  - 2 Output Ports at y = +W_eff/6 (Port 1, Bar) and y = -W_eff/6 (Port 2, Cross)
  - Active Phase-Shifting Patch (Sb2S3 top clad / recessed):
      * In Amorphous State: Self-images to Port 1 (Port 2 is naturally blocked!)
      * In Crystalline State: Shifts interference to Port 2 (Port 1 is blocked!)
"""

import math
import meep as mp

LAMBDA_0 = 1.064
FCEN = 1.0 / LAMBDA_0
DF = 0.08 * FCEN
N_CLAD = 1.449
N_CORE = 2.850

DPML = 0.8
RESOLUTION = 40

W_MMI = 1.80
w_eff = W_MMI + (LAMBDA_0 / math.pi) / math.sqrt(N_CORE**2 - N_CLAD**2)
Y_POS = w_eff / 6.0  # 0.323 um
L_MMI = 4.60

W_PORT = 0.36
W_TAPER = 0.44
L_TAPER = 1.00
L_LEAD = 1.00

sx = L_MMI + 2 * L_TAPER + 2 * L_LEAD + 2 * DPML
sy = W_MMI + 1.2 + 2 * DPML
cell = mp.Vector3(sx, sy, 0)
mat_core = mp.Medium(index=N_CORE)
mat_clad = mp.Medium(index=N_CLAD)

x_src = -sx/2 + DPML + 0.3
x_mon_out = sx/2 - DPML - 0.3
mon_w = W_PORT * 2.2

src = mp.EigenModeSource(
    src=mp.GaussianSource(FCEN, fwidth=DF),
    center=mp.Vector3(x_src, Y_POS, 0),
    size=mp.Vector3(0, mon_w, 0),
    eig_band=1, eig_match_freq=True, direction=mp.X
)

# Reference waveguide
print("--> Simulating Reference Waveguide...")
sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=[mp.Block(mp.Vector3(sx, W_PORT, mp.inf), center=mp.Vector3(0, Y_POS, 0), material=mat_core)], sources=[src], resolution=RESOLUTION, default_material=mat_clad)
m_ref = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
sim_ref.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, Y_POS, 0), 1e-5), until=100.0)
p_ref = abs(sim_ref.get_eigenmode_coefficients(m_ref, [1]).alpha[0, 0, 0])**2
print(f"    Reference Injected Power = {p_ref:.5e}")

results = {}

for state, delta_n in [("amorphous", 0.0), ("crystalline", 0.145)]:
    print(f"\n--> Simulating Paired 1x2 MMI in {state.upper()} State (Delta_n = {delta_n:.3f})...")
    
    geom = []
    # MMI Box
    geom.append(mp.Block(mp.Vector3(L_MMI, W_MMI, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core))
    
    # Input Lead + Taper (single input at +Y_POS)
    ll = L_LEAD + DPML
    x_in_lead = -L_MMI/2 - L_TAPER - ll/2
    geom.append(mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_in_lead, Y_POS, 0), material=mat_core))
    taper_in = [
        mp.Vector3(-L_MMI/2 - L_TAPER, Y_POS - W_PORT/2, 0),
        mp.Vector3(-L_MMI/2, Y_POS - W_TAPER/2, 0),
        mp.Vector3(-L_MMI/2, Y_POS + W_TAPER/2, 0),
        mp.Vector3(-L_MMI/2 - L_TAPER, Y_POS + W_PORT/2, 0),
    ]
    geom.append(mp.Prism(taper_in, height=mp.inf, material=mat_core))
    
    # Output Leads + Tapers (Port 1 at +Y_POS, Port 2 at -Y_POS)
    x_out_lead = L_MMI/2 + L_TAPER + ll/2
    geom += [
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead,  Y_POS, 0), material=mat_core),
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead, -Y_POS, 0), material=mat_core),
    ]
    taper_top = [
        mp.Vector3(L_MMI/2, Y_POS - W_TAPER/2, 0),
        mp.Vector3(L_MMI/2 + L_TAPER, Y_POS - W_PORT/2, 0),
        mp.Vector3(L_MMI/2 + L_TAPER, Y_POS + W_PORT/2, 0),
        mp.Vector3(L_MMI/2, Y_POS + W_TAPER/2, 0),
    ]
    geom.append(mp.Prism(taper_top, height=mp.inf, material=mat_core))
    taper_bot = [
        mp.Vector3(L_MMI/2, -Y_POS - W_TAPER/2, 0),
        mp.Vector3(L_MMI/2 + L_TAPER, -Y_POS - W_PORT/2, 0),
        mp.Vector3(L_MMI/2 + L_TAPER, -Y_POS + W_PORT/2, 0),
        mp.Vector3(L_MMI/2, -Y_POS + W_TAPER/2, 0),
    ]
    geom.append(mp.Prism(taper_bot, height=mp.inf, material=mat_core))
    
    # Active Patch (centered at y = +Y_POS to modulate the bar beam)
    if delta_n > 0:
        mat_patch = mp.Medium(index=N_CORE + delta_n)
        l_patch = L_MMI * 0.75
        w_patch = 0.50
        geom.append(mp.Block(mp.Vector3(l_patch, w_patch, mp.inf), center=mp.Vector3(0, Y_POS, 0), material=mat_patch))
        
    sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
    m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
    m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, -Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
    
    sim.run(mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(x_mon_out, Y_POS, 0), 1e-5), until=110.0)
    
    res_top = sim.get_eigenmode_coefficients(m_top, [1])
    res_bot = sim.get_eigenmode_coefficients(m_bot, [1])
    
    p_top = abs(res_top.alpha[0, 0, 0])**2 / p_ref
    p_bot = abs(res_bot.alpha[0, 0, 0])**2 / p_ref
    p_tot = p_top + p_bot
    results[state] = (p_top, p_bot, p_tot)
    print(f"    {state.upper()}: P_top (Port 1) = {p_top*100:.2f}%, P_bot (Port 2) = {p_bot*100:.2f}%, Total = {p_tot*100:.2f}%")

p_top_am, p_bot_am, tot_am = results["amorphous"]
p_top_cr, p_bot_cr, tot_cr = results["crystalline"]

er_am_dB = 10.0 * math.log10(p_top_am / max(p_bot_am, 1e-6))
er_cr_dB = 10.0 * math.log10(p_bot_cr / max(p_top_cr, 1e-6))

print("\n" + "=" * 70)
print("FINAL RESULTS: ACTIVE PAIRED 1x2 MMI SWITCH")
print(f"  Amorphous (State 0): Port 1 = {p_top_am*100:.2f}%, Port 2 = {p_bot_am*100:.2f}% (ER = {er_am_dB:.2f} dB, IL = {-10*math.log10(tot_am):.3f} dB)")
print(f"  Crystalline (State 1): Port 1 = {p_top_cr*100:.2f}%, Port 2 = {p_bot_cr*100:.2f}% (ER = {er_cr_dB:.2f} dB, IL = {-10*math.log10(tot_cr):.3f} dB)")
print("=" * 70)
