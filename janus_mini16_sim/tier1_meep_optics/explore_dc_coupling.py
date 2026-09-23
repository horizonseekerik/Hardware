import numpy as np
import meep as mp
from meep import mpb

LAMBDA_0 = 1.064
FCEN = 1.0 / LAMBDA_0
N_CLAD = 1.449
N_CORE = 2.850

def calc_coupling_length(w_wg, gap, resolution=64):
    """
    Computes neff_even, neff_odd, and Lc for two coupled 1D slab/rib waveguides in cross section.
    Using MPB in 1D along y (supermodes).
    """
    sy = 4.0
    y_sep = w_wg + gap
    
    # In MPB, k is along x (waveguide propagation direction).
    # Since it's a 1D transverse cross-section along y:
    # geometry_lattice = mp.Lattice(size=mp.Vector3(0, sy, 0))
    # We find kx for a given frequency FCEN.
    
    # Or simpler: run a 2D MPB with sx=0, sz=0, sy=sy
    geometry_lattice = mp.Lattice(size=mp.Vector3(0, sy, 0))
    
    geometry = [
        mp.Block(
            size=mp.Vector3(mp.inf, w_wg, mp.inf),
            center=mp.Vector3(0, y_sep / 2.0, 0),
            material=mp.Medium(index=N_CORE)
        ),
        mp.Block(
            size=mp.Vector3(mp.inf, w_wg, mp.inf),
            center=mp.Vector3(0, -y_sep / 2.0, 0),
            material=mp.Medium(index=N_CORE)
        )
    ]
    
    # Find mode frequencies for a guess kx, or use find_k
    # Typically kx = n_eff * FCEN
    # Let's use find_k
    ms = mpb.ModeSolver(
        geometry_lattice=geometry_lattice,
        geometry=geometry,
        resolution=resolution,
        default_material=mp.Medium(index=N_CLAD),
    )
    
    ms.verbosity = 0
    k_guess = (N_CORE + N_CLAD) / 2.0 * FCEN
    tol = 1e-4
    
    # Mode 1: Even supermode
    k_even = ms.find_k(mp.EVEN_Y, FCEN, 1, 1, mp.Vector3(1, 0, 0), tol, k_guess, N_CLAD*FCEN, N_CORE*FCEN)
    # Mode 2: Odd supermode
    k_odd = ms.find_k(mp.ODD_Y, FCEN, 1, 1, mp.Vector3(1, 0, 0), tol, k_guess, N_CLAD*FCEN, N_CORE*FCEN)
    
    n_even = k_even[0] / FCEN
    n_odd = k_odd[0] / FCEN
    dn = n_even - n_odd
    lc = LAMBDA_0 / (2.0 * dn) if dn > 1e-6 else np.inf
    
    return n_even, n_odd, dn, lc

print(f"{'W_wg (nm)':<10} {'Gap (nm)':<10} {'n_even':<10} {'n_odd':<10} {'Delta_n':<10} {'Lc (um)':<10}")
print("-" * 65)
for w in [320, 350, 380, 400]:
    for g in [80, 100, 120, 140]:
        n_e, n_o, dn, lc = calc_coupling_length(w/1000.0, g/1000.0, resolution=100)
        print(f"{w:<10} {g:<10} {n_e:<10.4f} {n_o:<10.4f} {dn:<10.4f} {lc:<10.2f}")
