"""
strongarm_latch_engine.py
=========================
Non-linear dynamic state-space ODE engine for the Clocked StrongARM Regenerative Latch.

Models the direct-to-digital photodetector front-end without an analog linear TIA:
1. Phase 1: Reset / Precharge phase (CLK = 0, internal sensing nodes & outputs precharged to VDD).
2. Phase 2: Dynamic Sampling & Integration (CLK rises, M_tail turns ON, photodiode charge integrates onto C_p).
3. Phase 3: Non-linear Positive Feedback Regeneration (cross-coupled inverter pair snaps to rail-to-rail digital logic).

Key Metrics:
- Regeneration time constant tau_regen = C_L / g_m ~ 1.5 - 3.5 ps.
- Total decision time t_decision (< 9.0 ps at 100 Gb/s).
- Dynamic decision energy E_decision = C_total * VDD^2 (< 100 aJ/bit, 0 W static power).
- Dynamic input offset voltage (due to transistor mismatch & hot-carrier aging).
"""

import numpy as np
from scipy.integrate import solve_ivp

# Technology Node Parameters: Advanced Sub-10nm FinFET / Monolithic 3D Heterogeneous Node
VDD = 0.75                # Supply voltage (0.75 V)
C_P = 75e-18              # Sensing node parasitic capacitance (75 aF)
C_L = 85e-18              # Internal regenerative output load capacitance (85 aF)
G_M = 0.35e-3             # Effective regenerative transconductance (0.35 mS)
T_INT = 3.0e-12           # Integration window (3.0 ps)
T_SETUP = 0.6e-12         # Setup/latch guard band (0.6 ps)

class StrongARMLatch:
    """
    Clocked StrongARM Regenerative Sense Amplifier / Direct-to-Digital Receiver.
    """
    def __init__(self,
                 vdd=VDD,
                 c_p=C_P,
                 c_l=C_L,
                 g_m=G_M,
                 t_int=T_INT,
                 t_setup=T_SETUP,
                 offset_voltage=0.0):
        self.vdd = vdd
        self.c_p = c_p
        self.c_l = c_l
        self.g_m = g_m
        self.t_int = t_int
        self.t_setup = t_setup
        self.offset_voltage = offset_voltage  # Dynamic threshold mismatch (V)
        self.tau_regen = self.c_l / self.g_m  # Regeneration time constant (~0.24 ps)
        
    def simulate_decision(self, t_span, clk_signal, i_photo, c_apd=0.8e-15, v_ref_bias=0.0):
        """
        Simulates the time-domain trajectory of the StrongARM latch.
        
        1. Integration phase:
           Integrates incoming photocurrent i_photo(t) over t_int into differential voltage:
           Delta_V_init = (Q_photo / C_total) + V_offset
        2. Non-linear cross-coupled ODE regeneration:
           C_L * d(Delta_V)/dt = g_m * Delta_V * [1 - (Delta_V / V_dd)^2]
        """
        dt = t_span[1] - t_span[0]
        n_steps = len(t_span)
        
        # Effective total input capacitance including APD mesa
        c_in_tot = self.c_p + c_apd
        
        # Integrate photocurrent during active integration window
        q_photo = np.sum(i_photo) * dt
        v_diff_init = (q_photo / c_in_tot) - self.offset_voltage
        
        # Bound initial offset for numerical stability
        sign = 1.0 if v_diff_init >= 0 else -1.0
        v_init_clamped = sign * max(abs(v_diff_init), 1e-5)
        v_init_clamped = sign * min(abs(v_init_clamped), 0.45 * self.vdd)
        
        # Regeneration ODE
        def regen_ode(t, y):
            v_d = y[0]
            sat_factor = max(0.0, 1.0 - (abs(v_d) / self.vdd)**2)
            return [(self.g_m / self.c_l) * v_d * sat_factor]
            
        t_max_regen = 8.0 * self.tau_regen
        sol = solve_ivp(regen_ode, [0, t_max_regen], [v_init_clamped],
                        method='RK45', max_step=0.05 * self.tau_regen)
        
        # Find 90% rail decision time
        v_thresh = 0.90 * self.vdd
        idx_decision = np.where(np.abs(sol.y[0]) >= v_thresh)[0]
        if len(idx_decision) > 0:
            t_regeneration = float(sol.t[idx_decision[0]])
        else:
            t_regeneration = float(self.tau_regen * np.log(v_thresh / abs(v_init_clamped)))
            
        t_decision_total = self.t_int + t_regeneration + self.t_setup
        decision_bit = 1 if v_diff_init > 0 else 0
        
        # Direct-to-Digital dynamic switching energy:
        # In a clocked latch with zero static bias (I_bias = 0), energy is purely dynamic:
        # E_core = (C_p + C_l) * V_dd^2 + Q_photo * V_dd = (160 aF)(0.75 V)^2 + (6.3 aC)(0.75 V) = 94.73 aJ/bit
        e_dyn = (self.c_p + self.c_l) * (self.vdd**2)
        e_opt_coupling = q_photo * self.vdd
        core_energy_aj = float((e_dyn + e_opt_coupling) * 1e18)
        
        # Total receiver energy budget:
        # E_clk: Clock buffer driving tail switch (~40 aF) = 22.5 aJ/bit
        # E_dark: APD dark current energy at 100 Gb/s (18.2 V * 6.74 nA / 100 Gb/s) = 1.23 aJ/bit
        e_clk_aj = 40e-18 * (self.vdd**2) * 1e18
        e_dark_aj = (18.2 * 6.74e-9 / 100e9) * 1e18
        total_rx_energy_aj = core_energy_aj + e_clk_aj + e_dark_aj
        
        # Build smooth output trajectories for plotting / visualization
        v_out_p = np.full(n_steps, self.vdd)
        v_out_n = np.full(n_steps, self.vdd)
        
        # Transition occurs after t_int
        idx_start_regen = int(self.t_int / dt)
        if idx_start_regen < n_steps:
            t_eval = t_span[idx_start_regen:] - self.t_int
            v_traj = np.interp(t_eval, sol.t, sol.y[0])
            if decision_bit == 1:
                v_out_p[idx_start_regen:] = np.clip(self.vdd - 0.5 * (self.vdd + v_traj), 0.0, self.vdd)
                v_out_n[idx_start_regen:] = self.vdd
            else:
                v_out_p[idx_start_regen:] = self.vdd
                v_out_n[idx_start_regen:] = np.clip(self.vdd - 0.5 * (self.vdd - v_traj), 0.0, self.vdd)
                
        return {
            'time': t_span,
            'v_out_p': v_out_p,
            'v_out_n': v_out_n,
            'decision_time_ps': float(t_decision_total * 1e12),
            't_regen_ps': float(t_regeneration * 1e12),
            'decision_bit': decision_bit,
            'energy_per_decision_aJ': core_energy_aj,
            'total_receiver_energy_aJ': total_rx_energy_aj,
            'v_diff_init_mV': float(v_diff_init * 1e3)
        }

if __name__ == '__main__':
    latch = StrongARMLatch()
    t = np.linspace(0, 10e-12, 1000)
    clk = np.ones_like(t)
    sigma = 0.6e-12
    # Pulse producing exactly 6.30 aC integrated photocharge
    q_target = 6.30e-18
    i_peak = q_target / (sigma * np.sqrt(2 * np.pi))
    i_photo = i_peak * np.exp(-0.5 * ((t - 1.5e-12) / sigma)**2)
    
    res = latch.simulate_decision(t, clk, i_photo, c_apd=0.486e-15)
    print("=== Clocked StrongARM Direct-to-Digital Audit ===")
    print(f"Integrated Photocharge : {q_target*1e18:.2f} aC")
    print(f"Initial Delta V0       : {res['v_diff_init_mV']:.2f} mV")
    print(f"Regeneration Time      : {res['t_regen_ps']:.2f} ps")
    print(f"Total Decision Time    : {res['decision_time_ps']:.2f} ps")
    print(f"Resolved Bit           : {res['decision_bit']}")
    print(f"Core Decision Energy   : {res['energy_per_decision_aJ']:.2f} aJ/bit")
    print(f"Total Receiver Energy  : {res['total_receiver_energy_aJ']:.2f} aJ/bit")

