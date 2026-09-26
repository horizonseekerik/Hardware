import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tier1_meep_optics.sb2s3_1x2_switch_cell import Sb2S3_1x2_SwitchCellMeep

print("Initializing Sb2S3 1x2 Switch Cell...")
sw = Sb2S3_1x2_SwitchCellMeep()

print("\n--- Running 2D Meep FDTD: AMORPHOUS STATE ---")
r_am = sw.solve_state_meep("amorphous")
print(f"Amorphous State Result:")
print(f"  Through Transmission (Port 2 Cross): {r_am['transmission_through']*100:.2f}%")
print(f"  Insertion Loss (IL): {r_am['insertion_loss_dB']:.4f} dB")
print(f"  Crosstalk (XT): {r_am['crosstalk_dB']:.2f} dB")
print(f"  Extinction Ratio (ER): {r_am['extinction_ratio_dB']:.2f} dB")

print("\n--- Running 2D Meep FDTD: CRYSTALLINE STATE ---")
r_cr = sw.solve_state_meep("crystalline")
print(f"Crystalline State Result:")
print(f"  Through Transmission (Port 1 Bar): {r_cr['transmission_through']*100:.2f}%")
print(f"  Insertion Loss (IL): {r_cr['insertion_loss_dB']:.4f} dB")
print(f"  Crosstalk (XT): {r_cr['crosstalk_dB']:.2f} dB")
print(f"  Extinction Ratio (ER): {r_cr['extinction_ratio_dB']:.2f} dB")
