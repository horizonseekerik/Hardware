import numpy as np
import meep as mp

def make_true_sbend_polygon(x_start, x_end, y_start, y_end, w, n_pts=20):
    """
    Creates a proper S-bend polygon connecting (x_start, y_start) to (x_end, y_end).
    Centerline: y(x) = y_start + (y_end - y_start) * (3*u^2 - 2*u^3)
    Width: w
    The derivative dy/dx = 0 at both ends, preventing radiation and scattering!
    """
    dx = x_end - x_start
    dy = y_end - y_start
    u_vals = np.linspace(0, 1, n_pts)
    x_vals = x_start + u_vals * dx
    y_vals = y_start + dy * (3 * u_vals**2 - 2 * u_vals**3)
    
    top_edge = [mp.Vector3(x, y + w / 2.0, 0) for x, y in zip(x_vals, y_vals)]
    bot_edge = [mp.Vector3(x, y - w / 2.0, 0) for x, y in reversed(list(zip(x_vals, y_vals)))]
    return top_edge + bot_edge

def make_parabolic_patch_polygon(x_center, y_center, l_patch, w_patch, l_tip=0.60, n_pts=10):
    """Generates an active patch with smooth parabolic entry and exit tips."""
    x_left_tip = x_center - l_patch / 2.0
    x_left_body = x_left_tip + l_tip
    x_right_body = x_center + l_patch / 2.0 - l_tip
    x_right_tip = x_center + l_patch / 2.0
    
    # Left entry parabolic taper: width 0 -> w_patch
    u_left = np.linspace(0, 1, n_pts)
    x_l = x_left_tip + u_left * l_tip
    w_l = w_patch * (2 * u_left - u_left**2)
    
    # Right exit parabolic taper: width w_patch -> 0
    u_right = np.linspace(0, 1, n_pts)
    x_r = x_right_body + u_right * l_tip
    w_r = w_patch * (1.0 - u_right**2)
    
    top_pts = [mp.Vector3(x, y_center + w/2.0, 0) for x, w in zip(x_l, w_l)]
    top_pts += [mp.Vector3(x_right_body, y_center + w_patch/2.0, 0)]
    top_pts += [mp.Vector3(x, y_center + w/2.0, 0) for x, w in zip(x_r, w_r)]
    
    bot_pts = [mp.Vector3(x, y_center - w/2.0, 0) for x, w in reversed(list(zip(x_r, w_r)))]
    bot_pts += [mp.Vector3(x_right_body, y_center - w_patch/2.0, 0)]
    bot_pts += [mp.Vector3(x, y_center - w/2.0, 0) for x, w in reversed(list(zip(x_l, w_l)))]
    
    return top_pts + bot_pts
