"""
OPTIMIZATION OF 1x2 MMI SWITCH WITH ADIABATIC PORT TAPERS
==========================================================
Explores active patch placement inside the 1x2 MMI cavity:
  - Cavity: W_mmi = 1.60 um, L_mmi = 4.00 um
  - Input: w_port = 400 nm -> w_taper = 550 nm (L_taper = 1.0 um)
  - Outputs: 2 ports at y = +/- 0.40 um (w_taper = 550 nm -> w_port = 400 nm)
  - Patch parameters:
      * x_center, length L_patch
      * y_center, width W_patch
      * Delta_n (amorphous vs crystalline)
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
L_LEAD = 1.00

sx = L_MMI + 2 * L_TAPER + 2 * L_LEAD + 2 * DPML
sy = W_MMI + 1.2 + 2 * DPML
cell = mp.Vector3(sx, sy, 0)
mat_core = mp.Medium(index=N_CORE)
mat_clad = mp.Medium(index=N_CLAD)

# Reference
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
sim_ref.run(until=80.0)
p_ref = abs(sim_ref.get_eigenmode_coefficients(m_ref, [1]).alpha[0, 0, 0])**2
print(f"Reference Power = {p_ref:.5e}")

def test_patch_geometry(desc, x_c, l_p, y_c, w_p, dn_am, dn_cr):
    print(f"\nEvaluating: {desc} (L={l_p}um, W={w_p}um, y_c={y_c}um)")
    
    results = {}
    for state, dn in [("amorphous", dn_am), ("crystalline", dn_cr)]:
        geom = []
        # MMI Base
        geom.append(mp.Block(mp.Vector3(L_MMI, W_MMI, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core))
        
        # Leads + Tapers
        ll = L_LEAD + DPML
        x_in_lead = -L_MMI/2 - L_TAPER - ll/2
        geom.append(mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_in_lead, 0, 0), material=mat_core))
        taper_in = [
            mp.Vector3(-L_MMI/2 - L_TAPER, -W_PORT/2, 0),
            mp.Vector3(-L_MMI/2, -W_TAPER/2, 0),
            mp.Vector3(-L_MMI/2, W_TAPER/2, 0),
            mp.Vector3(-L_MMI/2 - L_TAPER, W_PORT/2, 0),
        ]
        geom.append(mp.Prism(taper_in, height=mp.inf, material=mat_core))
        
        x_out_lead = L_MMI/2 + L_TAPER + ll/2
        geom += [
            mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead,  Y_OUT, 0), material=mat_core),
            mp.Block(mp.Vector3(ll, W_PORT, mp.inf), center=mp.Vector3(x_out_lead, -Y_OUT, 0), material=mat_core),
        ]
        taper_top = [
            mp.Vector3(L_MMI/2, Y_OUT - W_TAPER/2, 0),
            mp.Vector3(L_MMI/2 + L_TAPER, Y_OUT - W_PORT/2, 0),
            mp.Vector3(L_MMI/2 + L_TAPER, Y_OUT + W_PORT/2, 0),
            mp.Vector3(L_MMI/2, Y_OUT + W_TAPER/2, 0),
        ]
        geom.append(mp.Prism(taper_top, height=mp.inf, material=mat_core))
        taper_bot = [
            mp.Vector3(L_MMI/2, -Y_OUT - W_TAPER/2, 0),
            mp.Vector3(L_MMI/2 + L_TAPER, -Y_OUT - W_PORT/2, 0),
            mp.Vector3(L_MMI/2 + L_TAPER, -Y_OUT + W_PORT/2, 0),
            mp.Vector3(L_MMI/2, -Y_OUT + W_TAPER/2, 0),
        ]
        geom.append(mp.Prism(taper_bot, height=mp.inf, material=mat_core))
        
        # Active Patch
        if dn > 0:
            mat_p = mp.Medium(index=N_CORE + dn)
            geom.append(mp.Block(mp.Vector3(l_p, w_p, mp.inf), center=mp.Vector3(x_c, y_c, 0), material=mat_p))
            
        sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
        m_top = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out,  Y_OUT, 0), size=mp.Vector3(0, mon_w, 0)))
        m_bot = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon_out, -Y_OUT, 0), size=mp.Vector3(0, mon_w, 0)))
        sim.run(until=90.0)
        
        pt = abs(sim.get_eigenmode_coefficients(m_top, [1]).alpha[0, 0, 0])**2 / p_ref
        pb = abs(sim.get_eigenmode_coefficients(m_bot, [1]).alpha[0, 0, 0])**2 / p_ref
        results[state] = (pt, pb, pt + pb)
        print(f"  {state.upper()}: P_top = {pt*100:.2f}%, P_bot = {pb*100:.2f}%, Total = {(pt+pb)*100:.2f}%")
        
    return results

# Test Configuration A: Upper Lobe Patch (Isolated from center line y=0)
# y_c = 0.40 um, w_p = 0.50 um (spans y in [0.15, 0.65]), length = 3.2 um
resA = test_patch_geometry("Upper Lobe Isolated Patch", x_c=0.2, l_p=3.2, y_c=0.40, w_p=0.50, dn_am=0.0, dn_cr=0.145)

# Test Configuration B: Upper Half with Offset from Input Face (x_c = 0.4, L=2.8 um)
resB = test_patch_geometry("Upper Half (Delayed from Input)", x_c=0.4, l_p=2.8, y_c=0.40, w_p=0.70, dn_am=0.0, dn_cr=0.145)
