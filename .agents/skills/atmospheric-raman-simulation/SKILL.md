---
name: atmospheric-raman-simulation
description: >-
  Simulates high-precision Raman scattering spectra, differential scattering cross-sections,
  and lidar return channels for atmospheric gases (N2, O2, H2O, dry/humid air).
  Covers quantum rovibrational energy levels (Dunham expansion), nuclear spin statistics,
  Placzek polarizability dispersion, laser pulse and spectrometer resolution double convolution,
  lower-atmosphere collisional pressure broadening (Behrendt-Reichardt J-dependent model),
  and Olivero-Longbothum Pseudo-Voigt line synthesis.
  Use when modeling atmospheric Raman lidars, calculating temperature-dependent pure rotational
  Raman profiles, determining water vapor mixing ratio calibration factors, or convolving
  real-world instrument lineshapes.
---

# Atmospheric Raman Scattering & Lidar Spectroscopy Simulation

This skill provides quantum mechanical formulations, polarizability dispersion equations, and atmospheric lidar modeling methods for Raman scattering by diatomic and triatomic atmospheric gases ($\text{N}_2, \text{O}_2, \text{H}_2\text{O}$, dry/humid air).

---

## 1. Overview & Applicability

Use this skill when:
- Designing or simulating **atmospheric Raman lidars** (temperature profiling via Pure Rotational Raman, moisture profiling via $\text{H}_2\text{O}/\text{N}_2$ vibrational Raman).
- Calculating **differential Raman scattering cross sections** $\frac{d\sigma}{d\Omega}$ across arbitrary excitation wavelengths ($200 \sim 2000\ \text{nm}$) and temperatures ($10 \sim 3000\ \text{K}$).
- Synthesizing **realistic convolved spectra** accounting for both receiver instrument resolution (slit/filter FWHM) and transmitter laser pulse linewidth.
- Modeling **tropospheric collisional pressure broadening** and filter channel crosstalk (Lorentzian far-wing skirts) using Pseudo-Voigt line shapes.
- Calibrating atmospheric water vapor mixing ratio lidar retrieval constants $C_{\text{sys}}$.

---

## 2. Molecular Energy Levels & Rovibrational Constants

### A. Dunham Expansion for Rovibrational Terms
The term energy $T(v, J)$ (in $\text{cm}^{-1}$) above the potential minimum:
$$T(v, J) = G(v) + F_v(J)$$
$$G(v) = \omega_e \left(v + \frac{1}{2}\right) - \omega_e x_e \left(v + \frac{1}{2}\right)^2$$
$$F_v(J) = B_v J(J + 1) - D_e [J(J + 1)]^2, \quad B_v = B_e - \alpha_e \left(v + \frac{1}{2}\right)$$

### B. Standard Spectroscopic Constants (NIST SRD 69 / Herzberg)

| Molecule | Mode / State | $\omega_e\ (\text{cm}^{-1})$ | $\omega_e x_e\ (\text{cm}^{-1})$ | $B_e\ (\text{cm}^{-1})$ | $\alpha_e\ (\text{cm}^{-1})$ | $D_e\ (\text{cm}^{-1})$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$^{14}\text{N}_2$** | $X^1\Sigma_g^+$ | $2358.57$ | $14.324$ | $1.99824$ | $0.01732$ | $5.76 \times 10^{-6}$ |
| **$^{16}\text{O}_2$** | $X^3\Sigma_g^-$ | $1580.19$ | $11.980$ | $1.44563$ | $0.01580$ | $4.88 \times 10^{-6}$ |
| **$\text{H}_2\text{O}$** | $\nu_1$ (Sym. stretch) | $3657.05$ | $43.800$ | $14.52000$ | $0.12000$ | $3.20 \times 10^{-4}$ |
| **$\text{H}_2\text{O}$** | $\nu_2$ (Bending) | $1594.75$ | $19.500$ | $14.52000$ | $0.12000$ | $3.20 \times 10^{-4}$ |

---

## 3. Nuclear Spin Statistics & Boltzmann Population

### A. Nuclear Spin Wavefunction Parity
- **$^{14}\text{N}_2$ ($I=1$, Boson)**: Total wavefunction symmetry dictates:
  $$g_J = \begin{cases} 6 & (J \text{ even}) \\ 3 & (J \text{ odd}) \end{cases} \implies \text{Even} : \text{Odd} = 2 : 1$$
- **$^{16}\text{O}_2$ ($I=0$, Boson, $X^3\Sigma_g^-$ ground state)**: Inversion anti-symmetry requires:
  $$g_J = \begin{cases} 0 & (J \text{ even, strictly forbidden}) \\ 1 & (J \text{ odd, allowed transitions}) \end{cases}$$
- **$\text{H}_2\text{O}$ ($I=1/2$, Fermion protons, $C_{2v}$)**:
  $$g_J = \begin{cases} 3 & (J \text{ odd, Ortho-water}) \\ 1 & (J \text{ even, Para-water}) \end{cases} \implies \text{Ortho} : \text{Para} = 3 : 1$$

### B. Boltzmann Population & Total Partition Function
Relative population of level $(v, J)$ at temperature $T$ (K):
$$P(v, J) = \frac{(2J + 1) g_J \exp\left(-\frac{hc [T(v, J) - T(0, J_0)]}{k_B T}\right)}{Q(T)}$$
$$Q(T) = \sum_{v=0}^{v_{\max}} \sum_{J=0}^{J_{\max}} (2J + 1) g_J \exp\left(-\frac{hc [T(v, J) - T(0, J_0)]}{k_B T}\right)$$
Where $\frac{hc}{k_B} \approx 1.438776877\ \text{cm}\cdot\text{K}$ (CODATA 2018).

---

## 4. Placzek Polarizability & Differential Scattering Cross Sections

### A. Pure Rotational Raman Scattering (PRR)
Differential cross section for transition $J \to J'$:
$$\left(\frac{d\sigma}{d\Omega}\right)_{J \to J'} = \frac{64\pi^4}{45} (\nu_0 \mp \Delta\nu)^4 \gamma^2 b_{J \to J'} P(0, J)$$
Where Placzek-Teller coefficients $b_{J \to J'}$ are:
- Stokes $S$-branch ($\Delta J = +2$):
  $$b_{J \to J+2} = \frac{3(J + 1)(J + 2)}{2(2J + 1)(2J + 3)}$$
- Anti-Stokes $O$-branch ($\Delta J = -2$):
  $$b_{J \to J-2} = \frac{3J(J - 1)}{2(2J + 1)(2J - 1)}$$
Polarizability anisotropy tensor invariants:
$$\gamma^2(\text{N}_2) \approx 0.50 \times 10^{-48}\ \text{cm}^6, \quad \gamma^2(\text{O}_2) \approx 1.25 \times 10^{-48}\ \text{cm}^6, \quad \gamma^2(\text{H}_2\text{O}) \approx 0.10 \times 10^{-48}\ \text{cm}^6$$

### B. Vibrational Raman Bands & Placzek $(\nu_0 - \Delta\nu)^4$ Dispersion Scaling
$$\left(\frac{d\sigma(\nu_0)}{d\Omega}\right)_{\text{vib}} = \left(\frac{d\sigma(\nu_{\text{ref}})}{d\Omega}\right) \cdot \left(\frac{\nu_0 - \Delta\nu}{\nu_{\text{ref}} - \Delta\nu}\right)^4$$
Reference differential cross sections at $\lambda_{\text{ref}} = 532.0\ \text{nm}$ ($\nu_{\text{ref}} = 18796.99\ \text{cm}^{-1}$):
- $\text{N}_2$ Fundamental ($\Delta\nu = 2330.7\ \text{cm}^{-1}$): $\sigma_{\text{ref}} = 3.8 \times 10^{-31}\ \text{cm}^2/\text{sr}$
- $\text{O}_2$ Fundamental ($\Delta\nu = 1555.6\ \text{cm}^{-1}$): $\sigma_{\text{ref}} = 5.1 \times 10^{-31}\ \text{cm}^2/\text{sr}$
- $\text{H}_2\text{O}\ \nu_1$ Stretch ($\Delta\nu = 3657.05\ \text{cm}^{-1}$): $\sigma_{\text{ref}} = 9.5 \times 10^{-31}\ \text{cm}^2/\text{sr}$ ($\approx 2.5 \times \text{N}_2$)
- $\text{H}_2\text{O}\ \nu_2$ Bend ($\Delta\nu = 1594.75\ \text{cm}^{-1}$): $\sigma_{\text{ref}} = 0.38 \times 10^{-31}\ \text{cm}^2/\text{sr}$
- Hot band ($v=1 \to 2$) factor: $(v + 1) = 2.0 \times P(1, J)$
- Overtone ($v=0 \to 2$) factor: $\frac{1}{2} (2\omega_e x_e / \omega_e)^2$

### C. Polarization Channels & Depolarization Ratios ($\rho$)
$$I_\parallel = \frac{1}{1 + \rho} \cdot \left(\frac{d\sigma}{d\Omega}\right), \quad I_\perp = \frac{\rho}{1 + \rho} \cdot \left(\frac{d\sigma}{d\Omega}\right)$$
- Anisotropic Pure Rotational lines & Vibrational $O/S$ branches: $\rho = 3/4 = 0.75$.
- Isotropic Vibrational $Q$-branches: $\rho_Q(\text{N}_2) \approx 0.035$, $\rho_Q(\text{O}_2) \approx 0.065$, $\rho_Q(\text{H}_2\text{O}) \approx 0.050$.

---

## 5. Laser Pulse & Receiver Resolution Double Convolution

### A. Analytical Quad-Sum & Cauchy Addition Theorems
Avoid quadratic $O(N \cdot M)$ numerical convolution by utilizing analytical distribution convolution:
- **Gaussian Profile (Normal Distribution)**:
  $$\text{FWHM}_{\text{eff}} = \sqrt{\text{FWHM}_{\text{inst}}^2 + \text{FWHM}_{\text{laser}}^2}$$
- **Lorentzian Profile (Cauchy Distribution)**:
  $$\text{FWHM}_{\text{eff}} = \text{FWHM}_{\text{inst}} + \text{FWHM}_{\text{laser}}$$

### B. Cross-Domain Differential Jacobian Mapping
When switching the X-axis from wavelength ($\text{nm}$) to Raman shift ($\text{cm}^{-1}$), preserve physical linewidth:
$$\Delta\tilde{\nu}_{\text{eff}} \approx \frac{10^7}{\lambda_0^2} \Delta\lambda_{\text{eff}}$$
*(e.g., at $532\ \text{nm}$, $0.20\ \text{nm}$ instrument resolution corresponds strictly to $7.07\ \text{cm}^{-1}$)*.

---

## 6. Lower-Atmosphere Collisional Pressure Broadening & Pseudo-Voigt Profile

### A. $J$-Dependent Empirical Collisional Model (Behrendt & Reichardt 2000)
$$\gamma_{\text{coll}}(J, P, T) = \gamma_0(J) \cdot \left(\frac{P}{P_0}\right) \cdot \left(\frac{T_0}{T}\right)^n, \quad \text{FWHM}_{\text{coll}} = 2\gamma_{\text{coll}}$$
- **$^{14}\text{N}_2$**:
  $$\gamma_0(J) = \begin{cases} 0.050 + 0.023(J / 6.5) & (J < 6.5) \\ 0.020 + 0.053\exp\left(-\left(\frac{J - 6.5}{6.2}\right)^2\right) & (J \ge 6.5) \end{cases}, \quad n = 0.70$$
  Clamped to $[0.018, 0.075]\ \text{cm}^{-1}$.
- **$^{16}\text{O}_2$**:
  $$\gamma_0(J) = \begin{cases} 0.042 + 0.018(J / 5.5) & (J < 5.5) \\ 0.018 + 0.042\exp\left(-\left(\frac{J - 5.5}{5.5}\right)^2\right) & (J \ge 5.5) \end{cases}, \quad n = 0.75$$
  Clamped to $[0.016, 0.062]\ \text{cm}^{-1}$.

### B. Olivero-Longbothum Pseudo-Voigt Profile Synthesis
Combining Gaussian instrument width $f_G = \text{FWHM}_{\text{eff}}$ and collisional Lorentzian width $f_L = \text{FWHM}_{\text{coll}}$:
$$f_V \approx 0.5346 f_L + \sqrt{0.2166 f_L^2 + f_G^2}$$
$$\eta \approx 1.36603\left(\frac{f_L}{f_V}\right) - 0.47719\left(\frac{f_L}{f_V}\right)^2 + 0.11116\left(\frac{f_L}{f_V}\right)^3$$
$$V(x; f_V) = \eta \cdot L(x; f_V) + (1 - \eta) \cdot G(x; f_V)$$
Where $L(x)$ and $G(x)$ are area-normalized Lorentzian and Gaussian profiles:
$$L(x; f_V) = \frac{1}{\pi} \frac{f_V/2}{x^2 + (f_V/2)^2}, \quad G(x; f_V) = \frac{\sqrt{4\ln 2}}{\sqrt{\pi} f_V} \exp\left(-\frac{4\ln 2 \cdot x^2}{f_V^2}\right)$$
- **Integral Conservation**: $\int_{-\infty}^{+\infty} V(x) dx = 1$ strictly holds.
- **Lorentzian Skirt Effect**: Captures $1/x^2$ power-law skirts critical for evaluating adjacent narrow-band interference filter leakage in pure rotational Raman lidars.

---

## 7. Atmospheric Lidar Retrieval Formulations

### A. Water Vapor Mixing Ratio Inversion
$$w(z) = C_{\text{sys}} \cdot \frac{P_{\text{H}_2\text{O}}(z)}{P_{\text{N}_2}(z)} \cdot \frac{\sigma_{\text{N}_2}}{\sigma_{\text{H}_2\text{O}}} \cdot \exp\left[\int_0^z \left(\alpha(\lambda_{\text{H}_2\text{O}}, z') - \alpha(\lambda_{\text{N}_2}, z')\right) dz'\right]$$
Theoretical cross-section ratio:
$$\frac{\sigma_{\text{N}_2}}{\sigma_{\text{H}_2\text{O}}} \approx \frac{3.8 \times 10^{-31}}{9.5 \times 10^{-31}} \approx 0.40$$

### B. Pure Rotational Raman Temperature Profiling Ratio
Using two narrow filter passbands extracting low-$J$ ($J_{\text{low}}$) and high-$J$ ($J_{\text{high}}$) transitions:
$$R(T) = \frac{I_1(T)}{I_2(T)} = \exp\left(\frac{a}{T} + b\right)$$
Where constants $a$ and $b$ are derived from differential Boltzmann population ratios.

---

## 8. Common Pitfalls & Best Practices

1. **Slit Width vs. Spectral Resolution**: Never conflate spectrometer mechanical slit physical width (in $\mu\text{m}$) directly with spectral resolution ($\text{nm}$ or $\text{cm}^{-1}$). Resolution requires knowing collimator focal length and grating dispersion. Specify FWHM directly.
2. **Lorentzian Skirt Truncation**: When computing filter leakage, do not truncate Voigt integration at $3\sigma$ (Gaussian cutoff). Set cutoff radius to $\ge 20 \gamma_V$ to retain $1/x^2$ skirts.
3. **State Machine Defaults**: In scientific simulation tools, always default laser linewidth and pressure broadening toggles to **OFF** (`Default-Off Policy`) to maintain a clean theoretical Dirac-$\delta$ baseline until deliberately enabled.
4. **Dual-Engine Equivalence**: When deploying both Python CLI/library and browser-based JavaScript interfaces, run automated regression tests to verify that transition line positions, cross sections, and Voigt profiles match to within IEEE 754 float64 machine epsilon ($< 1.4 \times 10^{-17}$).

---

## 9. Key References & DOIs

1. Dunham, J. L. (1932). The Energy Levels of a Rotating Vibrator. *Phys. Rev.*, 41(6), 721. DOI: [10.1103/PhysRev.41.721](https://doi.org/10.1103/PhysRev.41.721)
2. Placzek, G., & Teller, E. (1933). Die Rotationsstruktur der Ramanbanden mehratomiger Moleküle. *Z. Phys.*, 81, 209. DOI: [10.1007/BF01338364](https://doi.org/10.1007/BF01338364)
3. Penney, C. M., et al. (1972). Raman scattering, cross sections, and depolarization ratios for gases. *Nature Phys. Sci.*, 235, 110. DOI: [10.1038/physci235110a0](https://doi.org/10.1038/physci235110a0)
4. Olivero, J. J., & Longbothum, R. L. (1977). Empirical fits to the Voigt line width. *JQSRT*, 17(2), 233. DOI: [10.1016/0022-4073(77)90161-3](https://doi.org/10.1016/0022-4073(77)90161-3)
5. Behrendt, A., & Reichardt, J. (2000). Atmospheric temperature profiling with a pure rotational Raman lidar. *Appl. Opt.*, 39(9), 1372. DOI: [10.1364/AO.39.001372](https://doi.org/10.1364/AO.39.001372)
6. Whiteman, D. N. (2003). Examination of the traditional Raman lidar technique. I. *Appl. Opt.*, 42(15), 2571. DOI: [10.1364/AO.42.002571](https://doi.org/10.1364/AO.42.002571)
7. Gordon, I. E., et al. (2022). The HITRAN2020 molecular spectroscopic database. *JQSRT*, 277, 107949. DOI: [10.1016/j.jqsrt.2021.107949](https://doi.org/10.1016/j.jqsrt.2021.107949)
8. Radke, C. D., & Behrendt, A. (2023). Rotational Raman lidar temperature measurements: Line broadening by air pressure. *AMT*, 16, 3121. DOI: [10.5194/amt-16-3121-2023](https://doi.org/10.5194/amt-16-3121-2023)
