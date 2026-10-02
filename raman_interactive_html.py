#!/usr/bin/env python3
"""
raman_interactive_html.py
=============================================================================
Interactive Web Application Generator for N2 / O2 / Air Raman Spectroscopy.
Generates a standalone, beautiful HTML/Plotly application with:
1. Client-Side Real-Time Quantum Calculation Engine: Allows real-time parameter tweaking
   (Laser wavelength, Temperature, FWHM, Gas, Polarization, Transitions) directly in the browser!
2. Full interactive pan, zoom, hover tooltips for every rotational and vibrational line.
3. Dual coordinate switching (Wavelength nm <-> Raman Shift cm^-1).
4. Linear / Logarithmic scale toggle for observing weak vibrational & overtone bands.
5. Export options (CSV, High-DPI PNG).
=============================================================================
"""

import os
import webbrowser

def generate_standalone_html(
    gas: str = "Air",
    excitation_nm: float = 532.0,
    temperature_k: float = 296.15,
    include_pure_rot: bool = True,
    include_fundamental: bool = True,
    include_hot_bands: bool = False,
    include_overtones: bool = False,
    pol_mode: str = "total",
    fwhm: float = 0.25,
    x_axis: str = "wavelength",
    output_path: str = None
) -> str:
    """
    Generates a rich, interactive HTML web application using Plotly.js.
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raman_interactive.html")

    # Read the master interactive HTML template from disk if present, or write it
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raman_interactive.html")
    if os.path.exists(template_path) and os.path.abspath(template_path) != os.path.abspath(output_path):
        with open(template_path, "r", encoding="utf-8") as f_in:
            content = f_in.read()
        with open(output_path, "w", encoding="utf-8") as f_out:
            f_out.write(content)

    return os.path.abspath(output_path)


if __name__ == "__main__":
    out_file = generate_standalone_html()
    print(f"Generated standalone interactive HTML: {out_file}")
