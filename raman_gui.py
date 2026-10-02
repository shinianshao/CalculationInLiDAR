#!/usr/bin/env python3
"""
raman_gui.py
=============================================================================
Native Windows Desktop Application for N2 / O2 / H2O / Air Raman Scattering Simulation.
Built with Tkinter and Matplotlib.

Features:
- Bilingual UI (Chinese / English 双语一键切换).
- 100% English ASCII CSV Export with UTF-8 BOM to prevent Excel mojibake.
- Arbitrary Excitation Wavelength with Quick Presets (266, 355, 532, 632.8, 785, 1064 nm).
- Temperature Adjustable (100 K - 1500 K) with Boltzmann Rovibrational Populations.
- Gas Selection: N2, O2, H2O, Standard Air, Humid Air, or All Comparison.
- Transition Selectors: Pure Rotational (S/O), Fundamental (v=0->1), Hot Bands (v=1->2), Overtones (v=0->2).
- Low-Atmosphere Pure Rotational Collisional Pressure Broadening (Scheme A Voigt model).
- Laser Linewidth & Receiver Resolution Double Convolution.
- Polarization Modes: Total, Parallel (I_parallel), Perpendicular (I_perp), Depolarization Ratio (rho).
- Dual Axes (Wavelength nm <-> Raman Shift cm^-1) & Scale (Linear / Log10).
- High-DPI Publication Figure Export (PNG/PDF/SVG).
=============================================================================
"""

import sys
import os
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Import Physics Engine & Web Generator
from raman_gas_physics import (
    RamanGasCalculator,
    compute_air_spectrum,
    convolve_spectrum,
    compute_effective_fwhm,
    compute_collisional_broadening_hwhm,
    MOLECULAR_DATA
)
from raman_interactive_html import generate_standalone_html

# Publication-Grade Styling Config
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Segoe UI', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'cm'

# Bilingual Dictionary for Desktop Application
GUI_I18N = {
    "zh": {
        "window_title": "🔬 氮气/氧气/水汽/空气拉曼散射光谱与截面高精度仿真软件 (双模专业版)",
        "header_title": "N₂ / O₂ / H₂O / Air 拉曼散射截面与波长高精度计算仿真平台",
        "header_sub": "量子微观能级 · 核自旋统计 · Placzek色散定律 · 温度玻尔兹曼布居 · 偏振退偏比",
        "grp_gas": "1. 目标气体分子 (Target Gas)",
        "gas_air": "标准干空气 (Dry Air: 78% N₂ + 21% O₂)",
        "gas_humid": "含湿空气 (Humid Air: 1% H₂O 水汽)",
        "gas_h2o": "水汽 (H₂O 纯气体)",
        "gas_n2": "氮气 (N₂ 纯气体)",
        "gas_o2": "氧气 (O₂ 纯气体)",
        "gas_all": "全组分对比 (N₂, O₂, H₂O 同时绘制)",
        "grp_laser": "2. 激发激光波长 (Excitation λ₀)",
        "lbl_laser": "波长 λ₀ (nm):",
        "grp_temp": "3. 气体温度 (Temperature T)",
        "lbl_temp": "绝对温度 (K):",
        "temp_presets": ["高空 220K", "常温 296K", "中温 600K", "火焰 1200K"],
        "grp_press": "3.5 环境压强与碰撞展宽 (Pressure & Broadening)",
        "chk_press": "启用低层大气纯转动碰撞压力展宽",
        "lbl_press": "环境气压 P (atm):",
        "press_presets": ["真空 0.00", "高空 0.25", "常压 1.00", "增压 1.50"],
        "press_status_off": "纯转动线型: 理想无碰撞基准 (未开启)",
        "press_status_on": "碰撞半宽: {fwhm_cm:.3f} cm⁻¹ ({fwhm_nm_pm:.1f} pm @N₂ S6)",
        "grp_trans": "4. 跃迁阶数与分支 (Transitions)",
        "chk_pure_rot": "纯转动拉曼 (Pure Rotational S/O支)",
        "chk_fund": "基频振动-转动 (v=0→1, Q/O/S支)",
        "chk_hot": "热带跃迁 (Hot Bands v=1→2)",
        "chk_over": "泛频跃迁 (Overtones v=0→2)",
        "grp_pol": "5. 偏振特性通道 (Polarization)",
        "pol_total": "总非偏振截面 (Total)",
        "pol_par": "平行偏振分量 (Parallel I_∥)",
        "pol_perp": "垂直偏振分量 (Perpendicular I_⊥)",
        "pol_depol": "退偏振比 (Depol. Ratio ρ)",
        "grp_inst": "6. 光学分辨率与激光谱宽 (Optics & Laser)",
        "lbl_fwhm": "接收分辨率/滤光片半宽:",
        "chk_laser_lw": "启用发射激光谱宽双重卷积",
        "lbl_laser_lw": "激光谱宽 FWHM (nm):",
        "lw_presets": ["单频 0.00", "常规YAG 0.02", "宽带 0.08"],
        "eff_fwhm_conv": "合成等效半宽: {eff:.3f} nm{cm_note} (双重卷积)",
        "eff_fwhm_single": "合成等效半宽: {inst:.3f} nm{cm_note} (单频基准)",
        "lbl_prof": "仪器线形函数:",
        "grp_disp": "7. 坐标系与呈现形式 (Display)",
        "lbl_x": "横坐标:",
        "x_wl": "波长 (nm)",
        "x_shift": "位移 (cm⁻¹)",
        "lbl_y": "纵坐标:",
        "y_lin": "线性",
        "y_log": "对数 Log10",
        "lbl_style": "样式:",
        "style_cont": "连续谱",
        "style_stick": "线谱",
        "style_both": "两者",
        "btn_calc": "⚡ 重新计算与刷新",
        "btn_web": "🌐 在浏览器打开交互式图表 (Plotly)",
        "btn_csv": "💾 导出数据表 CSV (英文格式)",
        "btn_fig": "📷 保存高清图片",
        "status_ready": "就绪",
        "status_done": "✅ 计算完成 | 跃迁总数: {count} 条 | 最强峰: {strongest} (λ = {wl:.3f} nm, Δν = {shift:.2f} cm⁻¹, 截面 = {cross:.3e} cm²/sr) | 总积分散射截面: {tot:.3e} cm²/sr",
        "err_input_title": "输入错误",
        "err_input_msg": "参数输入格式有误，请输入合法数值。\n{err}",
        "warn_trans_title": "提示",
        "warn_trans_msg": "请至少勾选一种跃迁类型（纯转动、基频、热带或泛频）。",
        "warn_no_data_title": "提示",
        "warn_no_data_msg": "当前无有效数据。",
        "export_csv_title": "导出成功",
        "export_csv_msg": "跃迁数据明细表 (全英文格式) 已成功导出至：\n{path}",
        "export_csv_err_title": "导出错误",
        "export_fig_title": "保存成功",
        "export_fig_msg": "高质量图表已保存至：\n{path}",
        "export_fig_err_title": "保存错误",
        "legend_n2_cont": "N₂ 连续谱",
        "legend_o2_cont": "O₂ 连续谱",
        "legend_h2o_cont": "H₂O 连续谱",
        "legend_conv": "{gas} 卷积谱 ({tag})",
        "plot_title": r"{gas} 拉曼散射光谱仿真 ($\lambda_0$ = {wl:.1f} nm, T = {temp:.1f} K, 偏振: {pol})"
    },
    "en": {
        "window_title": "🔬 N₂ / O₂ / H₂O / Air Raman Scattering Simulation Suite (Dual-Mode Pro)",
        "header_title": "N₂ / O₂ / H₂O / Air Raman Cross Section & Spectrum Simulation Platform",
        "header_sub": "Quantum Rovibrational Levels · Nuclear Spin Statistics · Placzek Dispersion · Boltzmann Population · Polarization",
        "grp_gas": "1. Target Gas Molecule",
        "gas_air": "Standard Dry Air (78% N₂ + 21% O₂)",
        "gas_humid": "Humid Air (1% H₂O Water Vapor)",
        "gas_h2o": "Water Vapor (Pure H₂O)",
        "gas_n2": "Nitrogen (Pure N₂)",
        "gas_o2": "Oxygen (Pure O₂)",
        "gas_all": "All Components (N₂, O₂, H₂O Comparison)",
        "grp_laser": "2. Excitation Wavelength (λ₀)",
        "lbl_laser": "Wavelength λ₀ (nm):",
        "grp_temp": "3. Gas Temperature (T)",
        "lbl_temp": "Absolute Temp (K):",
        "temp_presets": ["High Alt. 220K", "Room 296K", "Exhaust 600K", "Flame 1200K"],
        "grp_press": "3.5 Pressure & Broadening",
        "chk_press": "Enable Tropospheric Collisional Broadening",
        "lbl_press": "Ambient Pressure P (atm):",
        "press_presets": ["Vacuum 0.00", "High Alt. 0.25", "Std. 1.00", "Boost 1.50"],
        "press_status_off": "Pure Rotational: Collisionless Baseline (Disabled)",
        "press_status_on": "Collisional FWHM: {fwhm_cm:.3f} cm⁻¹ ({fwhm_nm_pm:.1f} pm @N₂ S6)",
        "grp_trans": "4. Transitions & Branches",
        "chk_pure_rot": "Pure Rotational (S & O Branches)",
        "chk_fund": "Fundamental Rovibrational (v=0→1, Q/O/S)",
        "chk_hot": "Hot Bands (v=1→2)",
        "chk_over": "Overtones (v=0→2)",
        "grp_pol": "5. Polarization Channels",
        "pol_total": "Total Unpolarized Cross Section (Total)",
        "pol_par": "Parallel Component (Parallel I_∥)",
        "pol_perp": "Perpendicular Component (Perpendicular I_⊥)",
        "pol_depol": "Depolarization Ratio (Depol. Ratio ρ)",
        "grp_inst": "6. Optical Resolution & Laser Linewidth",
        "lbl_fwhm": "Receiver Resolution / Filter FWHM:",
        "chk_laser_lw": "Enable Laser Linewidth Double Convolution",
        "lbl_laser_lw": "Laser Linewidth FWHM (nm):",
        "lw_presets": ["Single 0.00", "Std. YAG 0.02", "Broadband 0.08"],
        "eff_fwhm_conv": "Effective FWHM: {eff:.3f} nm{cm_note} (Double Conv.)",
        "eff_fwhm_single": "Effective FWHM: {inst:.3f} nm{cm_note} (Single Freq.)",
        "lbl_prof": "Instrument Line Profile:",
        "grp_disp": "7. Coordinates & Plot Style",
        "lbl_x": "X-Axis:",
        "x_wl": "Wavelength (nm)",
        "x_shift": "Raman Shift (cm⁻¹)",
        "lbl_y": "Y-Axis:",
        "y_lin": "Linear",
        "y_log": "Log10 Scale",
        "lbl_style": "Style:",
        "style_cont": "Continuous",
        "style_stick": "Stick Lines",
        "style_both": "Both",
        "btn_calc": "⚡ Recalculate & Refresh",
        "btn_web": "🌐 Open Interactive Web App (Plotly)",
        "btn_csv": "💾 Export CSV Data (English)",
        "btn_fig": "📷 Save High-DPI Figure",
        "status_ready": "Ready",
        "status_done": "✅ Calculation Done | Total Lines: {count} | Strongest: {strongest} (λ = {wl:.3f} nm, Δν = {shift:.2f} cm⁻¹, Cross = {cross:.3e} cm²/sr) | Integrated Cross: {tot:.3e} cm²/sr",
        "err_input_title": "Input Error",
        "err_input_msg": "Invalid parameter format. Please enter valid numeric values.\n{err}",
        "warn_trans_title": "Notice",
        "warn_trans_msg": "Please select at least one transition type (Pure Rot., Fundamental, Hot, or Overtone).",
        "warn_no_data_title": "Notice",
        "warn_no_data_msg": "No valid data available.",
        "export_csv_title": "Export Success",
        "export_csv_msg": "Line list (100% English format) successfully exported to:\n{path}",
        "export_csv_err_title": "Export Error",
        "export_fig_title": "Save Success",
        "export_fig_msg": "High-DPI figure successfully saved to:\n{path}",
        "export_fig_err_title": "Save Error",
        "legend_n2_cont": "N₂ Convolved",
        "legend_o2_cont": "O₂ Convolved",
        "legend_h2o_cont": "H₂O Convolved",
        "legend_conv": "{gas} Convolved ({tag})",
        "plot_title": r"{gas} Raman Spectrum ($\lambda_0$ = {wl:.1f} nm, T = {temp:.1f} K, Pol: {pol})"
    }
}


class RamanSpectroscopyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔬 氮气/氧气/水汽/空气拉曼散射光谱与截面高精度仿真软件 (双模专业版)")
        self.geometry("1420x920")
        self.minsize(1050, 720)

        # Style Configuration
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Data Cache
        self.current_lines = []
        self.last_computed_params = {}

        # Build UI Layout
        self._init_variables()
        self._create_layout()

        # Initial Computation & Plot
        self.recompute_and_plot()

    def _init_variables(self):
        """Initializes Tkinter state variables."""
        self.var_lang = tk.StringVar(value="zh")
        self.var_gas = tk.StringVar(value="Air")
        self.var_laser_nm = tk.DoubleVar(value=532.0)
        self.var_temp_k = tk.DoubleVar(value=296.15)
        self.var_enable_pressure = tk.BooleanVar(value=False)
        self.var_pressure_atm = tk.DoubleVar(value=1.00)
        
        # Transition toggles
        self.var_pure_rot = tk.BooleanVar(value=True)
        self.var_fundamental = tk.BooleanVar(value=True)
        self.var_hot_bands = tk.BooleanVar(value=False)
        self.var_overtones = tk.BooleanVar(value=False)
        
        # Polarization mode
        self.var_pol_mode = tk.StringVar(value="total")  # total, parallel, perpendicular, depol_ratio
        
        # Instrument & Laser Linewidth Profile
        self.var_fwhm = tk.DoubleVar(value=0.25)
        self.var_enable_laser_lw = tk.BooleanVar(value=False)
        self.var_laser_fwhm = tk.DoubleVar(value=0.020)
        self.var_profile = tk.StringVar(value="gaussian")
        
        # Axes & Plot style
        self.var_x_axis = tk.StringVar(value="wavelength")  # 'wavelength' or 'raman_shift'
        self.var_y_scale = tk.StringVar(value="linear")      # 'linear' or 'log10'
        self.var_plot_style = tk.StringVar(value="both")     # 'continuous', 'stick', 'both'

    def _create_layout(self):
        """Constructs UI sidebars, menus, and canvas."""
        # Top banner
        header = tk.Frame(self, bg="#1e293b", height=50)
        header.pack(side=tk.TOP, fill=tk.X)
        self.lbl_title = tk.Label(
            header,
            text="N₂ / O₂ / H₂O / Air 拉曼散射截面与波长高精度计算仿真平台",
            font=("Segoe UI", 14, "bold"),
            fg="#38bdf8",
            bg="#1e293b"
        )
        self.lbl_title.pack(side=tk.LEFT, padx=15, pady=10)

        # Right side controls: Language toggle and Subtitle
        lang_frame = tk.Frame(header, bg="#1e293b")
        lang_frame.pack(side=tk.RIGHT, padx=15, pady=10)

        self.btn_lang_zh = tk.Button(
            lang_frame, text="中文", font=("Segoe UI", 8, "bold"),
            bg="#0284c7", fg="white", activebackground="#0369a1", activeforeground="white",
            relief=tk.FLAT, padx=8, pady=2, cursor="hand2",
            command=lambda: self.set_language("zh")
        )
        self.btn_lang_zh.pack(side=tk.LEFT, padx=1)

        self.btn_lang_en = tk.Button(
            lang_frame, text="English", font=("Segoe UI", 8),
            bg="#334155", fg="#cbd5e1", activebackground="#475569", activeforeground="white",
            relief=tk.FLAT, padx=8, pady=2, cursor="hand2",
            command=lambda: self.set_language("en")
        )
        self.btn_lang_en.pack(side=tk.LEFT, padx=1)

        self.lbl_sub = tk.Label(
            header,
            text="量子微观能级 · 核自旋统计 · Placzek色散定律 · 温度玻尔兹曼布居 · 偏振退偏比",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#1e293b"
        )
        self.lbl_sub.pack(side=tk.RIGHT, padx=15, pady=12)

        # Main splitter (Left Sidebar + Right Plot)
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left control sidebar with scrolling capability
        sidebar_outer = tk.Frame(main_frame, width=390, bg="#f8fafc", relief=tk.RIDGE, bd=1)
        sidebar_outer.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        sidebar_outer.pack_propagate(False)

        canvas_sb = tk.Canvas(sidebar_outer, bg="#f8fafc", highlightthickness=0)
        scrollbar = ttk.Scrollbar(sidebar_outer, orient=tk.VERTICAL, command=canvas_sb.yview)
        self.sidebar = tk.Frame(canvas_sb, bg="#f8fafc", padx=12, pady=10)
        self.sidebar.bind("<Configure>", lambda e: canvas_sb.configure(scrollregion=canvas_sb.bbox("all")))
        canvas_sb.create_window((0, 0), window=self.sidebar, anchor="nw")
        canvas_sb.configure(yscrollcommand=scrollbar.set)
        canvas_sb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._populate_sidebar()

        # Right Plot Area
        plot_frame = tk.Frame(main_frame, bg="white")
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Matplotlib Figure
        self.fig = Figure(figsize=(9, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.10, right=0.96, top=0.92, bottom=0.12)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()

        # Matplotlib Navigation Toolbar
        toolbar_frame = tk.Frame(plot_frame, bg="#e2e8f0")
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Bottom Status / Peak Inspector Bar
        status_bar = tk.Frame(plot_frame, bg="#f1f5f9", height=45, bd=1, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_status = tk.Label(
            status_bar,
            text="就绪",
            font=("Segoe UI", 9),
            bg="#f1f5f9",
            fg="#334155",
            anchor="w"
        )
        self.lbl_status.pack(fill=tk.BOTH, padx=10, pady=5)

    def _populate_sidebar(self):
        """Populates left parameter widgets."""
        sb = self.sidebar

        # Group 1: Gas Selection
        self.grp_gas = ttk.LabelFrame(sb, text="1. 目标气体分子 (Target Gas)", padding=8)
        self.grp_gas.pack(fill=tk.X, pady=5)

        self.rb_gas_air = ttk.Radiobutton(self.grp_gas, text="标准干空气 (Dry Air: 78% N₂ + 21% O₂)",
                                          variable=self.var_gas, value="Air", command=self.recompute_and_plot)
        self.rb_gas_air.pack(anchor="w", pady=1.5)

        self.rb_gas_humid = ttk.Radiobutton(self.grp_gas, text="含湿空气 (Humid Air: 1% H₂O 水汽)",
                                            variable=self.var_gas, value="HumidAir", command=self.recompute_and_plot)
        self.rb_gas_humid.pack(anchor="w", pady=1.5)

        self.rb_gas_h2o = ttk.Radiobutton(self.grp_gas, text="水汽 (H₂O 纯气体)",
                                          variable=self.var_gas, value="H2O", command=self.recompute_and_plot)
        self.rb_gas_h2o.pack(anchor="w", pady=1.5)

        self.rb_gas_n2 = ttk.Radiobutton(self.grp_gas, text="氮气 (N₂ 纯气体)",
                                         variable=self.var_gas, value="N2", command=self.recompute_and_plot)
        self.rb_gas_n2.pack(anchor="w", pady=1.5)

        self.rb_gas_o2 = ttk.Radiobutton(self.grp_gas, text="氧气 (O₂ 纯气体)",
                                         variable=self.var_gas, value="O2", command=self.recompute_and_plot)
        self.rb_gas_o2.pack(anchor="w", pady=1.5)

        self.rb_gas_all = ttk.Radiobutton(self.grp_gas, text="全组分对比 (N₂, O₂, H₂O 同时绘制)",
                                          variable=self.var_gas, value="All", command=self.recompute_and_plot)
        self.rb_gas_all.pack(anchor="w", pady=1.5)

        # Group 2: Excitation Wavelength
        self.grp_laser = ttk.LabelFrame(sb, text="2. 激发激光波长 (Excitation λ₀)", padding=8)
        self.grp_laser.pack(fill=tk.X, pady=5)

        row_l = tk.Frame(self.grp_laser, bg="#f8fafc")
        row_l.pack(fill=tk.X, pady=2)
        self.lbl_laser_txt = ttk.Label(row_l, text="波长 λ₀ (nm):")
        self.lbl_laser_txt.pack(side=tk.LEFT)
        entry_laser = ttk.Entry(row_l, textvariable=self.var_laser_nm, width=10)
        entry_laser.pack(side=tk.RIGHT)
        entry_laser.bind("<Return>", lambda e: self.recompute_and_plot())

        # Quick preset buttons
        frame_presets = tk.Frame(self.grp_laser, bg="#f8fafc")
        frame_presets.pack(fill=tk.X, pady=4)
        for w_nm in [266.0, 355.0, 532.0, 632.8, 785.0, 1064.0]:
            btn = tk.Button(
                frame_presets, text=f"{int(w_nm) if w_nm.is_integer() else w_nm}",
                font=("Segoe UI", 7), relief=tk.GROOVE, bg="#e2e8f0",
                command=lambda w=w_nm: self._set_laser(w)
            )
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        # Group 3: Temperature
        self.grp_temp = ttk.LabelFrame(sb, text="3. 气体温度 (Temperature T)", padding=8)
        self.grp_temp.pack(fill=tk.X, pady=5)

        row_t = tk.Frame(self.grp_temp, bg="#f8fafc")
        row_t.pack(fill=tk.X, pady=2)
        self.lbl_temp_txt = ttk.Label(row_t, text="绝对温度 (K):")
        self.lbl_temp_txt.pack(side=tk.LEFT)
        self.lbl_t_val = ttk.Label(row_t, text=f"{self.var_temp_k.get():.1f} K", font=("Segoe UI", 9, "bold"))
        self.lbl_t_val.pack(side=tk.RIGHT)

        slider_t = ttk.Scale(
            self.grp_temp, from_=100.0, to=1500.0,
            variable=self.var_temp_k, orient=tk.HORIZONTAL,
            command=self._on_temp_slide
        )
        slider_t.pack(fill=tk.X, pady=4)

        # Quick preset buttons for Temperature
        frame_t_presets = tk.Frame(self.grp_temp, bg="#f8fafc")
        frame_t_presets.pack(fill=tk.X, pady=2)
        self.btn_t_presets = []
        for label, t_val in [("高空 220K", 220.0), ("常温 296K", 296.15), ("中温 600K", 600.0), ("火焰 1200K", 1200.0)]:
            btn_t = tk.Button(
                frame_t_presets, text=label, font=("Segoe UI", 7), relief=tk.GROOVE, bg="#e2e8f0",
                command=lambda t=t_val: self._set_temp(t)
            )
            btn_t.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
            self.btn_t_presets.append(btn_t)

        # Group 3.5: Environmental Pressure & Collisional Broadening
        self.grp_press = ttk.LabelFrame(sb, text="3.5 环境压强与碰撞展宽 (Pressure & Broadening)", padding=8)
        self.grp_press.pack(fill=tk.X, pady=5)

        self.chk_pressure = ttk.Checkbutton(
            self.grp_press,
            text="启用低层大气纯转动碰撞压力展宽",
            variable=self.var_enable_pressure,
            command=self._on_toggle_pressure
        )
        self.chk_pressure.pack(anchor="w", pady=(0, 2))

        self.frame_press_controls = tk.Frame(self.grp_press, bg="#f8fafc")
        self.frame_press_controls.pack(fill=tk.X, pady=2)

        row_p = tk.Frame(self.frame_press_controls, bg="#f8fafc")
        row_p.pack(fill=tk.X, pady=2)
        self.lbl_press_txt = ttk.Label(row_p, text="环境气压 P (atm):")
        self.lbl_press_txt.pack(side=tk.LEFT)
        self.lbl_p_val = ttk.Label(row_p, text=f"{self.var_pressure_atm.get():.2f} atm", font=("Segoe UI", 9, "bold"))
        self.lbl_p_val.pack(side=tk.RIGHT)

        self.slider_press = ttk.Scale(
            self.frame_press_controls, from_=0.00, to=2.00,
            variable=self.var_pressure_atm, orient=tk.HORIZONTAL,
            command=self._on_press_slide, state="disabled"
        )
        self.slider_press.pack(fill=tk.X, pady=4)

        # Quick preset buttons for Pressure
        self.frame_p_presets = tk.Frame(self.frame_press_controls, bg="#f8fafc")
        self.frame_p_presets.pack(fill=tk.X, pady=2)
        self.btn_p_presets = []
        for label, p_val in [("真空 0.00", 0.00), ("高空 0.25", 0.25), ("常压 1.00", 1.00), ("增压 1.50", 1.50)]:
            btn_p = tk.Button(
                self.frame_p_presets, text=label, font=("Segoe UI", 7), relief=tk.GROOVE, bg="#e2e8f0",
                state="disabled", command=lambda p=p_val: self._set_pressure(p)
            )
            btn_p.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
            self.btn_p_presets.append(btn_p)

        # Status badge for Pressure Broadening
        self.lbl_press_status = ttk.Label(
            self.grp_press,
            text="纯转动线型: 理想无碰撞基准 (未开启)",
            font=("Segoe UI", 8, "italic"),
            foreground="#64748b"
        )
        self.lbl_press_status.pack(anchor="w", pady=(3, 0))

        # Group 4: Transition Bands
        self.grp_trans = ttk.LabelFrame(sb, text="4. 跃迁阶数与分支 (Transitions)", padding=8)
        self.grp_trans.pack(fill=tk.X, pady=5)

        self.chk_pure_rot = ttk.Checkbutton(self.grp_trans, text="纯转动拉曼 (Pure Rotational S/O支)",
                                            variable=self.var_pure_rot, command=self.recompute_and_plot)
        self.chk_pure_rot.pack(anchor="w", pady=1)

        self.chk_fund = ttk.Checkbutton(self.grp_trans, text="基频振动-转动 (v=0→1, Q/O/S支)",
                                        variable=self.var_fundamental, command=self.recompute_and_plot)
        self.chk_fund.pack(anchor="w", pady=1)

        self.chk_hot = ttk.Checkbutton(self.grp_trans, text="热带跃迁 (Hot Bands v=1→2)",
                                       variable=self.var_hot_bands, command=self.recompute_and_plot)
        self.chk_hot.pack(anchor="w", pady=1)

        self.chk_over = ttk.Checkbutton(self.grp_trans, text="泛频跃迁 (Overtones v=0→2)",
                                        variable=self.var_overtones, command=self.recompute_and_plot)
        self.chk_over.pack(anchor="w", pady=1)

        # Group 5: Polarization Modes
        self.grp_pol = ttk.LabelFrame(sb, text="5. 偏振特性通道 (Polarization)", padding=8)
        self.grp_pol.pack(fill=tk.X, pady=5)

        self.rb_pol_total = ttk.Radiobutton(self.grp_pol, text="总非偏振截面 (Total)", variable=self.var_pol_mode,
                                            value="total", command=self.recompute_and_plot)
        self.rb_pol_total.pack(anchor="w", pady=1)

        self.rb_pol_par = ttk.Radiobutton(self.grp_pol, text="平行偏振分量 (Parallel I_∥)", variable=self.var_pol_mode,
                                          value="parallel", command=self.recompute_and_plot)
        self.rb_pol_par.pack(anchor="w", pady=1)

        self.rb_pol_perp = ttk.Radiobutton(self.grp_pol, text="垂直偏振分量 (Perpendicular I_⊥)", variable=self.var_pol_mode,
                                           value="perpendicular", command=self.recompute_and_plot)
        self.rb_pol_perp.pack(anchor="w", pady=1)

        self.rb_pol_depol = ttk.Radiobutton(self.grp_pol, text="退偏振比 (Depol. Ratio ρ)", variable=self.var_pol_mode,
                                            value="depol_ratio", command=self.recompute_and_plot)
        self.rb_pol_depol.pack(anchor="w", pady=1)

        # Group 6: Optical Resolution & Laser Linewidth Convolution
        self.grp_inst = ttk.LabelFrame(sb, text="6. 光学分辨率与激光谱宽 (Optics & Laser)", padding=8)
        self.grp_inst.pack(fill=tk.X, pady=5)

        # 1. Receiver resolution / filter bandwidth FWHM
        row_fwhm = tk.Frame(self.grp_inst, bg="#f8fafc")
        row_fwhm.pack(fill=tk.X, pady=2)
        self.lbl_fwhm_txt = ttk.Label(row_fwhm, text="接收分辨率/滤光片半宽:")
        self.lbl_fwhm_txt.pack(side=tk.LEFT)
        entry_fwhm = ttk.Entry(row_fwhm, textvariable=self.var_fwhm, width=7)
        entry_fwhm.pack(side=tk.RIGHT)
        entry_fwhm.bind("<Return>", lambda e: self.recompute_and_plot())

        # 2. Toggle for laser pulse linewidth double convolution
        row_chk_laser = tk.Frame(self.grp_inst, bg="#f8fafc")
        row_chk_laser.pack(fill=tk.X, pady=(6, 2))
        self.chk_laser_lw = ttk.Checkbutton(
            row_chk_laser,
            text="启用发射激光谱宽双重卷积",
            variable=self.var_enable_laser_lw,
            command=self._on_toggle_laser_lw
        )
        self.chk_laser_lw.pack(side=tk.LEFT)

        # 3. Laser linewidth controls frame
        self.frame_laser_lw = tk.Frame(self.grp_inst, bg="#f8fafc")
        self.frame_laser_lw.pack(fill=tk.X, pady=2)

        row_lw_input = tk.Frame(self.frame_laser_lw, bg="#f8fafc")
        row_lw_input.pack(fill=tk.X, pady=2)
        self.lbl_laser_lw_txt = ttk.Label(row_lw_input, text="激光谱宽 FWHM (nm):")
        self.lbl_laser_lw_txt.pack(side=tk.LEFT)
        self.entry_laser_lw = ttk.Entry(row_lw_input, textvariable=self.var_laser_fwhm, width=7, state="disabled")
        self.entry_laser_lw.pack(side=tk.RIGHT)
        self.entry_laser_lw.bind("<Return>", lambda e: self.recompute_and_plot())

        # Presets for laser linewidth
        self.frame_lw_presets = tk.Frame(self.frame_laser_lw, bg="#f8fafc")
        self.frame_lw_presets.pack(fill=tk.X, pady=2)
        self.btn_lw_presets = []
        for label, val in [("单频 0.00", 0.000), ("常规YAG 0.02", 0.020), ("宽带 0.08", 0.080)]:
            btn_lw = tk.Button(
                self.frame_lw_presets, text=label, font=("Segoe UI", 7), relief=tk.GROOVE, bg="#e2e8f0",
                state="disabled", command=lambda v=val: self._set_laser_lw(v)
            )
            btn_lw.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
            self.btn_lw_presets.append(btn_lw)

        # 4. Effective combined FWHM indicator
        self.lbl_eff_fwhm = ttk.Label(
            self.grp_inst,
            text=f"合成等效半宽: {self.var_fwhm.get():.3f} nm (单频基准)",
            font=("Segoe UI", 8, "italic"),
            foreground="#0369a1"
        )
        self.lbl_eff_fwhm.pack(anchor="w", pady=(2, 4))

        # 5. Profile function
        row_prof = tk.Frame(self.grp_inst, bg="#f8fafc")
        row_prof.pack(fill=tk.X, pady=2)
        self.lbl_prof_txt = ttk.Label(row_prof, text="仪器线形函数:")
        self.lbl_prof_txt.pack(side=tk.LEFT)
        cb_prof = ttk.Combobox(row_prof, textvariable=self.var_profile, values=["gaussian", "lorentzian"],
                               state="readonly", width=10)
        cb_prof.pack(side=tk.RIGHT)
        cb_prof.bind("<<ComboboxSelected>>", lambda e: self.recompute_and_plot())

        # Group 7: Plot Axes & Display Style
        self.grp_disp = ttk.LabelFrame(sb, text="7. 坐标系与呈现形式 (Display)", padding=8)
        self.grp_disp.pack(fill=tk.X, pady=5)

        row_x = tk.Frame(self.grp_disp, bg="#f8fafc")
        row_x.pack(fill=tk.X, pady=1)
        self.lbl_x_txt = ttk.Label(row_x, text="横坐标:")
        self.lbl_x_txt.pack(side=tk.LEFT)
        self.rb_x_wl = ttk.Radiobutton(row_x, text="波长 (nm)", variable=self.var_x_axis, value="wavelength",
                                      command=self.recompute_and_plot)
        self.rb_x_wl.pack(side=tk.LEFT, padx=5)
        self.rb_x_shift = ttk.Radiobutton(row_x, text="位移 (cm⁻¹)", variable=self.var_x_axis, value="raman_shift",
                                          command=self.recompute_and_plot)
        self.rb_x_shift.pack(side=tk.LEFT)

        row_y = tk.Frame(self.grp_disp, bg="#f8fafc")
        row_y.pack(fill=tk.X, pady=1)
        self.lbl_y_txt = ttk.Label(row_y, text="纵坐标:")
        self.lbl_y_txt.pack(side=tk.LEFT)
        self.rb_y_lin = ttk.Radiobutton(row_y, text="线性", variable=self.var_y_scale, value="linear",
                                        command=self.recompute_and_plot)
        self.rb_y_lin.pack(side=tk.LEFT, padx=5)
        self.rb_y_log = ttk.Radiobutton(row_y, text="对数 Log10", variable=self.var_y_scale, value="log10",
                                        command=self.recompute_and_plot)
        self.rb_y_log.pack(side=tk.LEFT)

        row_style = tk.Frame(self.grp_disp, bg="#f8fafc")
        row_style.pack(fill=tk.X, pady=1)
        self.lbl_style_txt = ttk.Label(row_style, text="样式:")
        self.lbl_style_txt.pack(side=tk.LEFT)
        self.rb_style_cont = ttk.Radiobutton(row_style, text="连续谱", variable=self.var_plot_style, value="continuous",
                                             command=self.recompute_and_plot)
        self.rb_style_cont.pack(side=tk.LEFT, padx=2)
        self.rb_style_stick = ttk.Radiobutton(row_style, text="线谱", variable=self.var_plot_style, value="stick",
                                              command=self.recompute_and_plot)
        self.rb_style_stick.pack(side=tk.LEFT, padx=2)
        self.rb_style_both = ttk.Radiobutton(row_style, text="两者", variable=self.var_plot_style, value="both",
                                             command=self.recompute_and_plot)
        self.rb_style_both.pack(side=tk.LEFT, padx=2)

        # Action Buttons
        frame_actions = tk.Frame(sb, bg="#f8fafc")
        frame_actions.pack(fill=tk.X, pady=12)

        self.btn_calc = tk.Button(
            frame_actions, text="⚡ 重新计算与刷新", font=("Segoe UI", 10, "bold"),
            bg="#0284c7", fg="white", activebackground="#0369a1", activeforeground="white",
            relief=tk.FLAT, padx=10, pady=6, cursor="hand2",
            command=self.recompute_and_plot
        )
        self.btn_calc.pack(fill=tk.X, pady=3)

        self.btn_web = tk.Button(
            frame_actions, text="🌐 在浏览器打开交互式图表 (Plotly)", font=("Segoe UI", 9, "bold"),
            bg="#0d9488", fg="white", activebackground="#0f766e", activeforeground="white",
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2",
            command=self.open_interactive_web
        )
        self.btn_web.pack(fill=tk.X, pady=3)

        row_export = tk.Frame(frame_actions, bg="#f8fafc")
        row_export.pack(fill=tk.X, pady=2)
        self.btn_csv = tk.Button(
            row_export, text="💾 导出数据表 CSV (英文)", font=("Segoe UI", 8),
            bg="#f1f5f9", fg="#334155", relief=tk.GROOVE, pady=4,
            command=self.export_csv
        )
        self.btn_csv.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        self.btn_fig = tk.Button(
            row_export, text="📷 保存高清图片", font=("Segoe UI", 8),
            bg="#f1f5f9", fg="#334155", relief=tk.GROOVE, pady=4,
            command=self.export_figure
        )
        self.btn_fig.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=1)

    def set_language(self, lang: str):
        """Switches UI language between Chinese and English."""
        self.var_lang.set(lang)
        t = GUI_I18N[lang]

        # Update language toggle button visual styles
        if lang == "zh":
            self.btn_lang_zh.config(bg="#0284c7", fg="white", font=("Segoe UI", 8, "bold"))
            self.btn_lang_en.config(bg="#334155", fg="#cbd5e1", font=("Segoe UI", 8))
        else:
            self.btn_lang_zh.config(bg="#334155", fg="#cbd5e1", font=("Segoe UI", 8))
            self.btn_lang_en.config(bg="#0284c7", fg="white", font=("Segoe UI", 8, "bold"))

        # Window & Header
        self.title(t["window_title"])
        self.lbl_title.config(text=t["header_title"])
        self.lbl_sub.config(text=t["header_sub"])

        # Group 1: Gas
        self.grp_gas.config(text=t["grp_gas"])
        self.rb_gas_air.config(text=t["gas_air"])
        self.rb_gas_humid.config(text=t["gas_humid"])
        self.rb_gas_h2o.config(text=t["gas_h2o"])
        self.rb_gas_n2.config(text=t["gas_n2"])
        self.rb_gas_o2.config(text=t["gas_o2"])
        self.rb_gas_all.config(text=t["gas_all"])

        # Group 2: Laser
        self.grp_laser.config(text=t["grp_laser"])
        self.lbl_laser_txt.config(text=t["lbl_laser"])

        # Group 3: Temperature
        self.grp_temp.config(text=t["grp_temp"])
        self.lbl_temp_txt.config(text=t["lbl_temp"])
        for btn, label in zip(self.btn_t_presets, t["temp_presets"]):
            btn.config(text=label)

        # Group 3.5: Pressure
        self.grp_press.config(text=t["grp_press"])
        self.chk_pressure.config(text=t["chk_press"])
        self.lbl_press_txt.config(text=t["lbl_press"])
        for btn, label in zip(self.btn_p_presets, t["press_presets"]):
            btn.config(text=label)

        # Group 4: Transitions
        self.grp_trans.config(text=t["grp_trans"])
        self.chk_pure_rot.config(text=t["chk_pure_rot"])
        self.chk_fund.config(text=t["chk_fund"])
        self.chk_hot.config(text=t["chk_hot"])
        self.chk_over.config(text=t["chk_over"])

        # Group 5: Polarization
        self.grp_pol.config(text=t["grp_pol"])
        self.rb_pol_total.config(text=t["pol_total"])
        self.rb_pol_par.config(text=t["pol_par"])
        self.rb_pol_perp.config(text=t["pol_perp"])
        self.rb_pol_depol.config(text=t["pol_depol"])

        # Group 6: Optics & Laser Linewidth
        self.grp_inst.config(text=t["grp_inst"])
        self.lbl_fwhm_txt.config(text=t["lbl_fwhm"])
        self.chk_laser_lw.config(text=t["chk_laser_lw"])
        self.lbl_laser_lw_txt.config(text=t["lbl_laser_lw"])
        for btn, label in zip(self.btn_lw_presets, t["lw_presets"]):
            btn.config(text=label)
        self.lbl_prof_txt.config(text=t["lbl_prof"])

        # Group 7: Display
        self.grp_disp.config(text=t["grp_disp"])
        self.lbl_x_txt.config(text=t["lbl_x"])
        self.rb_x_wl.config(text=t["x_wl"])
        self.rb_x_shift.config(text=t["x_shift"])
        self.lbl_y_txt.config(text=t["lbl_y"])
        self.rb_y_lin.config(text=t["y_lin"])
        self.rb_y_log.config(text=t["y_log"])
        self.lbl_style_txt.config(text=t["lbl_style"])
        self.rb_style_cont.config(text=t["style_cont"])
        self.rb_style_stick.config(text=t["style_stick"])
        self.rb_style_both.config(text=t["style_both"])

        # Action buttons
        self.btn_calc.config(text=t["btn_calc"])
        self.btn_web.config(text=t["btn_web"])
        self.btn_csv.config(text=t["btn_csv"])
        self.btn_fig.config(text=t["btn_fig"])

        # Refresh indicators and plot
        self._update_eff_fwhm_label()
        self._update_press_label()
        self.recompute_and_plot()

    def _set_laser(self, val: float):
        self.var_laser_nm.set(val)
        self.recompute_and_plot()

    def _set_temp(self, val: float):
        self.var_temp_k.set(val)
        self.lbl_t_val.config(text=f"{val:.1f} K")
        self._update_press_label()
        self.recompute_and_plot()

    def _on_temp_slide(self, val):
        t_float = float(val)
        self.lbl_t_val.config(text=f"{t_float:.1f} K")
        self._update_press_label()
        self.recompute_and_plot()

    def _on_toggle_pressure(self):
        state = "normal" if self.var_enable_pressure.get() else "disabled"
        self.slider_press.configure(state=state)
        for child in self.frame_p_presets.winfo_children():
            child.configure(state=state)
        self._update_press_label()
        self.recompute_and_plot()

    def _on_press_slide(self, val):
        self.lbl_p_val.configure(text=f"{float(val):.2f} atm")
        self._update_press_label()
        self.recompute_and_plot()

    def _set_pressure(self, val: float):
        self.var_pressure_atm.set(val)
        self.lbl_p_val.configure(text=f"{val:.2f} atm")
        self._update_press_label()
        self.recompute_and_plot()

    def _update_press_label(self):
        try:
            lang = self.var_lang.get()
            t = GUI_I18N[lang]
            if not self.var_enable_pressure.get():
                self.lbl_press_status.config(
                    text=t["press_status_off"],
                    foreground="#64748b"
                )
            else:
                p_atm = float(self.var_pressure_atm.get())
                t_k = float(self.var_temp_k.get())
                w_nm = float(self.var_laser_nm.get())
                gamma_cm = compute_collisional_broadening_hwhm("N2", 6, p_atm, t_k)
                fwhm_cm = 2.0 * gamma_cm
                fwhm_nm = fwhm_cm * (w_nm**2) / 1e7
                self.lbl_press_status.config(
                    text=t["press_status_on"].format(fwhm_cm=fwhm_cm, fwhm_nm_pm=fwhm_nm*1000),
                    foreground="#4338ca"
                )
        except Exception:
            pass

    def _on_toggle_laser_lw(self):
        state = "normal" if self.var_enable_laser_lw.get() else "disabled"
        self.entry_laser_lw.configure(state=state)
        for child in self.frame_lw_presets.winfo_children():
            child.configure(state=state)
        self._update_eff_fwhm_label()
        self.recompute_and_plot()

    def _set_laser_lw(self, val: float):
        self.var_laser_fwhm.set(val)
        self._update_eff_fwhm_label()
        self.recompute_and_plot()

    def _update_eff_fwhm_label(self):
        try:
            lang = self.var_lang.get()
            t = GUI_I18N[lang]
            inst_w = float(self.var_fwhm.get())
            laser_w = float(self.var_laser_fwhm.get())
            enable_lw = bool(self.var_enable_laser_lw.get())
            profile = self.var_profile.get()
            w_nm = max(100.0, float(self.var_laser_nm.get()))
            eff = compute_effective_fwhm(inst_w, laser_w, enable_lw, profile=profile)
            is_cm = (self.var_x_axis.get() == "raman_shift")
            cm_prefix = " (折合 " if lang == "zh" else " (equiv. "
            cm_note = f"{cm_prefix}{eff * (1e7 / (w_nm**2)):.2f} cm⁻¹)" if is_cm else ""
            if enable_lw and laser_w > 0:
                self.lbl_eff_fwhm.config(
                    text=t["eff_fwhm_conv"].format(eff=eff, cm_note=cm_note),
                    foreground="#d97706"
                )
            else:
                self.lbl_eff_fwhm.config(
                    text=t["eff_fwhm_single"].format(inst=inst_w, cm_note=cm_note),
                    foreground="#0369a1"
                )
        except Exception:
            pass

    def recompute_and_plot(self):
        """Core computation and rendering routine."""
        lang = self.var_lang.get()
        t = GUI_I18N[lang]

        try:
            gas = self.var_gas.get()
            w_nm = max(100.0, min(3000.0, float(self.var_laser_nm.get())))
            temp_k = max(10.0, min(3000.0, float(self.var_temp_k.get())))
            pure_rot = self.var_pure_rot.get()
            fund = self.var_fundamental.get()
            hot = self.var_hot_bands.get()
            over = self.var_overtones.get()
            pol = self.var_pol_mode.get()
            fwhm = max(0.01, float(self.var_fwhm.get()))
            enable_laser_conv = bool(self.var_enable_laser_lw.get())
            laser_fwhm = max(0.0, float(self.var_laser_fwhm.get())) if enable_laser_conv else 0.0
            enable_pressure = bool(self.var_enable_pressure.get())
            pressure_atm = float(self.var_pressure_atm.get()) if enable_pressure else 0.0
            profile = self.var_profile.get()
            eff_fwhm = compute_effective_fwhm(fwhm, laser_fwhm, enable_laser_conv, profile=profile)
            x_mode = self.var_x_axis.get()
            y_scale = self.var_y_scale.get()
            p_style = self.var_plot_style.get()
            self._update_eff_fwhm_label()
            self._update_press_label()
        except Exception as e:
            messagebox.showerror(t["err_input_title"], t["err_input_msg"].format(err=str(e)))
            return

        if not (pure_rot or fund or hot or over):
            messagebox.showwarning(t["warn_trans_title"], t["warn_trans_msg"])
            return

        self.ax.clear()

        # Cache parameters
        self.last_computed_params = {
            "gas": gas, "w_nm": w_nm, "temp_k": temp_k, "pressure_atm": pressure_atm,
            "pure_rot": pure_rot, "fund": fund, "hot": hot, "over": over,
            "pol": pol, "fwhm": fwhm, "laser_fwhm": laser_fwhm,
            "enable_laser_conv": enable_laser_conv, "eff_fwhm": eff_fwhm,
            "enable_pressure": enable_pressure,
            "profile": profile, "x_mode": x_mode
        }

        # Multi-gas comparison mode vs single gas
        if gas in ("Both", "All"):
            calc_n2 = RamanGasCalculator("N2", excitation_nm=w_nm, temperature_k=temp_k, pressure_atm=pressure_atm)
            lines_n2 = calc_n2.compute_all_transitions(pure_rot, fund, hot, over, pol)
            calc_o2 = RamanGasCalculator("O2", excitation_nm=w_nm, temperature_k=temp_k, pressure_atm=pressure_atm)
            lines_o2 = calc_o2.compute_all_transitions(pure_rot, fund, hot, over, pol)
            calc_h2o = RamanGasCalculator("H2O", excitation_nm=w_nm, temperature_k=temp_k, pressure_atm=pressure_atm)
            lines_h2o = calc_h2o.compute_all_transitions(pure_rot, fund, hot, over, pol)
            self.current_lines = lines_n2 + lines_o2 + lines_h2o

            all_lines = self.current_lines
            if not all_lines:
                return

            x_key = "wavelength_nm" if x_mode == "wavelength" else "raman_shift_cm"
            x_vals = [l[x_key] for l in all_lines]
            margin = 3.0 if x_mode == "wavelength" else 80.0
            x_grid = np.linspace(min(x_vals) - margin, max(x_vals) + margin, 3500)

            fwhm_grid = eff_fwhm * (1e7 / (w_nm**2)) if x_mode == "raman_shift" else eff_fwhm
            spec_n2 = convolve_spectrum(lines_n2, x_grid, fwhm=fwhm_grid, x_axis_mode=x_mode, profile=profile,
                                        enable_pressure_broadening=enable_pressure)
            spec_o2 = convolve_spectrum(lines_o2, x_grid, fwhm=fwhm_grid, x_axis_mode=x_mode, profile=profile,
                                        enable_pressure_broadening=enable_pressure)
            spec_h2o = convolve_spectrum(lines_h2o, x_grid, fwhm=fwhm_grid, x_axis_mode=x_mode, profile=profile,
                                         enable_pressure_broadening=enable_pressure)

            if p_style in ("continuous", "both"):
                press_tag = f" (+ P={pressure_atm:.2f}atm)" if enable_pressure else ""
                self.ax.plot(x_grid, spec_n2, color="#1f77b4", lw=1.8, label=f"{t['legend_n2_cont']}{press_tag}", alpha=0.9)
                self.ax.plot(x_grid, spec_o2, color="#2ca02c", lw=1.8, label=f"{t['legend_o2_cont']}{press_tag}", alpha=0.9)
                self.ax.plot(x_grid, spec_h2o, color="#d97706", lw=1.8, label=f"{t['legend_h2o_cont']}{press_tag}", alpha=0.9)

            if p_style in ("stick", "both"):
                for l in lines_n2:
                    self.ax.plot([l[x_key], l[x_key]], [0, l["active_cross_section"]],
                                 color="#1f77b4", alpha=0.35, lw=1.0)
                for l in lines_o2:
                    self.ax.plot([l[x_key], l[x_key]], [0, l["active_cross_section"]],
                                 color="#2ca02c", alpha=0.35, lw=1.0)
                for l in lines_h2o:
                    self.ax.plot([l[x_key], l[x_key]], [0, l["active_cross_section"]],
                                 color="#d97706", alpha=0.35, lw=1.0)

        else:
            if gas == "Air":
                lines = compute_air_spectrum(w_nm, temp_k, pure_rot, fund, hot, over, pol, h2o_fraction=0.0,
                                             pressure_atm=pressure_atm)
            elif gas == "HumidAir":
                lines = compute_air_spectrum(w_nm, temp_k, pure_rot, fund, hot, over, pol, h2o_fraction=0.01,
                                             pressure_atm=pressure_atm)
            else:
                calc = RamanGasCalculator(gas, excitation_nm=w_nm, temperature_k=temp_k, pressure_atm=pressure_atm)
                lines = calc.compute_all_transitions(pure_rot, fund, hot, over, pol)

            self.current_lines = lines
            if not lines:
                return

            x_key = "wavelength_nm" if x_mode == "wavelength" else "raman_shift_cm"
            x_vals = [l[x_key] for l in lines]
            margin = 3.0 if x_mode == "wavelength" else 80.0
            x_grid = np.linspace(min(x_vals) - margin, max(x_vals) + margin, 3500)
            fwhm_grid = eff_fwhm * (1e7 / (w_nm**2)) if x_mode == "raman_shift" else eff_fwhm
            spec_total = convolve_spectrum(lines, x_grid, fwhm=fwhm_grid, x_axis_mode=x_mode, profile=profile,
                                           enable_pressure_broadening=enable_pressure)

            fwhm_unit = "cm⁻¹" if x_mode == "raman_shift" else "nm"
            fwhm_disp = fwhm_grid if x_mode == "raman_shift" else eff_fwhm
            press_str = f" + P={pressure_atm:.2f}atm" if enable_pressure else ""
            fwhm_tag = f"FWHM_eff={fwhm_disp:.3f}{fwhm_unit}{press_str}" if enable_laser_conv else f"FWHM={fwhm_disp:.2f}{fwhm_unit}{press_str}"
            if p_style in ("continuous", "both"):
                self.ax.plot(x_grid, spec_total, color="#0f172a", lw=2.0,
                             label=t["legend_conv"].format(gas=gas, tag=fwhm_tag), zorder=4)

            if p_style in ("stick", "both"):
                # Color code by transition type and molecule
                for l in lines:
                    branch = l.get("branch", "Q")
                    t_type = l.get("type", "")
                    mol = l.get("molecule", "")
                    if "H₂O" in mol:
                        c = "#d97706"
                    elif "Pure Rotational" in t_type:
                        c = "#0284c7" if l.get("direction") == "Stokes" else "#06b6d4"
                    elif "Fundamental" in t_type:
                        c = "#dc2626" if branch == "Q" else "#ea580c"
                    else:
                        c = "#7c3aed"
                    self.ax.plot([l[x_key], l[x_key]], [0, l["active_cross_section"]],
                                 color=c, alpha=0.55, lw=1.0, zorder=3)

        # Axis labeling and formatting
        if x_mode == "wavelength":
            self.ax.set_xlabel(r"$\mathrm{Wavelength\ \lambda\ (nm)}$", fontsize=11, fontweight="bold")
        else:
            self.ax.set_xlabel(r"$\mathrm{Raman\ Shift\ \Delta\tilde{\nu}\ (cm^{-1})}$", fontsize=11, fontweight="bold")

        if pol == "depol_ratio":
            self.ax.set_ylabel(r"$\mathrm{Depolarization\ Ratio\ \rho}$", fontsize=11, fontweight="bold")
        else:
            unit_str = "nm^{-1}" if x_mode == "wavelength" else "cm"
            self.ax.set_ylabel(rf"$\mathrm{{d\sigma/d\Omega\ (cm^2\cdot sr^{{-1}}\cdot {unit_str})}}$",
                               fontsize=11, fontweight="bold")

        if y_scale == "log10":
            self.ax.set_yscale("log")
            self.ax.set_ylim(bottom=1e-36)

        title_str = t["plot_title"].format(gas=gas, wl=w_nm, temp=temp_k, pol=pol)
        self.ax.set_title(title_str, fontsize=12, pad=10, fontweight="bold")
        self.ax.grid(True, linestyle="--", alpha=0.4, color="#cbd5e1")
        self.ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#cbd5e1", fontsize=9)

        self.canvas.draw()

        # Update Status Bar with physics metrics
        if self.current_lines:
            strongest = max(self.current_lines, key=lambda x: x["active_cross_section"])
            tot_cross = sum(l["active_cross_section"] for l in self.current_lines)
            status_text = t["status_done"].format(
                count=len(self.current_lines),
                strongest=strongest['transition_label'],
                wl=strongest['wavelength_nm'],
                shift=strongest['raman_shift_cm'],
                cross=strongest['active_cross_section'],
                tot=tot_cross
            )
            self.lbl_status.config(text=status_text, fg="#0f766e")

    def open_interactive_web(self):
        """Generates standalone HTML and opens it in the default web browser."""
        params = self.last_computed_params
        gas = "Air" if params.get("gas") == "Both" else params.get("gas", "Air")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(script_dir, "raman_interactive.html")

        generate_standalone_html(
            gas=gas,
            excitation_nm=params.get("w_nm", 532.0),
            temperature_k=params.get("temp_k", 296.15),
            include_pure_rot=params.get("pure_rot", True),
            include_fundamental=params.get("fund", True),
            include_hot_bands=params.get("hot", False),
            include_overtones=params.get("over", False),
            pol_mode=params.get("pol", "total"),
            fwhm=params.get("fwhm", 0.25),
            x_axis=params.get("x_mode", "wavelength"),
            output_path=html_path
        )
        webbrowser.open(f"file:///{html_path}")

    def export_csv(self):
        """Exports calculated transitions line list to CSV (100% English ASCII with UTF-8 BOM)."""
        lang = self.var_lang.get()
        t = GUI_I18N[lang]
        if not self.current_lines:
            messagebox.showinfo(t["warn_no_data_title"], t["warn_no_data_msg"])
            return

        gas_clean = self.var_gas.get().replace("₂", "2")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV (Comma Separated Values)", "*.csv"), ("All Files (*.*)", "*.*")],
            initialfile=f"raman_{gas_clean}_{self.var_laser_nm.get():.1f}nm_{self.var_temp_k.get():.1f}K.csv"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8-sig") as f:
                # 100% English ASCII Header
                f.write("Molecule,Transition_Type,Branch,Direction,v_lower,J_lower,v_upper,J_upper,Wavelength_nm,Raman_Shift_cm-1,Diff_Cross_Section_cm2_sr,Active_Cross_Section_cm2_sr,Depolarization_Ratio_rho,Collisional_FWHM_cm-1,Collisional_FWHM_nm,Transition_Label\n")
                for l in self.current_lines:
                    mol_ascii = l['molecule'].replace("₂", "2")
                    label_ascii = l['transition_label'].replace("₂", "2").replace("ν", "nu").replace("₁", "1")
                    type_ascii = l['type'].replace("ν", "nu").replace("₁", "1").replace("₂", "2")
                    c_cm = l.get('fwhm_coll_cm', 0.0)
                    c_nm = l.get('fwhm_coll_nm', 0.0)
                    f.write(
                        f"{mol_ascii},{type_ascii},{l['branch']},{l.get('direction', 'Stokes')},"
                        f"{l['v_lower']},{l['J_lower']},{l['v_upper']},{l['J_upper']},"
                        f"{l['wavelength_nm']:.5f},{l['raman_shift_cm']:.3f},"
                        f"{l['cross_section_cm2_sr']:.5e},{l.get('active_cross_section', l['cross_section_cm2_sr']):.5e},"
                        f"{l.get('depol_ratio', 0.75):.4f},{c_cm:.4f},{c_nm:.6f},{label_ascii}\n"
                    )
            messagebox.showinfo(t["export_csv_title"], t["export_csv_msg"].format(path=file_path))
        except Exception as e:
            messagebox.showerror(t["export_csv_err_title"], f"{str(e)}")

    def export_figure(self):
        """Saves current Matplotlib figure at high DPI."""
        lang = self.var_lang.get()
        t = GUI_I18N[lang]
        gas_clean = self.var_gas.get().replace("₂", "2")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image (300 DPI)", "*.png"), ("PDF Vector (*.pdf)", "*.pdf"), ("SVG Vector (*.svg)", "*.svg")],
            initialfile=f"raman_spectrum_{gas_clean}_{self.var_laser_nm.get():.1f}nm.png"
        )
        if not file_path:
            return

        try:
            self.fig.savefig(file_path, dpi=300, bbox_inches="tight")
            messagebox.showinfo(t["export_fig_title"], t["export_fig_msg"].format(path=file_path))
        except Exception as e:
            messagebox.showerror(t["export_fig_err_title"], f"{str(e)}")


def main():
    app = RamanSpectroscopyApp()
    app.mainloop()


if __name__ == "__main__":
    main()
