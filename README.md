# CalculationInLiDAR: Atmospheric Raman Spectroscopy Simulation Suite
## 🔬 大气激光雷达与气体 (N₂ / O₂ / H₂O / Air) 拉曼散射光谱高精度仿真平台

> **Common calculations in atmospheric LiDAR and spectroscopy detection**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Plotly](https://img.shields.io/badge/Plotly.js-Interactive-emerald.svg)](https://plotly.com/javascript/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Bilingual](https://img.shields.io/badge/Language-中文%20%7C%20English-sky.svg)](#)

---

### 📖 Introduction / 项目简介

An advanced, high-precision quantum simulation suite for molecular Raman scattering in atmospheric gases ($\text{N}_2$, $\text{O}_2$, $\text{H}_2\text{O}$, standard dry air, and humid air). Specifically designed for **atmospheric lidar sounding, temperature and water vapor profiling, optical spectrometer calibration, and high-temperature combustion diagnostics**.

本软件是一套面向**激光雷达探测、大气水汽遥感反演、高精度温度/气压廓线测量、燃烧与高温诊断、光谱仪器标定**的高精度拉曼散射微观物理仿真套件。系统严格基于微观量子力学能级结构、玻尔兹曼热力学统计、核自旋宇称对称性、Placzek 极化率理论以及分子碰撞展宽动力学构建。

---

### 🌟 Key Features / 核心特性

1. **Tropospheric Pure Rotational Collisional Broadening (Scheme A Voigt Model)** / **低层大气纯转动碰撞压力展宽修正**
   - Implements $J$-dependent empirical collisional broadening based on Behrendt & Reichardt (2000) and HITRAN parameterizations.
   - Olivero-Longbothum Pseudo-Voigt line synthesis capturing Gaussian instrumental response and Lorentzian skirts ($1/x^2$ decay).
   - Independent on/off toggle and continuous pressure adjustment ($0.00 \sim 2.00\ \text{atm}$).
2. **Double Convolution (Laser Linewidth & Instrument FWHM)** / **发射激光脉冲线型与接收分辨率双重卷积**
   - Convolves both finite laser pulse linewidth ($\text{FWHM}_{\text{laser}}$) and receiver monochromator / interference filter bandwidth ($\text{FWHM}_{\text{inst}}$).
   - Independent switch with single-frequency (0.00 nm), standard Nd:YAG (0.02 nm), and broadband (0.08 nm) presets.
3. **Atmospheric Water Vapor ($\text{H}_2\text{O}$) Modeling** / **完备的水汽物理模型**
   - Incorporates $\nu_1$ symmetric stretch ($3657.05\ \text{cm}^{-1}$) and $\nu_2$ bending mode ($1594.75\ \text{cm}^{-1}$).
   - Ortho-to-para nuclear spin statistical weights ($3:1$).
   - Exact differential cross-sections for water vapor lidar channels ($532 \to 660.5\ \text{nm}$, $355 \to 407.5\ \text{nm}$, $266 \to 294.7\ \text{nm}$).
4. **Dual Platform Ecosystem** / **双平台交互生态**
   - **Interactive Web App (`raman_interactive.html`)**: Zero Python dependency, in-browser real-time quantum calculation engine, offline capable with local `plotly.min.js`.
   - **Native Desktop GUI (`raman_gui.py`)**: Tkinter + Matplotlib, publication-grade high-DPI (300~600 DPI) vector figure export (PNG, PDF, SVG).
5. **Runtime Bilingual Switching** / **中英双语一键无缝切换**
   - Full bilingual interface toggle (`[中文] [English]`) across Web App and Desktop GUI.
   - Dynamic real-time update of all controls, plots, axes, legends, tooltips, and physics theory cards.
6. **100% English Standard CSV Export** / **纯英文数据表导出 (彻底解决乱码)**
   - Unified standard 100% English ASCII headers and field contents with UTF-8 BOM (`\uFEFF`).
   - 100% compatible with Microsoft Excel, WPS Office, Python pandas, R, and MATLAB with zero mojibake.

---

### 🚀 Quick Start / 快速上手

#### Option 1: Standalone Web App (Recommended / 强烈推荐)
Directly double-click [`raman_interactive.html`](file:///t:/Spectroscopy/Raman_Spectroscopy_Software/raman_interactive.html) or run `启动拉曼计算软件_网页交互版.bat`.
- No Python installation required.
- Real-time parameter tuning: wavelength, temperature, pressure, linewidth, polarization, and transitions.

#### Option 2: Native Desktop GUI / 桌面客户端
Run via Python or double-click `启动拉曼计算软件_桌面版.bat`:
```bash
python launch_raman_app.py
# or
python raman_gui.py
```

#### Option 3: Command Line Batch Export / 命令行静默计算导出
```bash
# Export standard Air spectrum at 532 nm to English CSV
python launch_raman_app.py --export --laser 532.0 --temp 296.15 --gas Air
```

---

### 📁 Project Structure / 项目结构

```text
Raman_Spectroscopy_Software/
├── raman_interactive.html        # Core Web App (Standalone offline interactive Plotly app)
├── raman_gui.py                  # Native Windows desktop application (Tkinter + Matplotlib)
├── raman_gas_physics.py          # Core quantum physics & collisional broadening engine
├── raman_interactive_html.py     # HTML generator script
├── launch_raman_app.py           # Unified launcher (GUI / Web / CLI)
├── plotly.min.js                 # Offline Plotly.js library
├── 启动拉曼计算软件_网页交互版.bat   # Windows one-click batch launcher for Web
├── 启动拉曼计算软件_桌面版.bat      # Windows one-click batch launcher for Desktop GUI
├── 拉曼光谱计算软件使用说明书.md      # Detailed technical documentation & user manual
├── 拉曼光谱计算软件_独立审查与评估报告.md # Independent peer review and verification report
├── 拉曼光谱交互仿真软件_分享包.zip    # Portable ready-to-share offline package
├── raman_simulation_benchmark.png# 4-panel publication benchmark figure (PNG 300 DPI)
├── raman_simulation_benchmark.pdf# 4-panel publication benchmark figure (PDF Vector)
└── README.md                     # Project documentation (Bilingual)
```

---

### 📑 Literature References / 理论与文献出处

1. **Behrendt, A., & Reichardt, J. (2000)**. *Atmospheric temperature profiling in the presence of clouds with a pure rotational Raman lidar by use of Butterworth interference filters*. **Applied Optics**, 39(9), 1372-1378. [doi:10.1364/AO.39.001372](https://doi.org/10.1364/AO.39.001372)
2. **Inaba, H., & Kobayasi, T. (1972)**. *Laser-Raman Radar for Air Pollution Measurements*. **Opto-electronics**, 4(2), 101-123. [doi:10.1007/BF01416390](https://doi.org/10.1007/BF01416390)
3. **Avila, G., Fernández, J. M., Tejeda, G., & Montero, S. (1999)**. *The Raman spectra and cross-sections of H2O*. **Journal of Molecular Spectroscopy**, 196(1), 77-92. [doi:10.1006/jmsp.1999.7842](https://doi.org/10.1006/jmsp.1999.7842)
4. **Olivero, J. J., & Longbothum, R. L. (1977)**. *Empirical fits to the Voigt line width: A brief review*. **JQSRT**, 17(2), 233-236. [doi:10.1016/0022-4073(77)90161-3](https://doi.org/10.1016/0022-4073(77)90161-3)
5. **Gordon, I. E., et al. (2022)**. *The HITRAN2020 molecular spectroscopic database*. **JQSRT**, 277, 107949. [doi:10.1016/j.jqsrt.2021.107949](https://doi.org/10.1016/j.jqsrt.2021.107949)

---

### 📄 License / 开源许可

This project is licensed under the MIT License - see the LICENSE file for details.
