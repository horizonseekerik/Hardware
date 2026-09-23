import os
import numpy as np
import matplotlib.pyplot as plt

def generate_corrected_fig1():
    fig = plt.figure(figsize=(14, 6.0), dpi=300)
    gs = fig.add_gridspec(2, 2, hspace=0.30, wspace=0.20, top=0.94, bottom=0.08, left=0.06, right=0.95)

    # -------------------------------------------------------------
    # Panel (a): Corrected Binary Tree Routing Topology
    # -------------------------------------------------------------
    ax0 = fig.add_subplot(gs[0, 0])

    # Tree geometry: 4 binary stages (1 -> 2 -> 4 -> 8 -> 16)
    # Stage x coordinates: 0, 1, 2, 3, 4 (Outputs)
    nodes = {}
    nodes[0] = [8.5]
    for s in range(1, 5):
        n_nodes = 2**s
        # Spacing strictly within 1 to 16
        # At s=4 (Outputs): 1, 2, 3, ..., 16
        if s == 4:
            nodes[s] = list(range(1, 17))
        else:
            span = 15.0 / n_nodes
            nodes[s] = [1.0 + span * 0.5 + i * span for i in range(n_nodes)]

    # Draw all tree branches (parent to 2 children)
    for s in range(4):
        parents = nodes[s]
        children = nodes[s+1]
        for i, py in enumerate(parents):
            c1_y = children[2*i]
            c2_y = children[2*i + 1]
            ax0.plot([s, s+1], [py, c1_y], color='#94a3b8', lw=1.0, alpha=0.5, zorder=1)
            ax0.plot([s, s+1], [py, c2_y], color='#94a3b8', lw=1.0, alpha=0.5, zorder=1)

    # Plot switch nodes for stages 0..3 (15 switches per tree)
    for s in range(4):
        for py in nodes[s]:
            ax0.scatter(s, py, color='#0284c7', s=35, zorder=3, edgecolors='#0369a1', linewidth=0.8)

    # Plot output channels at stage 4 (16 active outputs)
    ax0.scatter([4]*16, nodes[4], color='#10b981', s=45, zorder=4, label=r"16 Active Channels ($WG_1 \dots WG_{16}$)")

    # Trace one active optical path (e.g., routing to channel 11)
    route_indices = [0, 1, 2, 5, 10]
    route_coords = [(s, nodes[s][route_indices[s]]) for s in range(5)]

    # Input line to root switch
    ax0.plot([-0.6, 0], [8.5, 8.5], color='#f59e0b', lw=2.0, zorder=5)
    ax0.scatter([-0.6], [8.5], color='#f59e0b', s=70, marker='*', zorder=6, label=r"Input Pulse ($WG_i$)")

    # Active trajectory
    for s in range(4):
        x0, y0 = route_coords[s]
        x1, y1 = route_coords[s+1]
        ax0.plot([x0, x1], [y0, y1], color='#f59e0b', lw=2.0, zorder=5)
        ax0.scatter(x0, y0, color='#f59e0b', s=35, zorder=6)

    ax0.scatter(4, 11, color='#ef4444', s=70, marker='D', zorder=6, label=r"Active Output ($Y = 11$)")

    # Passive Dark Reference WG_0
    ax0.plot([-0.6, 4.2], [0, 0], color='#64748b', linestyle=':', lw=1.6, label=r"$WG_0$ Passive Zero Bypass")
    ax0.scatter([4], [0], color='#64748b', s=45, zorder=4)

    ax0.set_title(r"(a) Asymmetric 16-Tree Routing ($\log_2 16 = 4$ Binary Stages, 15 Switches)", fontsize=8.8, weight='bold', pad=3)
    ax0.set_xlabel("Optical Stage Depth", fontsize=7.8, labelpad=1)
    ax0.set_ylabel("Spatial Output Channel", fontsize=7.8, labelpad=2)
    ax0.set_xticks(range(5))
    ax0.set_xticklabels(["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Outputs"], fontsize=7.2)
    ax0.set_yticks([0, 4, 8, 12, 16])
    ax0.tick_params(labelsize=7.2, pad=1)
    ax0.set_ylim(-1.0, 17.2)
    ax0.grid(True, linestyle=':', alpha=0.4)
    ax0.legend(loc="upper left", fontsize=6.5, framealpha=0.9)

    # -------------------------------------------------------------
    # Panel (b): Full Z_17 Multiplication Matrix (289 / 289 States)
    # -------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 1])
    A_vals = np.arange(17)
    B_vals = np.arange(17)
    Z17_matrix = np.zeros((17, 17))
    for a in A_vals:
        for b in B_vals:
            Z17_matrix[a, b] = (a * b) % 17

    c1 = ax1.imshow(Z17_matrix, cmap='viridis', origin='lower')
    ax1.set_title(r"(b) Full $\mathbb{Z}_{17}$ Multiplication Space ($289/289$ States Mapped)", fontsize=8.8, weight='bold', pad=3)
    ax1.set_xlabel(r"Weight Operand $B \in [0, 16]$", fontsize=7.8, labelpad=1)
    ax1.set_ylabel(r"Input Operand $A \in [0, 16]$", fontsize=7.8, labelpad=2)
    ax1.set_xticks(range(0, 17, 4))
    ax1.set_yticks(range(0, 17, 4))
    ax1.tick_params(labelsize=7.2, pad=1)
    ax1.axhline(16, color='#ef4444', lw=1.5, linestyle='--', label=r"Tree 16 Negation: $16 \times W \equiv -W\ (\mathrm{mod}\ 17)$")
    cbar1 = fig.colorbar(c1, ax=ax1, fraction=0.046, pad=0.03)
    cbar1.set_label(r"Residue $(A \times B)\ (\mathrm{mod}\ 17)$", fontsize=7.5)
    cbar1.ax.tick_params(labelsize=7.0)
    ax1.legend(loc="upper right", fontsize=6.5)

    # -------------------------------------------------------------
    # Panel (c): Radix-16 Z_257 Modular Reduction Landscape
    # -------------------------------------------------------------
    ax2 = fig.add_subplot(gs[1, 0])
    YH = np.linspace(0, 16, 80)
    YL = np.linspace(0, 16, 80)
    YHm, YLm = np.meshgrid(YH, YL)
    Z257_reduction = (YLm - YHm) % 257

    c2 = ax2.pcolormesh(YHm, YLm, Z257_reduction, cmap='plasma', shading='auto')
    ax2.set_title(r"(c) Radix-16 $\mathbb{Z}_{257}$ Division-Free Reduction: $(Y_L - Y_H)\ (\mathrm{mod}\ 257)$", fontsize=8.8, weight='bold', pad=3)
    ax2.set_xlabel(r"High Radix-16 Digit $Y_H \in [0, 16]$", fontsize=7.8, labelpad=1)
    ax2.set_ylabel(r"Low Radix-16 Digit $Y_L \in [0, 16]$", fontsize=7.8, labelpad=2)
    ax2.tick_params(labelsize=7.2, pad=1)
    cbar2 = fig.colorbar(c2, ax=ax2, fraction=0.046, pad=0.03)
    cbar2.set_label(r"Reduced Modulo 257 Value", fontsize=7.5)
    cbar2.ax.tick_params(labelsize=7.0)
    ax2.text(8.0, 8.0, r"Zero Integer Division" + "\n" + r"$16^2 \equiv -1\ (\mathrm{mod}\ 257)$", color='white', fontsize=7.5, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.75))

    # -------------------------------------------------------------
    # Panel (d): Hardware Scaling Comparison (Beneš vs 16-Tree Fermat)
    # -------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 1])
    metrics = ["Switches/Mult", "Optical Stages", "Fabric Loss (dB)", "Delay (ps)"]
    benes_norm = [1.0, 1.0, 1.0, 1.0]
    tree16_norm = [240/1920, 4/15, 1.61/7.50, 1.33/750.0]

    x_bar = np.arange(len(metrics))
    width = 0.35

    ax3.bar(x_bar - width/2, benes_norm, width, label='Legacy Beneš Mesh', color='#94a3b8')
    ax3.bar(x_bar + width/2, tree16_norm, width, label='16-Tree Fermat Core', color='#10b981')

    ax3.set_title(r"(d) Hardware Reduction Impact: 16-Tree Fermat vs. Beneš", fontsize=8.8, weight='bold', pad=3)
    ax3.set_ylabel("Normalized Value (Beneš = 1.0)", fontsize=7.8, labelpad=2)
    ax3.set_xticks(x_bar)
    ax3.set_xticklabels(metrics, fontsize=7.2)
    ax3.tick_params(labelsize=7.2, pad=1)
    ax3.set_yscale('log')
    ax3.set_ylim(0.001, 2.0)
    ax3.grid(True, which='both', linestyle=':', alpha=0.5)
    ax3.legend(loc="upper right", fontsize=6.8)

    ax3.text(0 + width/2, tree16_norm[0]*1.4, r"$-87.5\%$", ha='center', fontsize=7.2, weight='bold', color='#047857')
    ax3.text(1 + width/2, tree16_norm[1]*1.4, r"$-73.3\%$", ha='center', fontsize=7.2, weight='bold', color='#047857')
    ax3.text(2 + width/2, tree16_norm[2]*1.4, r"$-78.5\%$", ha='center', fontsize=7.2, weight='bold', color='#047857')
    ax3.text(3 + width/2, tree16_norm[3]*1.6, r"$-99.8\%$", ha='center', fontsize=7.2, weight='bold', color='#047857')

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dirs = [
        os.path.join(base_dir, "ofc_paper_latex", "figures"),
        os.path.join(base_dir, "simulation_paper_latex", "figures"),
        os.path.join(base_dir, "cmos_paper_latex", "figures")
    ]
    for d in out_dirs:
        os.makedirs(d, exist_ok=True)
        fig.savefig(os.path.join(d, "fig_asymmetric_16tree_fermat_topology.png"), bbox_inches='tight')
    plt.close(fig)
    print("SUCCESS: fig_asymmetric_16tree_fermat_topology.png regenerated with correct binary tree routing!")

if __name__ == "__main__":
    generate_corrected_fig1()
