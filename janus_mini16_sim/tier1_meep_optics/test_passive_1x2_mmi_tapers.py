"""
TEST PASSIVE 1x2 MMI WITH ADIABATIC PORT TAPERS IN MEEP
========================================================
Measures baseline insertion loss of 1x2 MMI with linear adiabatic port tapers:
  - Input: w_port = 400 nm, linearly tapered to w_taper = 550 nm over L_taper = 1.0 um
  - MMI box: W_mmi = 1.60 um, L_mmi = 4.00 um
  - Outputs: 2 symmetric ports (sep = 0.80 um), tapered from 550 nm to 400 nm over 1.0 um
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

W_MMI = 1.60
L_MMI = 4.00
W_PORT = 0.40
W_TAPER = 0.55
L_TAPER = 1.00
Y_OUT = 0.40
L_LEAD = 1.20

sx = L_MMI + 2 * L_TAPER + 2 * L_LEAD + 2 * DPML
sy = W_MMI + 1.2 + 2 * DPML
cell = mp.Vector3(sx, sy, 0)

mat_core = mp.Medium(index=N_CORE)
mat_clad = mp.Medium(index=N_CLAD)

# 1. Reference straight waveguide
print("--> Simulating Reference Waveguide...")
ref_geom = [mp.Block(mp.Vector3(sx, W_PORT, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core)]
x_src = -sx/2 + DPML + 0.3
x_mon_out = sx/2 - DPML - 0.3
mon_w = W_PORT * 2.2

src = mp.EigenModeSource(
    src=mp.GaussianSource(FCEN, fwidth=DF),
    center=mp.Vector3(x_src, 0, 0),
    size=mp.Vector3(0, mon_w, 0),
    eig_band=1, eig_match_freq=True, direction=mp.X
)

sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=ref_geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
m_ref = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, 0, 0), size=mp.Vector3(0, mon_w, 0)))
sim_ref.run(until=100.0)
p_ref = abs(sim_ref.get_eigenmode_coefficients(m_ref, [1]).alpha[0, 0, 0])**2
print(f"Reference Transmitted Power = {p_ref:.5e}")

# 2. 1x2 MMI with Adiabatic Linear Tapers
print("--> Simulating 1x2 MMI with Adiabatic Tapers...")
geom = []

# MMI Box
geom.append(mp.Block(mp.Vector3(L_MMI, W_MMI, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core))

# Input Lead + Taper (left)
# Input straight lead
ll = L_LEAD + DPML
x_in_lead = -L_MMI/2 - L_TAPER - ll/2
geom.append(mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_in_lead, 0, 0), material=mat_core))

# Input linear taper (wedge / trapezoid)
# Centered at x = -L_MMI/2 - L_TAPER/2
# Uses mp.Prism for exact linear taper
taper_in_verts = [
    mp.Vector3(-L_MMI/2 - L_TAPER, -W_PORT/2, 0),
    mp.Vector3(-L_MMI/2, -W_TAPER/2, 0),
    mp.Vector3(-L_MMI/2, W_TAPER/2, 0),
    mp.Vector3(-L_MMI/2 - L_TAPER, W_PORT/2, 0),
]
geom.append(mp.Prism(taper_in_verts, height=mp.inf, material=mat_core))

# Output Leads + Tapers (right, top and bottom)
x_out_lead = L_MMI/2 + L_TAPER + ll/2
geom += [
    mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead,  Y_OUT, 0), material=mat_core),
    mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead, -Y_OUT, 0), material=mat_core),
]

# Top output linear taper
taper_top_verts = [
    mp.Vector3(L_MMI/2, Y_OUT - W_TAPER/2, 0),
    mp.Vector3(L_MMI/2 + L_TAPER, Y_OUT - W_PORT/2, 0),
    mp.Vector3(L_MMI/2 + L_TAPER, Y_OUT + W_PORT/2, 0),
    mp.Vector3(L_MMI/2, Y_OUT + W_TAPER/2, 0),
]
geom.append(mp.Prism(taper_top_verts, height=mp.inf, material=mat_core))

# Bottom output linear taper
taper_bot_verts = [
    mp.Vector3(L_MMI/2, -Y_OUT - W_TAPER/2, 0),
    mp.Vector3(L_MMI/2 + L_TAPER, -Y_OUT - W_PORT/2, 0),
    mp.Vector3(L_MMI/2 + L_TAPER, -Y_OUT + W_PORT/2, 0),
    mp.Vector3(L_MMI/2, -Y_OUT + W_TAPER/2, 0),
]
geom.append(mp.Prism(taper_bot_verts, height=mp.inf, material=mat_core))

sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_OUT, 0), size=mp.Vector3(0, mon_w, 0)))
m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, -Y_OUT, 0), size=mp.Vector3(0, mon_w, 0)))

sim.run(until=100.0)

res_top = sim.get_eigenmode_coefficients(m_top, [1])
res_bot = sim.get_eigenmode_coefficients(m_bot, [1])
p_top = abs(res_top.alpha[0, 0, 0])**2 / p_ref
p_bot = abs(res_bot.alpha[0, 0, 0])**2 / p_ref
p_tot = p_top + p_bot
il_dB = -10.0 * math.log10(p_tot)

print("\n" + "=" * 60)
print(f"PASSIVE 1x2 MMI WITH ADIABATIC TAPERS RESULT:")
print(f"  P_top = {p_top*100:.2f}%, P_bot = {p_bot*100:.2f}%")
print(f"  Total Transmission = {p_tot*100:.2f}%")
print(f"  Insertion Loss     = {il_dB:.4f} dB")
print("=" * 60)
