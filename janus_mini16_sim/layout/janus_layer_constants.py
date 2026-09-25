"""
PROJECT JANUS MINI-16: UNIFIED PHYSICAL MASK LAYER CONSTANTS
=============================================================
Single source-of-truth for ALL GDS II layer numbers, datatypes,
and canonical physical dimensions used by both:
  - generate_cmos_base_gds.py  (65nm CMOS base die)
  - generate_mini16_gds.py     (complete 3D monolithic stack)

Layer number allocation (NO overlaps between strata):
  Range   1 –  29 : Top SiPh / Si3N4 Optical Stratum
  Range  30 –  39 : 3D Inter-Stratum Vertical Interconnects
  Range  40 –  49 : Abstract 65nm CMOS Block Annotations (both GDS files)
  Range 100 – 199 : Physical 65nm LP/GP CMOS Mask Layers
  Layers 190, 199 : Die Perimeter & Metrology (shared by both strata)
"""

# ==============================================================================
# TOP SiPh / Si3N4 OPTICAL STRATUM  (Layers 1-29)
# ==============================================================================
LAYER_SI_CORE         = (1,  0)   # Crystalline Si core (450x220 nm, APD mesa base)
LAYER_SIO2_CLAD       = (2,  0)   # SiO2 Upper Cladding & BOX
LAYER_LITAO3_EO       = (3,  0)   # Thin-Film LiTaO3 Electro-Optic Pockels Modulator
LAYER_SB2S3_AMORPH    = (4,  0)   # Sb2S3 Phase-Change Switch (Amorphous / OFF state)
LAYER_SB2S3_CRYST     = (4,  1)   # Sb2S3 Phase-Change Switch (Crystalline / ON state)
LAYER_SIN_CORE        = (5,  0)   # Low-Loss Si3N4 Core (800x300 nm, 0.1 dB/cm)
LAYER_CU_M1           = (10, 0)   # Cu Metal 1 RF Electrodes & Micro-Heaters
LAYER_CU_M2           = (11, 0)   # Cu Metal 2 Global Power/Clock Mesh
LAYER_APD_GE          = (20, 0)   # Ge Epitaxial Absorption Mesa (SAC2M APD)

# ==============================================================================
# 3D INTER-STRATUM VERTICAL INTERCONNECTS  (Layers 30-39)
# ==============================================================================
LAYER_TDV_PILLAR      = (30, 0)   # Vertical Cu Through-Dielectric Vias (8 um diam)
LAYER_UBM_BUMP        = (31, 0)   # Under-Bump Metallization & Micro-Bumps (50 um pitch)
LAYER_THERMAL_BUF     = (32, 0)   # 250 um SiO2 Monolithic Thermal Buffer Boundary

# ==============================================================================
# ABSTRACT 65nm CMOS BLOCK ANNOTATIONS  (Layers 40-49)
# Architectural floorplan outlines.  No physical mask shapes go on these layers.
# ==============================================================================
LAYER_ARCH_STRONGARM  = (40, 0)   # StrongARM Regenerative Sense-Amp Front-End Block
LAYER_ARCH_DESER      = (41, 0)   # 1:32 Polyphase Deserializer Block
LAYER_ARCH_SIMD       = (42, 0)   # 32-Lane SIMD Wallace-Kogge Array Block
LAYER_ARCH_SRAM       = (43, 0)   # 1.5 MB Dual-LUT Volatile SRAM Block
LAYER_ARCH_ROM        = (44, 0)   # 1.5 MB Central ROM & JIR FSM Block
LAYER_ARCH_ACC160     = (45, 0)   # 160-Bit Binary CSA Accumulator Block
LAYER_ARCH_THERMAL    = (46, 0)   # JIR Thermal Diodes & Delta-Sigma ADC Block

# ==============================================================================
# PHYSICAL 65nm LP/GP CMOS MASK LAYERS  (Layers 100-199)
# Offset by +100 vs. conventional CMOS numbering to avoid collision with the
# optical stratum layers (1-20) when both co-exist in the combined 3D GDS file.
# ==============================================================================
LAYER_NW_DIFF         = (101, 0)  # N-Well & Active Diffusion (P/N OD)
LAYER_POLY_GATE       = (102, 0)  # Polysilicon Gate (65nm drawn Lg)
LAYER_CONTACT         = (106, 0)  # Tungsten Contact Plugs
LAYER_METAL1          = (111, 0)  # Metal 1 Local Interconnect & StrongARM sense nodes
LAYER_VIA1            = (112, 0)  # Via 1 Inter-Metal Plugs & Via-ROM Matrix
LAYER_METAL2          = (121, 0)  # Metal 2 Intra-Tile Signal Routing
LAYER_VIA2            = (122, 0)  # Via 2
LAYER_METAL3          = (131, 0)  # Metal 3 Lane Bus & SIMD Cross-Routing
LAYER_VIA3            = (132, 0)  # Via 3
LAYER_METAL4          = (141, 0)  # Metal 4 SRAM Wordline/Bitline Strapping
LAYER_VIA4            = (142, 0)  # Via 4
LAYER_METAL5          = (151, 0)  # Metal 5 Accumulator & CRT Adder Bus
LAYER_VIA5            = (152, 0)  # Via 5
LAYER_METAL6_CLK      = (161, 0)  # Metal 6 3.125 GHz H-Tree Clock Distribution
LAYER_VIA6            = (162, 0)  # Via 6
LAYER_TOP_METAL_PWR   = (171, 0)  # Top Thick Metal VDD/VSS Power Grid
LAYER_PASSIVATION_UBM = (181, 0)  # Passivation Opening & UBM Landing Pads
LAYER_PAD_IO          = (182, 0)  # Wire-Bond & Solder Bump I/O Pads

# ==============================================================================
# DIE PERIMETER & METROLOGY  (Shared; no collision since no optical/CMOS overlap)
# ==============================================================================
LAYER_SEAL_RING       = (190, 0)  # 4-Layer Moisture Barrier Chip Seal Ring
LAYER_FLOORPLAN       = (199, 0)  # Die Boundary & Tile Keep-Out Margins

# ==============================================================================
# CANONICAL PHYSICAL DIMENSIONS  (micrometers, consistent across both scripts)
# ==============================================================================
# --- Die geometry (100.0 mm^2 total chip area) ---
DIE_WIDTH_UM          = 10000.0   # 10.00 mm (identical for both strata)
DIE_HEIGHT_UM         = 10000.0   # 10.00 mm (identical for both strata)

# --- Tile array geometry (4x4 = 16 tiles, 6.25 mm^2 each) ---
NUM_TILES_X           = 4
NUM_TILES_Y           = 4
TILE_CORE_UM          = 2500.0    # 2.50 mm x 2.50 mm core active area per tile (6.25 mm^2)
TILE_PITCH_UM         = 2500.0    # 2.50 mm center-to-center pitch
TILE_ARRAY_ORIGIN_X   = 0.0       # Tiled array origin
TILE_ARRAY_ORIGIN_Y   = 0.0

# --- SIMD Lane & Tree Bay Geometry ---
NUM_LANES_PER_TILE    = 32        # 32 parallel SIMD lanes per tile
NUM_TREES_PER_LANE    = 16        # 16 binary switch trees per lane (one per residue state)
LANE_PITCH_UM         = TILE_CORE_UM / NUM_LANES_PER_TILE  # 78.125 um column pitch
TREE_BAY_HEIGHT_UM    = TILE_CORE_UM / NUM_TREES_PER_LANE  # 156.25 um tree bay height
CHANNEL_PITCH_UM      = LANE_PITCH_UM  # 78.125 um inter-channel pitch (54 um clear dielectric gap)

# --- Optical waveguide dimensions ---
# Conventional port waveguide (Si3N4 strip at ports, outside switch cell)
SIN_WIDTH_UM          = 0.800     # 800 nm Si3N4 conventional strip width (single-mode at 1064 nm)
SI_WIDTH_UM           = 0.450     # 450 nm crystalline Si strip width (APD coupling section)

# ── Slot-waveguide Sb2S3 switch cell (MPB-verified, MEEP FDTD validated) ──
# Architecture: two 350 nm Si3N4 rails + 100 nm Sb2S3-filled slot
# Reference: MPB eigensolve (JANUS v2, 2026) → Γ = 36.0%
# De-coupling node: Γ·L = √3·λ/(2·Δn) = 1.5347 µm → L = 1.5347/0.36 = 4.260 µm
# Cell footprint: 4.260 µm × 0.800 µm = 3.408 µm²  (97% reduction vs legacy 108 µm²)
SIN_RAIL_WIDTH_UM     = 0.350     # 350 nm Si3N4 rail width (each side of slot)
SLOT_WIDTH_UM         = 0.100     # 100 nm Sb2S3-filled slot width (Γ = 36.0%)
COUPLER_LEN_UM        = 4.260     # 4.260 um slot coupling length  [was 8.4 um legacy]
COUPLER_GAP_UM        = 0.100     # 100 nm slot width (= SLOT_WIDTH_UM)  [was 200 nm]
PATCH_LEN_UM          = 4.260     # 4.260 um active Sb2S3 patch length   [was 8.0 um]
PATCH_WIDTH_UM        = 0.100     # 100 nm patch (= slot fill width)      [was 800 nm]
GAMMA_MODAL_OVERLAP   = 0.360     # Γ = 36.0% (MPB vectorial eigensolve, MEEP v1 2026)
SWITCH_CELL_AREA_UM2  = 3.408     # 3.408 µm² per switch cell             [was ~108 µm²]

# Inverse-taper slot coupler (port lead → slot interaction region, outside cell)
INV_TAPER_LEN_UM      = 3.000     # 3.0 um adiabatic inverse taper (Almeida 2004 method)

# MMI splitter
MMI_W_UM              = 2.400     # 2.4 um Si3N4 Talbot MMI multimode width
MMI_L_UM              = 5.800     # 5.8 um self-imaging center length
MMI_TAPER_UM          = 6.000     # 6.0 um MMI access taper length

# Modulator (compact LiTaO3)
LITAO3_LEN_UM         = 120.0     # 120 um LiTaO3 modulator active region length
LITAO3_W_UM           = 2.000     # 2.0 um LiTaO3 waveguide rib width

# --- Photodetector & 3D interconnect ---
APD_LEN_UM            = 10.00     # 10 um Ge absorption mesa length
APD_W_UM              = 1.200     # 1.2 um Ge mesa width
THERMAL_BUF_THICKNESS_UM = 50.0   # 50 um SiO2 thermal buffer (6.25:1 aspect ratio, C_via = 5.92 fF)
TDV_DIAMETER_UM       = 8.000     # 8 um Cu-pillar via diameter
TDV_UBM_OVERHANG_UM   = 1.500     # UBM pad extends 1.5 um beyond TDV radius per side (11 um pad diam)
BUMP_PITCH_UM         = 50.00     # 50 um micro-bump pitch

# --- Grating coupler (2nd-order Si3N4 coupler at operating wavelength) ---
WAVELENGTH_NM         = 1064.0    # 1064 nm operating wavelength (Yb-fiber laser carrier)
GC_TEETH_PERIOD_UM    = 0.725     # 725 nm grating period (2nd-order Si3N4 phase-matched at 1064 nm)
GC_DUTY_CYCLE         = 0.500     # 50% duty cycle
GC_NUM_TEETH          = 22        # Number of grating teeth per coupler
GC_BODY_LEN_UM        = 35.0      # Grating coupler total body length
GC_HALF_WIDTH_UM      = 6.0       # Half-width of grating aperture

# --- I/O pad geometry ---
PAD_SIZE_UM           = 75.0      # 75 um square pad size
PAD_PITCH_UM          = 120.0     # 120 um center-to-center pad pitch

# --- Power distribution ---
PWR_RING_WIDTH_UM     = 40.0      # Global VDD/VSS power ring width
PWR_RING_OFFSET_UM    = 60.0      # Distance of power ring from die edge


# ==============================================================================
# CANONICAL 1:1 TDV COORDINATE GENERATOR (Shared by Optical & CMOS Strata)
# ==============================================================================
def get_leaf_tdv_coordinate(tile_x_idx: int, tile_y_idx: int,
                           lane_idx: int, tree_idx: int,
                           leaf_idx: int) -> tuple[float, float]:
    """
    Deterministic mathematical source of truth for the absolute (X, Y)
    coordinates of every TDV pillar and CMOS UBM landing pad across the 100 mm^2 die.
    Guarantees 0.00 nm misalignment between strata.

    Args:
        tile_x_idx : Horizontal tile index (0 to 3)
        tile_y_idx : Vertical tile index (0 to 3)
        lane_idx   : Parallel SIMD lane index (0 to 31)
        tree_idx   : Binary switch tree index in lane (0 to 15)
        leaf_idx   : Spatial output leaf index in tree (0 to 15)

    Returns:
        (x_abs, y_abs) coordinate tuple in micrometers.
    """
    tile_origin_x = tile_x_idx * TILE_PITCH_UM
    tile_origin_y = tile_y_idx * TILE_PITCH_UM

    lane_x = tile_origin_x + (lane_idx + 0.5) * LANE_PITCH_UM
    tree_y = tile_origin_y + (tree_idx + 0.5) * TREE_BAY_HEIGHT_UM

    # 4x4 leaf sub-grid inside the tree bay (sub-pitch: 16 um in X, 32 um in Y)
    col = leaf_idx % 4
    row = leaf_idx // 4
    dx_leaf = (col - 1.5) * 16.0
    dy_leaf = (row - 1.5) * 32.0

    return (lane_x + dx_leaf, tree_y + dy_leaf)

