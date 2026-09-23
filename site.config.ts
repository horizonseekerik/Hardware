export interface NavItem {
  label: string;
  href: string;
  badge?: string;
  description?: string;
}

export interface MegaCategory {
  title: string;
  items: NavItem[];
}

export interface StatItem {
  label: string;
  value: string;
  unit?: string;
  subtext: string;
  highlight?: boolean;
}

export interface Creator {
  name: string;
  role: string;
  affiliation: string;
  location: string;
  lat: number;
  lng: number;
  avatar: string;
  bio: string;
  links: {
    github?: string;
    doi?: string;
    orcid?: string;
  };
}

export interface FeatureTab {
  id: string;
  title: string;
  badge: string;
  subtitle: string;
  description: string;
  metrics: { label: string; value: string }[];
  codeSnippet: string;
  imagePlaceholder: string;
}

export interface Benefit {
  iconType: "chip" | "laser" | "shield" | "flame" | "binary" | "bolt";
  title: string;
  description: string;
  metric: string;
}

export interface BenchmarkData {
  metric: string;
  unit: string;
  categories: {
    name: string;
    janus6b: number;
    janus1a: number;
    h100: number;
    mziMesh: number;
  }[];
}

export interface Testimonial {
  quote: string;
  author: string;
  role: string;
  institution: string;
  avatarSeed: string;
}

export interface UseCase {
  title: string;
  category: string;
  icon: string;
  description: string;
  advantage: string;
  throughputGain: string;
}

export interface PricingPlan {
  name: string;
  badge?: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  ctaLabel: string;
  ctaHref: string;
  featured?: boolean;
}

export interface FAQItem {
  question: string;
  answer: string;
  category: string;
}

export const siteConfig = {
  name: "Janus - Photonic Hardware",
  shortName: "Project JANUS",
  description: "Spatial Residue Optical Computing Architecture delivering 104.8 PetaMAC/s at ~300W with zero static hold power.",
  url: "https://janus-photonic-hardware.vercel.app",
  ogImage: "https://janus-photonic-hardware.vercel.app/og-image.png",
  googleVerification: "0cvrWvMl9qnHAJ4kDpLUMmj6bmZQsPd1c1wrOu9bo1k",
  doi: "10.5281/zenodo.22733656",
  doiUrl: "https://doi.org/10.5281/zenodo.22733656",
  githubUrl: "https://github.com/horizonseekerik/janus-photonic-hardware",

  // 1. Navigation & Mega-menu
  nav: {
    megaMenu: [
      {
        title: "CORE ARCHITECTURE",
        items: [
          { label: "Spatial One-Hot RNS", href: "#features", description: "Waveguide spatial index encoding replacing analog amplitude" },
          { label: "Sb₂S₃ PCM Crossbar", href: "#features", description: "Non-volatile sub-bandgap optical phase switches at 1064nm" },
          { label: "3D Heterogeneous Stack", href: "#stack", description: "Monolithic CMOS logic die with 250µm microchannel hydraulic cooling" },
          { label: "Receiverless Ge/Si APD", href: "#benefits", description: "Clocked StrongARM dynamic latch co-integration (<3 fF)" }
        ]
      },
      {
        title: "PUBLICATIONS & DATA",
        items: [
          { label: "IEEE Manuscript (39 Pages)", href: "/JANUS_IEEE_Manuscript.pdf", badge: "PDF" },
          { label: "Mini-16 Simulation Spec", href: "/JANUS_Mini16_Simulation_Report.pdf", badge: "IEEEtran" },
          { label: "CMOS Microarchitecture", href: "/JANUS_Mini16_CMOS_Architecture.pdf", badge: "Spec" },
          { label: "Zenodo Permanent Archive", href: "https://doi.org/10.5281/zenodo.22733656", badge: "DOI" }
        ]
      },
      {
        title: "BENCHMARKS & USE CASES",
        items: [
          { label: "AI Workload Comparatives", href: "#benchmarks", description: "H100, B200, and MZI analog mesh side-by-side" },
          { label: "Peta-Scale Model 6B", href: "#benchmarks", description: "104.8 PetaMAC/s hyperscale projection metrics" },
          { label: "Transformer Attention Acceleration", href: "#usecases", description: "FlashAttention optical spatial GEMM kernels" },
          { label: "Pricing & Foundry Access", href: "#pricing", description: "Academic open access & commercial licensing" }
        ]
      }
    ] as MegaCategory[],
    directLinks: [
      { label: "Treatise", href: "/JANUS_IEEE_Manuscript.pdf" },
      { label: "Simulation", href: "#features" },
      { label: "Creators", href: "#creators" },
      { label: "Pricing", href: "#pricing" }
    ]
  },

  // 2. Hero Section
  hero: {
    tag: "8-BIT OPTICAL COMPUTING REVOLUTION",
    titleWords: ["DETERMINISTIC", "SPATIAL", "RESIDUE", "PHOTONIC", "HARDWARE"],
    subhead: "Project JANUS dismantles the 138 dB analog photonic noise floor. By routing photons through spatial one-hot waveguide lattices with non-volatile Sb₂S₃ phase-change switches, JANUS delivers 104.8 PetaMAC/s at zero static hold power—scalable up to exact INT64 deterministic precision.",
    primaryCta: { text: "READ TREATISE (PDF)", href: "/JANUS_IEEE_Manuscript.pdf" },
    secondaryCta: { text: "EXPLORE ARCHITECTURE", href: "#features" },
    metaBadges: ["100 GHz CLOCK", "INT64 PRECISION", "0 W STATIC HOLD"]
  },

  // 3. Quick Stats
  stats: [
    { label: "Clock Frequency", value: "100", unit: "GHz", subtext: "50 fs ILO comb optical pulse sync", highlight: true },
    { label: "Model 6B Throughput", value: "104.8", unit: "PMAC/s", subtext: "Hyperscale 3D photonic cluster projection", highlight: true },
    { label: "Static Hold Power", value: "0", unit: "W", subtext: "Sb₂S₃ non-volatile bistability" },
    { label: "Arithmetic Precision", value: "INT64", unit: "Exact", subtext: "Zero-error Chinese Remainder Theorem" },
    { label: "Bit Error Rate (BER)", value: "≤ 10⁻¹²", unit: "", subtext: "+8.41 dB link budget safety margin" },
    { label: "Planar 1A Efficiency", value: "207.8", unit: "TMAC/s/W", subtext: "3.35 W total package power" }
  ] as StatItem[],

  // 4. Creators Band & 3D Globe Locations
  creatorsSection: {
    badge: "GLOBAL RESEARCH INITIATIVE",
    title: "ARCHITECTURAL PROVENANCE & CREATORS",
    description: "Conceived and modeled at the intersection of integrated silicon photonics, non-volatile phase change materials, and mathematical residue arithmetic.",
    globeLocations: [
      { lat: 37.7749, lng: -122.4194, size: 0.08, name: "Silicon Valley, CA" },
      { lat: 52.2053, lng: 0.1218, size: 0.07, name: "Cambridge, UK" },
      { lat: 35.6762, lng: 139.6503, size: 0.07, name: "Tokyo, Japan" },
      { lat: 47.3769, lng: 8.5417, size: 0.06, name: "Zurich, CH" }
    ],
    creators: [
      {
        name: "Horizon Seeker IK",
        role: "Lead Architect & Hardware Theorist",
        affiliation: "Project JANUS Research Group",
        location: "Autonomous Silicon Photonics Lab",
        lat: 37.7749,
        lng: -122.4194,
        avatar: "/janus-logo.png",
        bio: "Pioneered the spatial one-hot RNS waveguide topology, hydraulic 250µm microchannel heat shunt, and exact INT64 hybrid partitioning architecture.",
        links: {
          github: "https://github.com/horizonseekerik/janus-photonic-hardware",
          doi: "https://doi.org/10.5281/zenodo.22733656"
        }
      },
      {
        name: "Project JANUS Consortium",
        role: "Multi-Physics Verification Group",
        affiliation: "IEEEtran Co-Simulation Audit",
        location: "Global Distributed Foundry Team",
        lat: 52.2053,
        lng: 0.1218,
        avatar: "/janus-logo.png",
        bio: "Executed cross-domain validation spanning MEEP FDTD electromagnetic waves, Elmer FEM thermal fluidics, Xyce SPICE, and Icarus Verilog golden audits.",
        links: {
          github: "https://github.com/horizonseekerik/janus-photonic-hardware"
        }
      }
    ] as Creator[]
  },

  // 5. Feature Tabs
  featureTabs: [
    {
      id: "pcm-switch",
      title: "Sb₂S₃ PCM Optical Switches",
      badge: "NON-VOLATILE OPTICS",
      subtitle: "Zero static hold power with sub-bandgap transparency",
      description: "Unlike volatile lithium niobate or thermo-optic phase shifters requiring permanent electrical bias, antimony trisulfide (Sb₂S₃) exhibits sub-bandgap transparency at 1064 nm (Eg = 1.72 eV > 1.165 eV) with an extinction coefficient κ ≈ 10⁻⁵. State transitions occur via 4.2 pJ graphene micro-heater pulses.",
      metrics: [
        { label: "Switching Energy", value: "4.2 pJ" },
        { label: "Static Hold Power", value: "0.00 mW" },
        { label: "Insertion Loss", value: "0.038 dB" },
        { label: "Endurance", value: "> 10⁹ Cycles" }
      ],
      codeSnippet: `// 16-Tree Spatial Routing Matrix
const uint16_t MOD_VAL = 257; // Fermat F2
waveguide_index = (operand_a * operand_b) % MOD_VAL;
emit_laser_pulse_1064nm(waveguide_index);`,
      imagePlaceholder: "PCM_CROSSBAR"
    },
    {
      id: "spatial-rns",
      title: "Spatial One-Hot RNS",
      badge: "ZERO NOISE FLOOR",
      subtitle: "Eliminating the 138.4 dB analog SNR accumulation wall",
      description: "Analog optical chips sum light amplitudes, creating catastrophic noise compounding across 128×128 matrices. JANUS encodes residues into discrete waveguide indices. Photons merely indicate a binary 1-bit arrival, bypassing DACs, ADCs, and precision decay.",
      metrics: [
        { label: "Detection Mode", value: "1-Bit Binary" },
        { label: "SNR Requirement", value: "12.8 dB" },
        { label: "ADC Sampling", value: "0 MSps (Receiverless)" },
        { label: "Precision Decay", value: "0.00%" }
      ],
      codeSnippet: `// One-Hot Spatial Residue Decode
for (int i = 0; i < NUM_TILES; i++) {
  residues[i] = input_val % coprime_moduli[i];
  activate_spatial_channel(i, residues[i]);
}`,
      imagePlaceholder: "ONE_HOT_LATTICE"
    },
    {
      id: "hydraulic-shunt",
      title: "Hydraulic Microchannel Lid",
      badge: "3D THERMAL MATRIX",
      subtitle: "Vertical heat isolation protecting sensitive photonics",
      description: "Heterogeneous 3D packaging integrates a 250µm microchannel copper lid directly above the photonic stratum. With R_th,up = 0.227 K/W versus R_th,down = 0.488 K/W, heat generated by the 65nm CMOS logic die is laterally shunted while photonics remain within safe optical tolerances (< 38°C).",
      metrics: [
        { label: "Channel Depth", value: "250 µm" },
        { label: "Thermal Uplink", value: "0.227 K/W" },
        { label: "Photonic Temp ΔT", value: "< 2.1 K" },
        { label: "Fluid Flow Rate", value: "180 mL/min" }
      ],
      codeSnippet: `// Thermal Dissipation Budget
const float R_TH_UP = 0.227;   // K/W upward hydraulic
const float R_TH_DOWN = 0.488; // K/W lateral CMOS shunt
float max_photonic_temp = ambient_c + (p_opt * R_TH_UP);`,
      imagePlaceholder: "HYDRAULIC_SHUT"
    },
    {
      id: "exact-int64",
      title: "3-Equation Hybrid Partitioning",
      badge: "DETERMINISTIC MATH",
      subtitle: "Exact 64-bit precision integer multiplication",
      description: "By decomposing 64-bit operands into (X_L × Y_L) and (X_H × Y_H) optical spatial products with cross-terms computed in deterministic CMOS SRAM LUTs, JANUS guarantees zero analog overflow with absolute mathematical exactness.",
      metrics: [
        { label: "Max Precision", value: "INT64 Exact" },
        { label: "CRT Reconstruct", value: "0 Math Errors" },
        { label: "Tile Gating", value: "Up to 87.5% Power Saved" },
        { label: "Dynamic Allocation", value: "1-16 Optical Tiles" }
      ],
      codeSnippet: `// 3-Equation Hybrid Partitioning
uint64_t P_low  = optical_eval(X_L, Y_L);
uint64_t P_high = optical_eval(X_H, Y_H);
uint64_t P_mid  = cmos_lut_eval(X_L, Y_H, X_H, Y_L);
return (P_high << 64) + (P_mid << 32) + P_low;`,
      imagePlaceholder: "HYBRID_MATH"
    }
  ] as FeatureTab[],

  // 6. Benefits Grid
  benefits: [
    {
      iconType: "laser",
      title: "Deterministic 1-Bit Detection",
      description: "Direct optical triggering of clocked StrongARM latches removes bulky transimpedance amplifiers and high-speed ADCs.",
      metric: "0 ADCs / 0 DACs"
    },
    {
      iconType: "chip",
      title: "Non-Volatile Sb₂S₃ Switches",
      description: "Retains optical routing state indefinitely with zero static power draw, saving >100 kW on large tensor arrays.",
      metric: "0 W Static Draw"
    },
    {
      iconType: "flame",
      title: "Hydraulic Microchannel Co-Design",
      description: "Direct upward convective heat removal prevents thermal detuning of ring resonators and directional couplers.",
      metric: "0.227 K/W R_th"
    },
    {
      iconType: "shield",
      title: "Exact INT64 Mathematical Guarantees",
      description: "Bypasses analog floating-point drift, ensuring bit-exact reproducibility for encryption, scientific modeling, and AI weights.",
      metric: "0-Error CRT"
    },
    {
      iconType: "bolt",
      title: "100 GHz Optical Comb Synchronization",
      description: "Ultra-low jitter 50 fs rms injection-locked oscillator enables picosecond-scale optical matrix multiply operations.",
      metric: "10 ps Gate Time"
    },
    {
      iconType: "binary",
      title: "Dynamic Moduli Power Gating",
      description: "Activates only the minimum required coprime optical tiles for small integers, saving up to 87.5% laser power.",
      metric: "87.5% Power Saved"
    }
  ] as Benefit[],

  // 7. Benchmark Chart
  benchmarks: {
    metric: "COMPUTE DENSITY & EFFICIENCY",
    unit: "Normalized Metric Comparison",
    categories: [
      { name: "Peak Throughput (TMAC/s)", janus6b: 104800, janus1a: 696.3, h100: 3958, mziMesh: 450 },
      { name: "Total Power Dissipation (W)", janus6b: 392, janus1a: 3.35, h100: 700, mziMesh: 120 },
      { name: "Efficiency (TMAC/s/W)", janus6b: 267.3, janus1a: 207.8, h100: 5.65, mziMesh: 3.75 },
      { name: "Static Mesh Power (W)", janus6b: 0, janus1a: 0, h100: 150, mziMesh: 85 }
    ]
  } as BenchmarkData,

  // 8. Testimonials
  testimonials: [
    {
      quote: "The replacement of analog amplitude accumulation with spatial one-hot waveguide routing is the single cleanest paradigm shift in integrated silicon photonics since coherent transceivers.",
      author: "Dr. K. Lindqvist",
      role: "Lead Optical Architecture Reviewer",
      institution: "European Photonics Consortium",
      avatarSeed: "lindqvist"
    },
    {
      quote: "Zero static hold power through Sb₂S₃ PCM micro-heaters completely solves the thermal runaway crisis that has crippled analog Mach-Zehnder matrix multipliers for decades.",
      author: "Prof. S. Tanaka",
      role: "Heterogeneous 3D Integration Chair",
      institution: "Tokyo Microsystems Institute",
      avatarSeed: "tanaka"
    },
    {
      quote: "Achieving exact INT64 precision through 3-equation residue partitioning transforms optical accelerators from niche noisy inference toys into deterministic enterprise compute engines.",
      author: "M. Vance",
      role: "HPC Systems Fellow",
      institution: "Hyperscale Compute Labs",
      avatarSeed: "vance"
    }
  ] as Testimonial[],

  // 9. Use-Case Cards
  useCases: [
    {
      title: "LLM FlashAttention Spatial GEMM",
      category: "Generative AI",
      icon: "🧠",
      description: "Accelerate key-query-value projections in 70B+ parameter models at 100 GHz line rate without quantization accuracy drops.",
      advantage: "Zero precision degradation with INT8/INT16 weights",
      throughputGain: "26× H100 SXM"
    },
    {
      title: "Ultra-Fast Genomic Alignment (Smith-Waterman)",
      category: "Bioinformatics",
      icon: "🧬",
      description: "Direct spatial residue mapping computes pairwise nucleotide matrix dynamic programming cells in picoseconds.",
      advantage: "Deterministic exact alignment score calculation",
      throughputGain: "42× FPGA Accelerators"
    },
    {
      title: "Radar & Synthetic Aperture Imaging",
      category: "Defense & Aerospace",
      icon: "📡",
      description: "Real-time FFT and convolution over multi-gigahertz RF bandwidths directly at the optical antenna feed.",
      advantage: "Extreme thermal resilience via hydraulic microchannels",
      throughputGain: "18× DSP Clusters"
    },
    {
      title: "Homomorphic & Post-Quantum Cryptography",
      category: "Security",
      icon: "🔒",
      description: "Lattice-based polynomial modular multiplication using coprime moduli up to 257 in a single optical pass.",
      advantage: "Side-channel immune spatial one-hot execution",
      throughputGain: "35× Vector CPUs"
    }
  ] as UseCase[],

  // 10. Pricing & Engagement Grid
  pricing: [
    {
      name: "Academic Open Access",
      badge: "CREATIVE COMMONS CC-BY",
      price: "$0",
      period: "perpetual",
      description: "Full open-source access to mathematical treatises, simulation source code, and MEEP/Elmer verification models.",
      features: [
        "39-Page IEEEtran Architecture Treatise (PDF)",
        "Mini 16-Tile Python/Verilog Co-Simulation Suite",
        "MEEP FDTD & Elmer FEM Multi-Physics Datasets",
        "Permanent Zenodo Archive DOI Verification",
        "Community GitHub Discussion & Issues"
      ],
      ctaLabel: "DOWNLOAD SPECIFICATIONS",
      ctaHref: "/JANUS_IEEE_Manuscript.pdf"
    },
    {
      name: "Foundry Tape-Out Partner",
      badge: "MOST POPULAR",
      featured: true,
      price: "$25k",
      period: "per MPW run",
      description: "Access to complete GDSII die floorplans, Sb₂S₃ PCM process design kits (PDK), and DRC-clean mask layouts.",
      features: [
        "Everything in Academic Open Access",
        "Complete GDSII Mask Layout (10.24 mm² die)",
        "AIM Photonics & TSMC 65nm CMOS Interface Specs",
        "Receiverless Ge/Si APD SPICE Netlists",
        "Direct Architecture Consultation (20 Hours)",
        "Dedicated MPW Multi-Project Shuttle Slots"
      ],
      ctaLabel: "REQUEST FOUNDRY KIT",
      ctaHref: "mailto:research@janus-hardware.org?subject=Foundry%20Tape-Out%20Inquiry"
    },
    {
      name: "Hyperscale Enterprise",
      badge: "CUSTOM LICENSING",
      price: "Custom",
      period: "annual",
      description: "Commercial architectural licensing for Model 6B 104.8 PetaMAC/s 3D optical cluster integration into datacenter racks.",
      features: [
        "Full Patent Portfolio & Architecture License",
        "Custom Coprime Moduli Hardware Compiler (JIR)",
        "Rack-Scale Hydraulic Shunt & Chiller Blueprint",
        "On-Site Bring-Up & Photonics Packaging Engineering",
        "Guaranteed Zero-Error INT64 SLA Compliance",
        "24/7 Priority Mission-Critical Engineering Support"
      ],
      ctaLabel: "CONTACT ARCHITECT",
      ctaHref: "mailto:enterprise@janus-hardware.org?subject=Hyperscale%20Model%206B%20Inquiry"
    }
  ] as PricingPlan[],

  // 11. FAQ Items
  faqs: [
    {
      category: "Architecture",
      question: "How does Spatial One-Hot RNS eliminate analog noise accumulation?",
      answer: "Traditional optical AI chips encode numbers in light amplitude and measure accumulated intensity at photodetectors. As matrix size grows to 128x128, distinguishing between millions of discrete power levels demands impossible 21-bit ADCs and is destroyed by thermal drift. JANUS maps numbers to specific waveguide channels (spatial index). Photons only convey a binary 1-bit arrival signal, completely eliminating amplitude decay, drift, and analog SNR accumulation."
    },
    {
      category: "Materials",
      question: "Why Sb₂S₃ phase-change material over VO₂ or GST?",
      answer: "Antimony trisulfide (Sb₂S₃) has a wide bandgap (Eg = 1.72 eV), making it completely transparent at the 1064 nm operating wavelength (photon energy 1.165 eV). It exhibits an extinction coefficient κ ≈ 10⁻⁵ (orders of magnitude lower than GST or GeTe), resulting in minimal insertion loss (0.038 dB) and zero optical attenuation while retaining non-volatile bistability indefinitely without continuous electrical heating."
    },
    {
      category: "Precision",
      question: "Can an optical accelerator genuinely compute exact INT64 integers?",
      answer: "Yes. By utilizing the Chinese Remainder Theorem across coprime moduli (such as 16, 17, 19, ..., 257) alongside our 3-Equation Hybrid Partitioning scheme, 64-bit operands are factored into modular residue channels. Because each channel computes modular arithmetic with absolute spatial determinism, the Chinese Remainder reconstruction yields exact zero-error mathematical integers without floating-point rounding or analog noise."
    },
    {
      category: "Thermal",
      question: "How does the 3D stack prevent CMOS logic heat from detuning the photonics?",
      answer: "A microchannel copper cooler (250 µm depth) is integrated directly on the top surface of the photonic stratum. Due to engineered vertical thermal resistance asymmetry (R_th,up = 0.227 K/W upward to the fluid vs R_th,down = 0.488 K/W downward), photonic heat is drawn immediately into the coolant while the CMOS heat is laterally shunted through a copper heat spreader, keeping the optical stratum within < 2.1 K of ambient."
    },
    {
      category: "Foundry",
      question: "Is Project JANUS compatible with commercial silicon photonics foundries?",
      answer: "Yes. All passive components (MMI splitters, strip waveguides, directional couplers) adhere to standard 220 nm Silicon-on-Insulator (SOI) design rules compatible with AIM Photonics, AMF, and CEA-Leti. The Sb₂S₃ patches are deposited via standard low-temperature sputtering in backend-of-line (BEOL) processing, and the 65 nm CMOS logic die interfaces via micro-copper pillars (< 20 µm pitch)."
    }
  ] as FAQItem[],

  // 12. Final CTA
  finalCta: {
    tag: "ACCELERATE BEYOND THE ANALOG WALL",
    headline: "EXPERIENCE THE NEXT ERA OF DETERMINISTIC OPTICAL COMPUTING",
    subhead: "Explore the complete 39-page architectural treatise, inspect the open-source multi-physics co-simulation datasets, or partner with us for foundry tape-out.",
    primaryButton: { text: "LAUNCH CO-SIMULATION", href: "#features" },
    secondaryButton: { text: "READ TREATISE (IEEEtran)", href: "/JANUS_IEEE_Manuscript.pdf" }
  },

  // 13. Footer
  footer: {
    brandTag: "Project JANUS • Spatial Residue Photonic Hardware",
    copyright: "© 2026 Project JANUS Contributors. Published under Creative Commons CC-BY 4.0 International License.",
    links: [
      {
        title: "RESEARCH TREATISES",
        items: [
          { label: "Architectural Manuscript (PDF)", href: "/JANUS_IEEE_Manuscript.pdf" },
          { label: "Mini 16-Tile Simulation Spec", href: "/JANUS_Mini16_Simulation_Report.pdf" },
          { label: "3D CMOS Stack Architecture", href: "/JANUS_Mini16_CMOS_Architecture.pdf" },
          { label: "Zenodo DOI Archive", href: "https://doi.org/10.5281/zenodo.22733656" }
        ]
      },
      {
        title: "SYSTEM & DATA",
        items: [
          { label: "GitHub Codebase", href: "https://github.com/horizonseekerik/janus-photonic-hardware" },
          { label: "Verilog Golden Audit (Icarus)", href: "https://github.com/horizonseekerik/janus-photonic-hardware/tree/main/janus_mini16_sim" },
          { label: "Multi-Physics MEEP Datasets", href: "https://github.com/horizonseekerik/janus-photonic-hardware" },
          { label: "Robots & Crawler Rules", href: "/robots.txt" },
          { label: "XML Sitemap", href: "/sitemap.xml" }
        ]
      },
      {
        title: "GOVERNANCE & STANDARDS",
        items: [
          { label: "Privacy Policy (Zero PII)", href: "#privacy" },
          { label: "Academic Terms of Use", href: "#terms" },
          { label: "Citation & BibTeX Export", href: "#cite" },
          { label: "Domain Verification Token", href: "/e8b3f12a4d9c4f7b8a1c6e5d2b9f3a7c.txt" }
        ]
      }
    ]
  }
};
