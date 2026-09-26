import os
import matplotlib.pyplot as plt
import numpy as np

# Set styling for publication-grade crispness
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'axes.edgecolor': '#334155',
    'axes.linewidth': 1.0,
    'mathtext.fontset': 'dejavusans',
})

out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ofc_paper_latex", "figures")
os.makedirs(out_dir, exist_ok=True)

# =========================================================================
# 1-Graph Clean Fig 1(a): Dedicated 4-Stage Fermat Routing Architecture
# =========================================================================
fig_a, ax0 = plt.subplots(figsize=(3.4, 1.35), dpi=300)

nodes = {}
nodes[0] = [8.5]
for s in range(1, 5):
    n_nodes = 2**s
    if s == 4:
        nodes[s] = list(range(1, 17))
    else:
        span = 15.0 / n_nodes
        nodes[s] = [1.0 + span * 0.5 + i * span for i in range(n_nodes)]

# Passive unselected paths
for s in range(4):
    parents = nodes[s]
    children = nodes[s+1]
    for i, py in enumerate(parents):
        ax0.plot([s, s+1], [py, children[2*i]], color='#cbd5e1', lw=1.0, alpha=0.7, zorder=1)
        ax0.plot([s, s+1], [py, children[2*i + 1]], color='#cbd5e1', lw=1.0, alpha=0.7, zorder=1)

# Switch couplers (stages 0 to 3)
for s in range(4):
    for py in nodes[s]:
        ax0.scatter(s, py, color='#0284c7', s=20, zorder=3, edgecolors='#0369a1', linewidth=0.6)

# 16 Output waveguides
ax0.scatter([4]*16, nodes[4], color='#10b981', s=24, zorder=4, label='16 Outputs ($WG_1..WG_{16}$)')

# Active routed path (e.g. Y=11)
route_indices = [0, 1, 2, 5, 10]
route_coords = [(s, nodes[s][route_indices[s]]) for s in range(5)]

ax0.plot([-0.6, 0], [8.5, 8.5], color='#d97706', lw=2.4, zorder=5)
ax0.scatter([-0.6], [8.5], color='#d97706', s=45, marker='*', zorder=6, label='Input Pulse ($WG_i$)')

for s in range(4):
    x0, y0 = route_coords[s]
    x1, y1 = route_coords[s+1]
    ax0.plot([x0, x1], [y0, y1], color='#d97706', lw=2.4, zorder=5)
    ax0.scatter(x0, y0, color='#d97706', s=22, zorder=6)

ax0.scatter(4, 11, color='#dc2626', s=38, marker='D', zorder=6, label='Active Path ($Y=11$)')

# Passive Zero Bypass
ax0.plot([-0.6, 4.3], [0, 0], color='#475569', linestyle=':', lw=1.5, label='$WG_0$ Zero Bypass')
ax0.scatter([4], [0], color='#475569', s=24, zorder=4)

ax0.set_title(r'4-Stage Asymmetric 16-Tree Fermat Core', fontsize=8.2, weight='bold', pad=3)
ax0.set_xlabel('Optical Switch Stage', fontsize=7.2, weight='semibold', labelpad=1)
ax0.set_ylabel('Spatial Channel', fontsize=7.2, weight='semibold', labelpad=1)
ax0.set_xticks(range(5))
ax0.set_xticklabels(['Stg 1', 'Stg 2', 'Stg 3', 'Stg 4', 'Outputs'], fontsize=6.8)
ax0.set_yticks([0, 4, 8, 12, 16])
ax0.tick_params(axis='both', which='major', labelsize=6.8, pad=1)
ax0.set_ylim(-1.5, 21.0)
ax0.set_xlim(-0.8, 4.4)
ax0.grid(True, linestyle=':', alpha=0.45)
ax0.legend(loc='upper left', ncol=2, fontsize=5.8, framealpha=0.94, borderpad=0.2, handletextpad=0.25, labelspacing=0.2)

# Annotation for Fermat Radix-16 Reduction
ax0.text(0.02, 1.2, r'Radix-16 $\mathbb{Z}_{257}$: $(16^2 Y_H + Y_L) \equiv (Y_L - Y_H)\ (\mathrm{mod}\ 257)$' + '\n' + r'Tree 16 Negation: $16W \equiv -W\ (\mathrm{mod}\ 17)$',
         fontsize=5.8, weight='medium', bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8fafc', edgecolor='#64748b', lw=0.7, alpha=0.95))

fig_a.tight_layout(pad=0.2)
fig_a.savefig(os.path.join(out_dir, "fig_asymmetric_16tree_fermat_topology.png"), dpi=300)
fig_a.savefig(os.path.join(out_dir, "fig_asymmetric_16tree_fermat_topology.pdf"))
fig_a.savefig(os.path.join(out_dir, "single_fig1a_clean.png"), dpi=300)
plt.close(fig_a)

# =========================================================================
# Fig 1(b): 13-Stage Cascaded MMI Tree Loss
# =========================================================================
fig_b, bx0 = plt.subplots(figsize=(3.4, 1.35), dpi=300)

stages = np.arange(1, 14)
ideal_split = 3.0103 * stages
mean_excess = 0.14 * stages
sigma_excess = 0.015 * np.sqrt(stages)

bx0.plot(stages, ideal_split, color='#475569', linestyle='--', lw=1.6, label='Ideal Split (3.01 dB/stg)')
bx0.plot(stages, ideal_split + mean_excess, color='#0284c7', lw=2.2, label='Mean Loss (+0.14 dB/stg)')
bx0.fill_between(stages, ideal_split + mean_excess - 3*sigma_excess,
                 ideal_split + mean_excess + 3*sigma_excess, color='#38bdf8', alpha=0.38, label=r'$\pm 3\sigma$ Litho Band')

bx0.set_title('13-Stage MMI Distribution Tree (1:8192 Split)', fontsize=8.2, weight='bold', pad=3)
bx0.set_xlabel('MMI Stage Depth (1 to 13)', fontsize=7.2, weight='semibold', labelpad=1)
bx0.set_ylabel('Cumulative Loss (dB)', fontsize=7.2, weight='semibold', labelpad=1)
bx0.set_xticks(range(1, 14, 2))
bx0.set_xticklabels([f'S{s} (1:{2**s if 2**s < 1000 else str(2**s//1000)+"k"})' for s in range(1, 14, 2)], fontsize=6.2)
bx0.set_yticks([0, 10, 20, 30, 40])
bx0.tick_params(axis='both', which='major', labelsize=6.8, pad=1)
bx0.set_xlim(0.8, 13.2)
bx0.set_ylim(-1.5, 46.0)
bx0.grid(True, linestyle=':', alpha=0.45)
bx0.legend(loc='upper left', fontsize=6.0, framealpha=0.94, borderpad=0.2, handletextpad=0.25, labelspacing=0.2)

# Annotation for Total Loss & Delivered Power
bx0.text(6.8, 8.5, 'Stage-13 Loss: ' + r'$-40.95\,\mathrm{dB}$' + '\n' + 'Delivered $P_{\mathrm{rx}}$: ' + r'$-14.63\,\mathrm{dBm}$',
         fontsize=6.2, weight='medium', bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8fafc', edgecolor='#64748b', lw=0.7, alpha=0.95))

fig_b.tight_layout(pad=0.2)
fig_b.savefig(os.path.join(out_dir, "fig_mc_cascaded_mmi_loss.png"), dpi=300)
fig_b.savefig(os.path.join(out_dir, "fig_mc_cascaded_mmi_loss.pdf"))
fig_b.savefig(os.path.join(out_dir, "single_fig1b_clean.png"), dpi=300)
plt.close(fig_b)

print("Single graph figures generated successfully with high readability.")
