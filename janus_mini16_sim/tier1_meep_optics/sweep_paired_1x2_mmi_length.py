"""
SWEEP PAIRED 1x2 MMI CAVITY LENGTH IN MEEP
===========================================
Finds the exact cavity length L_MMI for peak transmission into Port 1 (Bar)
and determines extinction ratio to Port 2 (Cross).
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

W_PORT = 0.36
W_TAPER = 0.44
L_TAPER = 1.00
L_LEAD = 1.00

# Sweep L_MMI around 4.5 - 5.5 um
lengths = [4.4, 4.8, 5.2, 5.6]

mat_core = mp.Medium(index=N_CORE)
mat_clad = mp.Medium(index=N_CLAD)

for l_mmi in lengths:
    sx = l_mmi + 2 * L_TAPER + 2 * L_LEAD + 2 * DPML
    sy = W_MMI + 1.2 + 2 * DPML
    cell = mp.Vector3(sx, sy, 0)
    
    x_src = -sx/2 + DPML + 0.3
    x_mon_out = sx/2 - DPML - 0.3
    mon_w = W_PORT * 2.2
    
    src = mp.EigenModeSource(
        src=mp.GaussianSource(FCEN, fwidth=DF),
        center=mp.Vector3(x_src, Y_POS, 0),
        size=mp.Vector3(0, mon_w, 0),
        eig_band=1, eig_match_freq=True, direction=mp.X
    )
    
    # Ref
    sim_ref = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=[mp.Block(mp.Vector3(sx, W_PORT, mp.inf), center=mp.Vector3(0, Y_POS, 0), material=mat_core)], sources=[src], resolution=RESOLUTION, default_material=mat_clad)
    m_ref = sim_ref.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
    sim_ref.run(until=80.0)
    p_ref = abs(sim_ref.get_eigenmode_coefficients(m_ref, [1]).alpha[0, 0, 0])**2
    
    # Device
    geom = [mp.Block(mp.Vector3(l_mmi, W_MMI, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core)]
    ll = L_LEAD + DPML
    x_in_lead = -l_mmi/2 - L_TAPER - ll/2
    geom.append(mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_in_lead, Y_POS, 0), material=mat_core))
    taper_in = [
        mp.Vector3(-l_mmi/2 - L_TAPER, Y_POS - W_PORT/2, 0),
        mp.Vector3(-l_mmi/2, Y_POS - W_TAPER/2, 0),
        mp.Vector3(-l_mmi/2, Y_POS + W_TAPER/2, 0),
        mp.Vector3(-l_mmi/2 - L_TAPER, Y_POS + W_PORT/2, 0),
    ]
    geom.append(mp.Prism(taper_in, height=mp.inf, material=mat_core))
    
    x_out_lead = l_mmi/2 + L_TAPER + ll/2
    geom += [
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead,  Y_POS, 0), material=mat_core),
        mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead, -Y_POS, 0), material=mat_core),
    ]
    taper_top = [
        mp.Vector3(l_mmi/2, Y_POS - W_TAPER/2, 0),
        mp.Vector3(l_mmi/2 + L_TAPER, Y_POS - W_PORT/2, 0),
        mp.Vector3(l_mmi/2 + L_TAPER, Y_POS + W_PORT/2, 0),
        mp.Vector3(l_mmi/2, Y_POS + W_TAPER/2, 0),
    ]
    geom.append(mp.Prism(taper_top, height=mp.inf, material=mat_core))
    taper_bot = [
        mp.Vector3(l_mmi/2, -Y_POS - W_TAPER/2, 0),
        mp.Vector3(l_mmi/2 + L_TAPER, -Y_POS - W_PORT/2, 0),
        mp.Vector3(l_mmi/2 + L_TAPER, -Y_POS + W_PORT/2, 0),
        mp.Vector3(l_mmi/2, -Y_POS + W_TAPER/2, 0),
    ]
    geom.append(mp.Prism(taper_bot, height=mp.inf, material=mat_core))
    
    sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
    m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
    m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, -Y_POS, 0), size=mp.Vector3(0, mon_w, 0)))
    sim.run(until=80.0)
    
    p_top = abs(sim.get_eigenmode_coefficients(m_top, [1]).alpha[0, 0, 0])**2 / p_ref
    p_bot = abs(sim.get_eigenmode_coefficients(m_bot, [1]).alpha[0, 0, 0])**2 / p_ref
    p_tot = p_top + p_bot
    il_dB = -10.0 * math.log10(p_tot)
    er_dB = 10.0 * math.log10(p_top / max(p_bot, 1e-6))
    
    print(f"L_MMI = {l_mmi} um: P_top = {p_top*100:.2f}%, P_bot = {p_bot*100:.2f}%, Total = {p_tot*100:.2f}% (IL = {il_dB:.3f} dB, ER = {er_dB:.2f} dB)")
