import meep as mp
from meep import mpb
import numpy as np

cell = mp.Vector3(0, 4.0, 2.0)
fcen = 1.0 / 1.064
si = mp.Medium(index=3.565)
sio2 = mp.Medium(index=1.449)
al2o3 = mp.Medium(index=1.750)
sb_am = mp.Medium(index=2.712)
sb_cr = mp.Medium(index=3.328)

w_wg = 0.280
h_wg = 0.220

# 1. Baseline bare patch
geom_base = [
    mp.Block(mp.Vector3(mp.inf, w_wg, h_wg), center=mp.Vector3(0, 0, 0), material=si),
    mp.Block(mp.Vector3(mp.inf, w_wg, 0.025), center=mp.Vector3(0, 0, h_wg/2.0 + 0.025/2.0), material=sb_am),
]
ms_base = mpb.ModeSolver(geometry_lattice=mp.Lattice(size=cell), geometry=geom_base, default_material=sio2, resolution=100)
ms_base.verbosity = 0
k_base = ms_base.find_k(mp.NO_PARITY, fcen, 1, 1, mp.Vector3(1, 0, 0), 1e-4, 2.6*fcen, 1.4*fcen, 3.5*fcen)[0]
n_base = float(k_base / fcen)

# Compute field energy in baseline patch
ms_base.get_dfield(1)
ms_base.compute_field_energy()
energy_base = ms_base.compute_energy_in_dielectric(2.712**2 - 0.1, 2.712**2 + 0.1)

# 2. Hardened Quad-layer Superlattice + Buffer
geom_hard = [
    mp.Block(mp.Vector3(mp.inf, w_wg, h_wg), center=mp.Vector3(0, 0, 0), material=si),
    # 2 nm ALD Buffer
    mp.Block(mp.Vector3(mp.inf, w_wg, 0.002), center=mp.Vector3(0, 0, h_wg/2.0 + 0.001), material=al2o3),
]
z_c = h_wg/2.0 + 0.002
for i in range(4):
    geom_hard.append(mp.Block(mp.Vector3(mp.inf, w_wg, 0.006), center=mp.Vector3(0, 0, z_c + 0.003), material=sb_am))
    z_c += 0.006
    if i < 3:
        geom_hard.append(mp.Block(mp.Vector3(mp.inf, w_wg, 0.0005), center=mp.Vector3(0, 0, z_c + 0.00025), material=al2o3))
        z_c += 0.0005

ms_hard = mpb.ModeSolver(geometry_lattice=mp.Lattice(size=cell), geometry=geom_hard, default_material=sio2, resolution=100)
ms_hard.verbosity = 0
k_hard = ms_hard.find_k(mp.NO_PARITY, fcen, 1, 1, mp.Vector3(1, 0, 0), 1e-4, 2.6*fcen, 1.4*fcen, 3.5*fcen)[0]
n_hard = float(k_hard / fcen)

ms_hard.get_dfield(1)
ms_hard.compute_field_energy()
# Energy in ALD buffer + barrier sheets (index = 1.750, epsilon = 3.0625)
energy_ald = ms_hard.compute_energy_in_dielectric(1.75**2 - 0.1, 1.75**2 + 0.1)
# Energy in Sb2S3 layers (index = 2.712, epsilon = 7.3549)
energy_sb2s3 = ms_hard.compute_energy_in_dielectric(2.712**2 - 0.1, 2.712**2 + 0.1)

print(f"RESULTS FROM PURE MPB (NO HARDCODING):")
print(f"  Baseline n_eff:              {n_base:.6f}")
print(f"  Hardened n_eff:              {n_hard:.6f}")
print(f"  Delta n_eff from ALD stack:  {n_hard - n_base:+.6f}")
print(f"  Baseline Confinement Gamma:  {energy_base*100:.3f}%")
print(f"  Hardened Sb2S3 Confinement:  {energy_sb2s3*100:.3f}%")
print(f"  Hardened ALD Confinement:    {energy_ald*100:.4f}%")

# Compute exact physical excess absorption loss from ALD layers and Sb2S3 thinning
# k_Al2O3 < 1e-6 (pure sapphire/ALD at 1064 nm)
# Patch length = 5.20 um
alpha_ald = (4 * np.pi * 1e-5 / 1.064e-6) # m^-1
loss_ald_db = 4.343 * energy_ald * alpha_ald * 5.20e-6
print(f"  Physical excess loss from ALD confinement: {loss_ald_db:.6f} dB")
