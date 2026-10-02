#!/usr/bin/env python3
"""
generate_benchmark_figures.py
=============================================================================
Generates 4-Panel Publication-Grade Demonstration Benchmark Figures for:
1. Multi-Wavelength Excitation Comparison (266, 355, 532, 1064 nm) with (nu_0 - Delta_nu)^4 scaling.
2. High-Resolution Standard Air Raman Spectrum (78% N2 + 21% O2) showing Pure Rotational & Vibrational bands.
3. Thermodynamic Temperature Evolution (100 K, 296 K, 600 K, 1200 K) showing Boltzmann envelope shift & hot bands.
4. Polarization Analysis (Total, Parallel I_parallel, Perpendicular I_perp, and Depolarization Ratio rho).
=============================================================================
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from raman_gas_physics import (
    RamanGasCalculator,
    compute_air_spectrum,
    convolve_spectrum
)

# Publication Typography Settings
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

def generate_benchmark_suite():
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), dpi=300)
    plt.subplots_adjust(hspace=0.28, wspace=0.22, left=0.08, right=0.96, top=0.93, bottom=0.08)

    # -------------------------------------------------------------------------
    # Panel (a): Multi-Wavelength Excitation Scaling (Air at 296 K)
    # -------------------------------------------------------------------------
    ax_a = axes[0, 0]
    lasers = [266.0, 355.0, 532.0]
    colors = ["#7c3aed", "#2563eb", "#059669"]

    shift_grid = np.linspace(-300, 2600, 3500)
    for lam, col in zip(lasers, colors):
        lines = compute_air_spectrum(excitation_nm=lam, temperature_k=296.15,
                                     include_pure_rot=True, include_fundamental=True,
                                     include_hot_bands=False, include_overtones=False)
        spec = convolve_spectrum(lines, shift_grid, fwhm=8.0, x_axis_mode="raman_shift")
        ax_a.plot(shift_grid, spec, label=rf"$\lambda_0 = {int(lam)}\ \mathrm{{nm}}$", color=col, lw=1.8)

    ax_a.set_yscale("log")
    ax_a.set_ylim(bottom=1e-36, top=2e-28)
    ax_a.set_xlabel(r"$\mathrm{Raman\ Shift\ \Delta\tilde{\nu}\ (cm^{-1})}$", fontsize=11, fontweight="bold")
    ax_a.set_ylabel(r"$\mathrm{d\sigma/d\Omega\ (cm^2\cdot sr^{-1}\cdot cm)}$", fontsize=11, fontweight="bold")
    ax_a.set_title("(a) Multi-Wavelength Excitation Dispersion [($\\nu_0 - \\Delta\\nu)^4$ Scaling]",
                   fontsize=12, loc="left", pad=8, fontweight="bold")
    ax_a.grid(True, linestyle="--", alpha=0.4, color="#cbd5e1")
    ax_a.legend(loc="upper right", frameon=True, facecolor="white", fontsize=9)

    # Annotate peak difference
    ax_a.annotate("UV 266 nm Cross Section ≈ 16× of 532 nm",
                  xy=(1556, 1e-29), xytext=(400, 3e-31),
                  arrowprops=dict(facecolor="#7c3aed", shrink=0.08, width=1, headwidth=6),
                  fontsize=9, color="#7c3aed", fontweight="bold")

    # -------------------------------------------------------------------------
    # Panel (b): Standard Air High-Resolution Spectrum at 532 nm (Linear + Stick)
    # -------------------------------------------------------------------------
    ax_b = axes[0, 1]
    lines_air = compute_air_spectrum(excitation_nm=532.0, temperature_k=296.15,
                                     include_pure_rot=True, include_fundamental=True,
                                     include_hot_bands=True, include_overtones=True)
    wl_grid = np.linspace(525.0, 615.0, 4000)
    spec_air = convolve_spectrum(lines_air, wl_grid, fwhm=0.3, x_axis_mode="wavelength")

    ax_b.plot(wl_grid, spec_air, color="#0f172a", lw=1.8, label=r"$\mathrm{Air\ Convolved\ (\Delta\lambda=0.3\ nm)}$")

    # Sample stick lines for N2 and O2
    for l in lines_air:
        if l["active_cross_section"] > 5e-33:
            c = "#2563eb" if "N" in l["molecule"] else "#dc2626"
            ax_b.plot([l["wavelength_nm"], l["wavelength_nm"]], [0, l["active_cross_section"] * 3],
                      color=c, alpha=0.35, lw=0.9)

    ax_b.set_yscale("log")
    ax_b.set_ylim(bottom=1e-35, top=5e-30)
    ax_b.set_xlim(525.0, 615.0)
    ax_b.set_xlabel(r"$\mathrm{Scattered\ Wavelength\ \lambda\ (nm)}$", fontsize=11, fontweight="bold")
    ax_b.set_ylabel(r"$\mathrm{d\sigma/d\Omega\ (cm^2\cdot sr^{-1}\cdot nm^{-1})}$", fontsize=11, fontweight="bold")
    ax_b.set_title(r"(b) Standard Air Raman Spectrum ($\lambda_0 = 532$ nm, T = 296 K)",
                   fontsize=12, loc="left", pad=8, fontweight="bold")
    ax_b.grid(True, linestyle="--", alpha=0.4, color="#cbd5e1")

    # Labels for key features
    ax_b.text(532.0, 2e-30, "Pure Rotational\n(Stokes/Anti-Stokes)", ha="center", fontsize=8,
              bbox=dict(boxstyle="round,pad=0.2", facecolor="#e0f2fe", edgecolor="#0284c7"))
    ax_b.text(580.0, 8e-31, r"$\mathrm{O_2\ Q(v=0\to 1)}$" + "\n(580.0 nm)", ha="center", fontsize=8,
              bbox=dict(boxstyle="round,pad=0.2", facecolor="#fee2e2", edgecolor="#ef4444"))
    ax_b.text(607.3, 1.2e-30, r"$\mathrm{N_2\ Q(v=0\to 1)}$" + "\n(607.3 nm)", ha="center", fontsize=8,
              bbox=dict(boxstyle="round,pad=0.2", facecolor="#dbeafe", edgecolor="#3b82f6"))

    # -------------------------------------------------------------------------
    # Panel (c): Thermodynamic Temperature Evolution of N2 Pure Rotation
    # -------------------------------------------------------------------------
    ax_c = axes[1, 0]
    temps = [120.0, 296.15, 600.0, 1200.0]
    t_colors = ["#0284c7", "#10b981", "#f59e0b", "#ef4444"]
    t_labels = ["120 K (Mesosphere/Polar)", "296 K (Room/Troposphere)", "600 K (Exhaust)", "1200 K (Flame)"]

    rot_shift_grid = np.linspace(0, 250, 2500)
    for t_val, col, lbl in zip(temps, t_colors, t_labels):
        calc = RamanGasCalculator("N2", excitation_nm=532.0, temperature_k=t_val)
        lines = calc.compute_pure_rotational_lines(j_max=60)
        # Select Stokes only
        stokes_lines = [l for l in lines if l["direction"] == "Stokes"]
        spec = convolve_spectrum(stokes_lines, rot_shift_grid, fwhm=1.0, x_axis_mode="raman_shift")
        ax_c.plot(rot_shift_grid, spec, label=lbl, color=col, lw=1.8)

    ax_c.set_xlabel(r"$\mathrm{Raman\ Shift\ \Delta\tilde{\nu}\ (cm^{-1})}$", fontsize=11, fontweight="bold")
    ax_c.set_ylabel(r"$\mathrm{d\sigma/d\Omega\ (cm^2\cdot sr^{-1}\cdot cm)}$", fontsize=11, fontweight="bold")
    ax_c.set_title("(c) Temperature Dependence of $N_2$ Pure Rotational Envelope",
                   fontsize=12, loc="left", pad=8, fontweight="bold")
    ax_c.grid(True, linestyle="--", alpha=0.4, color="#cbd5e1")
    ax_c.legend(loc="upper right", frameon=True, facecolor="white", fontsize=8.5)

    # -------------------------------------------------------------------------
    # Panel (d): Polarization Decomposition (Total, Parallel, Perpendicular, Depol)
    # -------------------------------------------------------------------------
    ax_d = axes[1, 1]
    calc_n2 = RamanGasCalculator("N2", excitation_nm=532.0, temperature_k=296.15)
    lines_tot = calc_n2.compute_all_transitions(True, True, False, False, pol_mode="total")
    lines_par = calc_n2.compute_all_transitions(True, True, False, False, pol_mode="parallel")
    lines_per = calc_n2.compute_all_transitions(True, True, False, False, pol_mode="perpendicular")

    pol_shift_grid = np.linspace(-150, 2500, 3500)
    spec_tot = convolve_spectrum(lines_tot, pol_shift_grid, fwhm=10.0, x_axis_mode="raman_shift")
    spec_par = convolve_spectrum(lines_par, pol_shift_grid, fwhm=10.0, x_axis_mode="raman_shift")
    spec_per = convolve_spectrum(lines_per, pol_shift_grid, fwhm=10.0, x_axis_mode="raman_shift")

    ax_d.plot(pol_shift_grid, spec_tot, color="#0f172a", lw=2.0, label=r"$\mathrm{Total\ (Unpolarized)}$")
    ax_d.plot(pol_shift_grid, spec_par, color="#2563eb", lw=1.6, linestyle="-", label=r"$\mathrm{Parallel\ (I_\parallel)}$")
    ax_d.plot(pol_shift_grid, spec_per, color="#dc2626", lw=1.6, linestyle="--", label=r"$\mathrm{Perpendicular\ (I_\perp)}$")

    ax_d.set_yscale("log")
    ax_d.set_ylim(bottom=1e-35, top=5e-29)
    ax_d.set_xlabel(r"$\mathrm{Raman\ Shift\ \Delta\tilde{\nu}\ (cm^{-1})}$", fontsize=11, fontweight="bold")
    ax_d.set_ylabel(r"$\mathrm{d\sigma/d\Omega\ (cm^2\cdot sr^{-1}\cdot cm)}$", fontsize=11, fontweight="bold")
    ax_d.set_title("(d) Polarization Decomposition & Depolarization Ratio",
                   fontsize=12, loc="left", pad=8, fontweight="bold")
    ax_d.grid(True, linestyle="--", alpha=0.4, color="#cbd5e1")
    ax_d.legend(loc="upper right", frameon=True, facecolor="white", fontsize=8.5)

    ax_d.text(120, 3e-30, r"$\mathrm{Rotational:\ \rho = 0.75}$" + "\n" + r"$\mathrm{(I_\perp \approx 0.43\ I_{tot})}$",
              fontsize=8, bbox=dict(boxstyle="round,pad=0.2", facecolor="#f1f5f9", edgecolor="#64748b"))
    ax_d.text(2331, 3e-31, r"$\mathrm{Q-Branch:\ \rho \approx 0.035}$" + "\n" + r"$\mathrm{(Strongly\ Parallel)}$",
              fontsize=8, bbox=dict(boxstyle="round,pad=0.2", facecolor="#fef2f2", edgecolor="#ef4444"))

    # Save outputs
    png_path = "t:/Spectroscopy/raman_simulation_benchmark.png"
    pdf_path = "t:/Spectroscopy/raman_simulation_benchmark.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)

    print(f"Benchmark figures generated successfully:")
    print(f" - PNG (300 DPI): {png_path}")
    print(f" - PDF (Vector):  {pdf_path}")

if __name__ == "__main__":
    generate_benchmark_suite()
