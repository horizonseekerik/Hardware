import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def make_composites():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fig_dir = os.path.join(base_dir, "ofc_paper_latex", "figures")

    # 1. Composite Fig 2: Layout & Tolerance (GDSII + PDF + Semilog CDF)
    gds_path = os.path.join(fig_dir, "fig_gds_die_and_tile_floorplan.png")
    pdf_path = os.path.join(fig_dir, "fig_mc_histogram_pdf_1m.png")
    cdf_path = os.path.join(fig_dir, "fig_mc_yield_cdf_semilog.png")

    if os.path.exists(gds_path) and os.path.exists(pdf_path) and os.path.exists(cdf_path):
        img_gds = mpimg.imread(gds_path)
        img_pdf = mpimg.imread(pdf_path)
        img_cdf = mpimg.imread(cdf_path)

        fig = plt.figure(figsize=(12, 5.5), dpi=300)
        gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 1.0], wspace=0.18)

        # Left: GDS II layout
        ax0 = fig.add_subplot(gs[0])
        ax0.imshow(img_gds)
        ax0.axis('off')
        ax0.set_title(r"(a) Monolithic $10.24\,\mathrm{mm}^2$ Die & Tile Layout", fontsize=10, weight='bold', pad=6)

        # Right: Subdivided into PDF and CDF
        gs_r = gs[1].subgridspec(2, 1, hspace=0.28)
        ax1 = fig.add_subplot(gs_r[0])
        ax1.imshow(img_pdf)
        ax1.axis('off')
        ax1.set_title(r"(b) 1,000,000-Sample Margin PDF ($3\sigma = +6.95\,\mathrm{dB}$)", fontsize=9.5, weight='bold', pad=4)

        ax2 = fig.add_subplot(gs_r[1])
        ax2.imshow(img_cdf)
        ax2.axis('off')
        ax2.set_title(r"(c) Optical Yield Semilog CDF (Gaussian-Fit $5\sigma = +6.85\,\mathrm{dB}$)", fontsize=9.2, weight='bold', pad=4)

        fig.savefig(os.path.join(fig_dir, "fig_layout_and_tolerance.png"), bbox_inches='tight')
        plt.close(fig)
        print("Generated fig_layout_and_tolerance.png successfully.")

    # 2. Composite Fig 3: 100-GHz Receiver (Eye Diagram + Regeneration Delay Histogram)
    eye_path = os.path.join(fig_dir, "fig_spice_1m_eye_density_heatmap.png")
    hist_path = os.path.join(fig_dir, "fig_spice_strongarm_regen_histogram_1m.png")

    if os.path.exists(eye_path) and os.path.exists(hist_path):
        img_eye = mpimg.imread(eye_path)
        img_hist = mpimg.imread(hist_path)

        fig = plt.figure(figsize=(11, 4.8), dpi=300)
        gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.16)

        ax0 = fig.add_subplot(gs[0])
        ax0.imshow(img_eye)
        ax0.axis('off')
        ax0.set_title(r"(a) 1,000,000-Cycle 100 GHz Eye ($73.9\%$ Opening, $122.6\,\mathrm{mV}$)", fontsize=10, weight='bold', pad=6)

        ax1 = fig.add_subplot(gs[1])
        ax1.imshow(img_hist)
        ax1.axis('off')
        ax1.set_title(r"(b) StrongARM Regeneration Delay Distribution ($T_{\mathrm{cycle}} = 10.0\,\mathrm{ps}$)", fontsize=10, weight='bold', pad=6)

        fig.savefig(os.path.join(fig_dir, "fig_receiver_100ghz.png"), bbox_inches='tight')
        plt.close(fig)
        print("Generated fig_receiver_100ghz.png successfully.")

if __name__ == "__main__":
    make_composites()
