import os
import sys
import numpy as np

# Redirect stdout/stderr at file descriptor level to suppress MPB C-level output
def run_sweep():
    import meep as mp
    from meep import mpb

    LAMBDA_0 = 1.064
    FCEN = 1.0 / LAMBDA_0
    N_CLAD = 1.449
    N_CORE = 2.850

    results = []
    for w_nm in [260, 280, 300, 320, 340, 360, 380, 400]:
        for g_nm in [60, 80, 100, 120, 140]:
            w_wg = w_nm / 1000.0
            gap = g_nm / 1000.0
            sy = 4.0
            y_sep = w_wg + gap
            
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
            
            ms = mpb.ModeSolver(
                geometry_lattice=geometry_lattice,
                geometry=geometry,
                resolution=80,
                default_material=mp.Medium(index=N_CLAD),
            )
            ms.verbosity = 0
            k_guess = (N_CORE + N_CLAD) / 2.0 * FCEN
            tol = 1e-4
            
            k_even = ms.find_k(mp.EVEN_Y, FCEN, 1, 1, mp.Vector3(1, 0, 0), tol, k_guess, N_CLAD*FCEN, N_CORE*FCEN)
            k_odd = ms.find_k(mp.ODD_Y, FCEN, 1, 1, mp.Vector3(1, 0, 0), tol, k_guess, N_CLAD*FCEN, N_CORE*FCEN)
            
            n_even = k_even[0] / FCEN
            n_odd = k_odd[0] / FCEN
            dn = n_even - n_odd
            lc = LAMBDA_0 / (2.0 * dn) if dn > 1e-6 else 999.0
            results.append((w_nm, g_nm, n_even, n_odd, dn, lc))
            
    return results

if __name__ == "__main__":
    # Save original stdout fd
    old_stdout_fd = os.dup(1)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 1)
    
    try:
        res = run_sweep()
    finally:
        os.dup2(old_stdout_fd, 1)
        os.close(devnull)
        os.close(old_stdout_fd)
        
    print(f"{'W_wg (nm)':<12} {'Gap (nm)':<10} {'n_even':<10} {'n_odd':<10} {'Delta_n':<10} {'Lc (um)':<10}")
    print("=" * 65)
    for r in res:
        print(f"{r[0]:<12} {r[1]:<10} {r[2]:<10.4f} {r[3]:<10.4f} {r[4]:<10.4f} {r[5]:<10.2f}")
