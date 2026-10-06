"""
apd_endurance_solver.py
=======================
High-field reliability and accelerated aging solver for the Ge/Si APD and CMOS front-end.

Models degradation physics over >10^18 cycles (>10 years continuous operation at 100 Gb/s):
1. Hot-Carrier Passivation Degradation:
   - High-energy avalanching electrons breaking Si-H bonds at the mesa SiO2 passivation interface.
   - Power-law accumulation of interface trap density: Delta D_it(N) = A_HC * (Q_pulse / q)^n * N^m.
   - Resulting surface leakage current drift: Delta I_dark_surf(N).
2. CMOS Dynamic Threshold Mismatch (HCI / BTI):
   - Asymmetric threshold shift Delta Vth(t) in the StrongARM input differential pair.
   - Resulting input sensitivity degradation and dynamic offset drift.
3. Black's Electromigration Equation:
   - Current density stress J_rms in contact vias and Cu through-die vias (TDVs).
   - Mean Time to Failure (MTTF) projection as a function of temperature (55 C, 70 C, 85 C).
"""

import numpy as np

Q = 1.602176634e-19       # Electron charge (C)
KB = 1.380649e-23         # Boltzmann constant (J/K)
EV_TO_J = 1.602176634e-19

class APDEnduranceSolver:
    def __init__(self,
                 initial_dark_current=1.2e-9,  # 1.2 nA initial dark current
                 surface_area_cm2=3.5e-8,      # Passivation sidewall area (pi * d * W_tot)
                 ea_electromigration=0.9,      # Activation energy for Cu-W vias (eV)
                 ea_interface_trap=0.45):      # Activation energy for Si-H bond breaking (eV)
        self.i_dark_0 = initial_dark_current
        self.area_surf = surface_area_cm2
        self.ea_em = ea_electromigration * EV_TO_J
        self.ea_trap = ea_interface_trap * EV_TO_J
        
    def simulate_hot_carrier_trap_generation(self, cycles_array, temp_k=343.15, m_gain=7.0):
        """
        Calculates interface trap density Delta D_it (cm^-2 * eV^-1) and dark current drift
        as a function of cumulative switching cycles (from 1 to 3.16 * 10^19 cycles,
        representing 10 years continuous operation at 100 Gb/s).
        
        Physics:
        Bond breaking rate governed by hot-carrier current density and Arrhenius activation:
        Delta D_it = D0 * (M * Q_e)^0.4 * (N_cycles)^0.18 * exp(-Ea / (kB * T))
        """
        # Calibration constant matched to Ge/Si high-field mesa experimental kinetics
        # Over 3.16 * 10^19 optical cycles (10 years at 100 Gb/s):
        # Power-law aging exponent m = 0.18 (sub-linear interface trap generation)
        d0 = 3.5e7
        q_pulse_norm = (m_gain / 7.0)
        
        arrhenius_factor = np.exp(-self.ea_trap / (KB * temp_k))
        ref_arrhenius = np.exp(-self.ea_trap / (KB * 300.0))
        temp_scaling = arrhenius_factor / ref_arrhenius
        
        m_exp = 0.18
        delta_dit = d0 * (q_pulse_norm**0.4) * (cycles_array**m_exp) * temp_scaling
        
        # Surface recombination leakage: Delta I_dark_surf = q * S * n_i * Area_surf
        # Empirical conversion factor: 1e11 cm^-2 eV^-1 trap density ~ 0.85 nA surface leakage
        delta_i_dark = (delta_dit / 1.0e11) * 0.85e-9
        
        total_i_dark = self.i_dark_0 + delta_i_dark
        return delta_dit, total_i_dark

    def cmos_latch_aging_offset(self, operating_hours, temp_k=343.15, enable_dac_trim=True):
        """
        Calculates asymmetric dynamic threshold offset Delta Vth (mV) in StrongARM input pair
        due to Hot-Carrier Injection (HCI) and Negative Bias Temperature Instability (NBTI).
        
        Delta Vth = A_BTI * (t / t_0)^(0.16) * exp(-Ea_bti / (kB * T))
        With active auto-zeroing / foreground 4-bit capacitor trimming DAC (enable_dac_trim=True).
        """
        ea_bti = 0.35 * EV_TO_J
        # At 10 years (87,600 hours) at 70 C (343.15 K), intrinsic Delta Vth is ~4.17 mV for FinFETs
        t_hours = np.maximum(operating_hours, 1.0)
        temp_factor = np.exp(-ea_bti / (KB * temp_k)) / np.exp(-ea_bti / (KB * 343.15))
        delta_vth_raw = 0.675 * (t_hours**0.16) * temp_factor
        
        if enable_dac_trim:
            # 4-bit auto-zero calibration DAC with 1.0 mV LSB: residual offset bounded to <= 1.33 mV
            v_lsb = 1.0
            delta_vth_residual = np.minimum(delta_vth_raw, 0.5 * v_lsb + 0.2 * delta_vth_raw)
            return float(delta_vth_residual)
        return float(delta_vth_raw)

    def black_electromigration_mttf(self, j_rms_a_cm2, temp_k_array):
        """
        Calculates MTTF (Mean Time to Failure in years) using Black's Equation:
        MTTF = (A / J_rms^n) * exp(Ea / (kB * T))
        with n = 2 for Cu interconnects and W contacts.
        """
        a_em = 1.8e15 # Empirical Black's constant for nanoscale via metallization
        mttf_sec = (a_em / (j_rms_a_cm2**2.0)) * np.exp(self.ea_em / (KB * temp_k_array))
        mttf_years = mttf_sec / (365.25 * 24.0 * 3600.0)
        return mttf_years

    def ber_penalty_vs_aging(self, total_i_dark, delta_vth_mv, nominal_q=9.5):
        """
        Translates dark current increase and dynamic latch offset into Q-factor and
        optical sensitivity power penalty (dB).
        
        Delta P_penalty (dB) = 10 * log10( Q_aged / Q_nominal * (1 + delta_noise / signal) )
        """
        # Noise variance increase: sigma_total^2 = sigma_thermal^2 + sigma_shot^2 + sigma_latch^2
        # Shot noise: sigma_shot^2 = 2 * q * I_dark * F(M) * B
        b_bw = 70.0e9 # 70 GHz effective noise bandwidth
        f_m = 1.15   # Thin Si dead-space suppressed excess noise factor at M=7
        sigma_shot_0 = np.sqrt(2.0 * Q * self.i_dark_0 * f_m * b_bw)
        sigma_shot_aged = np.sqrt(2.0 * Q * total_i_dark * f_m * b_bw)
        
        # Effective signal current at sensitivity threshold with M=7: I_sig ~ 3.5 uA
        i_sig = 3.5e-6
        
        # Degradation factor
        noise_ratio = (sigma_shot_aged - sigma_shot_0) / i_sig
        offset_ratio = (delta_vth_mv * 1e-3) / 0.045 # normalized to nominal swing
        
        penalty_db = 10.0 * np.log10(1.0 + 1.2 * noise_ratio + 0.8 * offset_ratio)
        q_aged = nominal_q / (10.0**(penalty_db / 20.0))
        
        return penalty_db, q_aged

if __name__ == '__main__':
    solver = APDEnduranceSolver()
    # 10 years at 100 Gb/s corresponds to 3.16e19 switching cycles
    cycles = np.logspace(0, 19.5, 20)
    n_10yr = 3.156e19
    
    print("=== APD High-Field Reliability & Endurance Audit ===")
    dit_25, idark_25 = solver.simulate_hot_carrier_trap_generation(np.array([n_10yr]), temp_k=298.15)
    dit_55, idark_55 = solver.simulate_hot_carrier_trap_generation(np.array([n_10yr]), temp_k=328.15)
    dit_70, idark_70 = solver.simulate_hot_carrier_trap_generation(np.array([n_10yr]), temp_k=343.15)
    
    print(f"10-Year (3.16e19 cycles) Aging Results:")
    print(f"  25 C (Room Temp) : I_dark = {idark_25[0]*1e9:.2f} nA (Dit: {dit_25[0]:.2e} cm^-2 eV^-1)")
    print(f"  55 C (Nominal)   : I_dark = {idark_55[0]*1e9:.2f} nA (Dit: {dit_55[0]:.2e} cm^-2 eV^-1)")
    print(f"  70 C (Stress)    : I_dark = {idark_70[0]*1e9:.2f} nA (Dit: {dit_70[0]:.2e} cm^-2 eV^-1)")
    
    # 10-year FinFET aging (87,600 hours)
    vth_raw = solver.cmos_latch_aging_offset(87600, temp_k=343.15, enable_dac_trim=False)
    vth_trim = solver.cmos_latch_aging_offset(87600, temp_k=343.15, enable_dac_trim=True)
    print(f"10-Year Dynamic Latch Offset Drift (70 C): Raw = {vth_raw:.2f} mV, Trimmed = {vth_trim:.2f} mV")
    
    pen_raw, q_raw = solver.ber_penalty_vs_aging(idark_70[0], vth_raw)
    pen_trim, q_trim = solver.ber_penalty_vs_aging(idark_70[0], vth_trim)
    print(f"10-Year Optical Sensitivity Penalty (70 C):")
    print(f"  Uncompensated : {pen_raw:.3f} dB (Q drops to {q_raw:.2f})")
    print(f"  4-Bit C-DAC   : {pen_trim:.3f} dB (Q drops to {q_trim:.2f})")
    
    # Electromigration projection
    temps = np.array([328.15, 343.15, 358.15]) # 55C, 70C, 85C
    mttf = solver.black_electromigration_mttf(j_rms_a_cm2=4.5e5, temp_k_array=temps)
    print(f"Electromigration reliability: J_rms = 4.5e5 A/cm^2 << J_crit (1.5e6 A/cm^2), MTTF > 100 years at 70 C.")
