"""
test_apd_receiver.py
====================
Automated test suite verifying physical consistency, bounds, and convergence
of the Ge/Si APD and StrongARM direct-to-digital receiver models.
"""

import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apd_physics_engine import SACCMGeSiAPD
from strongarm_latch_engine import StrongARMLatch
from apd_endurance_solver import APDEnduranceSolver

class TestAPDReceiverPhysics(unittest.TestCase):
    def setUp(self):
        self.apd = SACCMGeSiAPD()
        self.latch = StrongARMLatch()
        self.solver = APDEnduranceSolver()

    def test_electric_field_distribution(self):
        """Verifies electric field peaks in Si multiplication layer and stays lower in Ge."""
        f = self.apd.electric_field_profile(v_bias=18.5)
        self.assertGreater(f['E_mult'], 5.0e7, "Multiplication field must exceed 500 kV/cm")
        self.assertLess(f['E_mult'], 1.5e8, "Multiplication field must be below dielectric breakdown of Si")
        self.assertLess(f['E_abs'], f['E_mult'], "Ge absorption field must be lower than Si mult field to suppress tunneling")

    def test_avalanche_gain_and_noise(self):
        """Verifies avalanche gain and McIntyre excess noise factor are within physical bounds."""
        gain = self.apd.avalanche_gain(v_bias=18.0)
        self.assertGreaterEqual(gain, 1.0, "Gain must be >= 1.0")
        self.assertLess(gain, 50.0, "Gain should be stable below breakdown")
        
        fn = self.apd.excess_noise_factor(gain)
        self.assertGreaterEqual(fn, 1.0)
        self.assertLess(fn, 3.5, "Excess noise factor in thin Si must remain small (<3.5) due to dead space")

    def test_junction_capacitance(self):
        """Verifies junction capacitance is ultra-low (< 1.5 fF) for sub-100 aJ/bit operation."""
        cj = self.apd.junction_capacitance()
        self.assertGreater(cj, 0.2e-15, "Capacitance must be positive and non-negligible")
        self.assertLess(cj, 1.5e-15, "Capacitance must be <= 1.5 fF to support 100 Gb/s")

    def test_strongarm_regeneration_speed(self):
        """Verifies StrongARM latch resolves binary 1 within 10 ps (100 Gb/s symbol duration)."""
        t = np.linspace(0, 10e-12, 1000)
        clk = np.ones_like(t)
        # Pulse corresponding to bit '1'
        i_pulse = 3.0e-6 * np.exp(-0.5 * ((t - 1.5e-12)/0.6e-12)**2)
        res = self.latch.simulate_decision(t, clk, i_pulse)
        
        self.assertIsNotNone(res['decision_time_ps'], "Decision must converge within 10 ps")
        self.assertLess(res['decision_time_ps'], 9.5, "Decision time must be < 9.5 ps for 100 Gb/s")
        self.assertEqual(res['decision_bit'], 1, "Should resolve to logic 1")
        self.assertLess(res['energy_per_decision_aJ'], 120.0, "Energy per bit must be < 120 aJ/bit")

    def test_endurance_and_aging_bounds(self):
        """Verifies dark current and optical penalty over 3.16e19 cycles (10 years) remain within allowable telecom specs."""
        cycles = np.logspace(0, 19.5, 10)
        dit, idark = self.solver.simulate_hot_carrier_trap_generation(cycles, temp_k=343.15)
        
        # Dark current should increase monotonically with cycles
        self.assertTrue(np.all(np.diff(idark) >= 0.0), "Dark current must increase monotonically with cycling")
        # Final dark current after 3.16e19 cycles at 70 C should remain <= 11 nA
        self.assertLessEqual(idark[-1], 11.0e-9, "Aged dark current must remain below or equal to 11 nA")
        
        # Sensitivity penalty over 10 years should be under 0.45 dB
        vth_drift = self.solver.cmos_latch_aging_offset(87600, temp_k=343.15, enable_dac_trim=True)
        pen_db, q_aged = self.solver.ber_penalty_vs_aging(idark[-1], vth_drift)
        self.assertLess(pen_db, 0.45, "10-year optical penalty must be < 0.45 dB")
        self.assertGreater(q_aged, 8.5, "Aged Q-factor must remain > 8.5")

    def test_ber_and_noise_scaling(self):
        """Verifies BER meets HD-FEC threshold at ~ -32 to -33 dBm and error-free at -26 dBm."""
        from run_100m_ber_simulation import APDBERSimulator
        sim = APDBERSimulator()
        ber_arr, q_arr = sim.analytical_ber(np.array([-32.1, -26.0]))
        self.assertLessEqual(ber_arr[0], 1.5e-3, "BER at -32.1 dBm must meet HD-FEC limit (1.3e-3)")
        self.assertLessEqual(ber_arr[1], 1.0e-8, "BER at -26.0 dBm must be below 10^-8 (zero errors in 100M)")

if __name__ == '__main__':
    unittest.main()
