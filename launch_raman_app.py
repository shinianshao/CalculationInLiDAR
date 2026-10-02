#!/usr/bin/env python3
"""
launch_raman_app.py
=============================================================================
Unified Launcher for N2 / O2 / Air Raman Scattering Simulation Suite.

Usage:
  python launch_raman_app.py           # Launch Desktop GUI (Default)
  python launch_raman_app.py --web     # Directly open Interactive Web App in browser
  python launch_raman_app.py --export  # Compute and export default Air spectrum to CSV & PNG
=============================================================================
"""

import sys
import argparse
import webbrowser
import os
from raman_interactive_html import generate_standalone_html
from raman_gas_physics import compute_air_spectrum

def main():
    parser = argparse.ArgumentParser(description="氮气/氧气/水汽/空气拉曼散射高精度仿真软件")
    parser.add_argument("--web", action="store_true", help="直接在浏览器中打开现代化交互式 Web App")
    parser.add_argument("--export", action="store_true", help="后台静默计算并导出标准空气数据表与高清图表")
    parser.add_argument("--laser", type=float, default=532.0, help="激发激光波长 (nm)")
    parser.add_argument("--temp", type=float, default=296.15, help="气体温度 (K)")
    parser.add_argument("--gas", type=str, default="Air", choices=["Air", "HumidAir", "H2O", "N2", "O2", "All"], help="气体选择")
    args = parser.parse_args()

    if args.web:
        print(f"正在生成 {args.gas} 交互式 Web 网页版 (λ₀ = {args.laser} nm, T = {args.temp} K)...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        html_file = os.path.join(script_dir, "raman_interactive.html")
        generate_standalone_html(
            gas=args.gas,
            excitation_nm=args.laser,
            temperature_k=args.temp,
            include_pure_rot=True,
            include_fundamental=True,
            include_hot_bands=True,
            include_overtones=True,
            output_path=html_file
        )
        print(f"正在调用默认浏览器打开: {html_file}")
        webbrowser.open(f"file:///{html_file}")
        return

    if args.export:
        print("正在进行标准空气拉曼全谱计算与导出...")
        import matplotlib.pyplot as plt
        import numpy as np
        from raman_gas_physics import convolve_spectrum

        lines = compute_air_spectrum(args.laser, args.temp, True, True, True, True)
        csv_file = f"raman_air_{args.laser}nm.csv"
        with open(csv_file, "w", encoding="utf-8-sig") as f:
            f.write("Molecule,Transition_Type,Branch,Direction,v_lower,J_lower,v_upper,J_upper,Wavelength_nm,Raman_Shift_cm-1,Diff_Cross_Section_cm2_sr,Active_Cross_Section_cm2_sr,Depolarization_Ratio_rho,Collisional_FWHM_cm-1,Collisional_FWHM_nm,Transition_Label\n")
            for l in lines:
                mol_ascii = l['molecule'].replace("₂", "2")
                label_ascii = l['transition_label'].replace("₂", "2").replace("ν", "nu").replace("₁", "1")
                type_ascii = l['type'].replace("ν", "nu").replace("₁", "1").replace("₂", "2")
                c_cm = l.get('fwhm_coll_cm', 0.0)
                c_nm = l.get('fwhm_coll_nm', 0.0)
                f.write(f"{mol_ascii},{type_ascii},{l['branch']},{l.get('direction', 'Stokes')},"
                        f"{l['v_lower']},{l['J_lower']},{l['v_upper']},{l['J_upper']},"
                        f"{l['wavelength_nm']:.5f},{l['raman_shift_cm']:.3f},"
                        f"{l['cross_section_cm2_sr']:.5e},{l.get('active_cross_section', l['cross_section_cm2_sr']):.5e},"
                        f"{l.get('depol_ratio', 0.75):.4f},{c_cm:.4f},{c_nm:.6f},{label_ascii}\n")
        print(f"数据已导出: {csv_file}")
        return

    # Default: Launch Tkinter Desktop Application
    print("正在启动原生桌面 GUI 程序...")
    import raman_gui
    raman_gui.main()

if __name__ == "__main__":
    main()
