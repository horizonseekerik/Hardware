import math
import numpy as np
import meep as mp
from dc_geom_utils import make_true_sbend_polygon, make_parabolic_patch_polygon

LAMBDA_0 = 1.064
FCEN = 1.0 / LAMBDA_0
DF = 0.08 * FCEN
N_CLAD = 1.449
N_CORE = 2.850
DPML = 0.8
RESOLUTION = 40

def test_normalization(w_wg=0.28):
    sx = 10.0
    sy = 3.6
    cell = mp.Vector3(sx, sy, 0)
    mat_core = mp.Medium(index=N_CORE)
    mat_clad = mp.Medium(index=N_CLAD)
    
    x_src = -sx/2 + DPML + 0.3
    x_mon = sx/2 - DPML - 0.3
    mon_w = w_wg * 2.5
    
    src = mp.EigenModeSource(
        src=mp.GaussianSource(FCEN, fwidth=DF),
        center=mp.Vector3(x_src, 0, 0),
        size=mp.Vector3(0, mon_w, 0),
        eig_band=1, eig_match_freq=True, direction=mp.X
    )
    
    geom = [mp.Block(mp.Vector3(sx, w_wg, mp.inf), center=mp.Vector3(0, 0, 0), material=mat_core)]
    sim = mp.Simulation(cell_size=cell, boundary_layers=[mp.PML(DPML)], geometry=geom, sources=[src], resolution=RESOLUTION, default_material=mat_clad)
    
    # Check both flux and mode coeff
    mon_mode = sim.add_mode_monitor(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon, 0, 0), size=mp.Vector3(0, mon_w, 0)))
    mon_flux = sim.add_flux(FCEN, 0, 1, mp.FluxRegion(center=mp.Vector3(x_mon, 0, 0), size=mp.Vector3(0, mon_w, 0)))
    
    sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Ez, mp.Vector3(x_mon, 0, 0), 1e-6))
    
    flux_val = mp.get_fluxes(mon_flux)[0]
    coeff = sim.get_eigenmode_coefficients(mon_mode, [1])
    alpha_fwd = coeff.alpha[0, 0, 0] # forward mode amplitude
    mode_pwr = abs(alpha_fwd)**2
    
    print(f"Poynting Flux = {flux_val:.6e}")
    print(f"Eigenmode Coeff Power = {mode_pwr:.6e}")
    print(f"Ratio Flux / ModePwr = {flux_val / mode_pwr:.4f}")

if __name__ == "__main__":
    test_normalization()
