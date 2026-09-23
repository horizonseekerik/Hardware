"""
MEEP FDTD: PAIRED-INTERFERENCE 1x2 MMI SWITCH
==============================================
Physics Principle:
  - Input at y = +W_eff / 6 excites paired modes (m = 0, 1, 3, 4...)
  - Cross-imaging distance: L_cross = 4 * n_eff * W_eff^2 / (9 * lambda_0)
  - Light from y = +W_eff/6 self-images directly into y = -W_eff/6 (Port 2, Cross)
  - Applying phase perturbation shifts beat length to L_bar, imaging to y = +W_eff/6 (Port 1, Bar)
  - Cavity size: W = 1.80 um, L = 4.38 um!
  - 1 Input, 2 Outputs (True 1x2 MMI Switch)
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
# Analytical W_eff:
w_eff = W_MMI + (LAMBDA_0 / math.pi) / math.sqrt(N_CORE**2 - N_CLAD**2)
# Paired interference cross distance:
L_MMI = (4.0 * N_CORE * (w_eff**2)) / (9.0 * LAMBDA_0)
print(f"Paired MMI: W_eff = {w_eff:.4f} um, L_MMI = {L_MMI:.4f} um")

W_PORT = 0.38
W_TAPER = 0.50
L_TAPER = 1.00
Y_POS = w_eff / 6.0  # ~ +0.323 um
L_LEAD = 1.20

sx = L_MMI + 2 * L_TAPER + 2 * L_LEAD + 2 * DPML
sy = W_MMI + 1.2 + 2 * DPML
cell = mp.Vector3(sx, sy, 0)

mat_core = mp.Medium(index=N_CORE)
mat_clad = mp.Medium(index=N_CLAD)

# Reference waveguide
ref_geom = [mp.Block(mp.Vector3(sx, W_PORT, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core)]
x_src = -sx/2 + DPML + 0.3
x_mon_out = sx/2 - DPML - 0.3
mon_w = W_PORT * 2.2

src = mp.EigenModeSource(
    src=mp.GaussianSource(FCEN, fwidth=DF),
    center=mp.Vector3(x_src, Y_POS, 0),
    size=mp.Vector3(0, mon_w, 0),
    eig_band=1, eig_match_freq=True, direction=mp.X
)

sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=[mp.Block(mp.Vector3(sx, W_PORT, mp.inf), center=mp.Vector3(0, Y_POS, 0), material=mat_core)], sources=[src], resolution=RESOLUTION, default_material=mat_clad)
m_ref = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
sim_ref.run(until=100.0)
p_ref = abs(sim_ref.get_eigenmode_coefficients(m_ref, [1]).alpha[0, 0, 0])**2
print(f"Reference Transmitted Power = {p_ref:.5e}")

# Paired 1x2 MMI Simulation
geom = []
geom.append(mp.Block(mp.Vector3(L_MMI, W_MMI, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core))

# Input Lead + Taper (at y = +Y_POS)
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

sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, -Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))

sim.run(until=100.0)

res_top = sim.get_eigenmode_coefficients(m_top, [1])
res_bot = sim.get_eigenmode_coefficients(m_bot, [1])
p_top = abs(res_top.alpha[0, 0, 0])**2 / p_ref
p_bot = abs(res_bot.alpha[0, 0, 0])**2 / p_ref
p_tot = p_top + p_bot
il_dB = -10.0 * math.log10(p_tot)
er_dB = 10.0 * math.log10(p_bot / max(p_top, 1e-6))

print("\n" + "=" * 65)
print("PAIRED-INTERFERENCE 1x2 MMI PASSIVE (CROSS STATE) RESULTS:")
print(f"  Port 1 (Bar, +Y_POS)  = {p_top*100:.2f}%")
print(f"  Port 2 (Cross, -Y_POS)= {p_bot*100:.2f}%")
print(f"  Total Transmission    = {p_tot*100:.2f}%")
print(f"  Insertion Loss        = {il_dB:.4f} dB")
print(f"  Extinction Ratio      = {er_dB:.2f} dB")
print("=" * 65)
