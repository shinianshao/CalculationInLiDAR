#!/usr/bin/env python3
"""
raman_gas_physics.py
=============================================================================
High-Precision Quantum Mechanical & Spectroscopic Engine for Raman Scattering
of Diatomic Nitrogen (N2) and Oxygen (O2) and Standard Air Mixtures.

Physical Modeling Capabilities:
1. Pure Rotational Raman (Stokes S-branch Delta J=+2, Anti-Stokes O-branch Delta J=-2).
2. Vibrational Fundamental Raman (v=0 -> 1: Q, O, S branches).
3. Hot Bands (v=1 -> 2: Q, O, S branches, thermal population dependent).
4. First Overtones (v=0 -> 2: Q, O, S branches, anharmonicity scaled).
5. Arbitrary Excitation Wavelength (200 - 2000 nm) with (nu_0 - Delta_nu)^4 scaling.
6. Nuclear Spin Statistics & Parity:
   - 14N2 (I=1, 1Sigma_g+): g_even:g_odd = 6:3 = 2:1.
   - 16O2 (I=0, 3Sigma_g-): Bose symmetry forbids even J, strictly odd J=1,3,5...
7. Boltzmann Population at arbitrary Temperature (50 K - 3000 K).
8. Polarization Resolution: Total, Parallel (I_parallel), Perpendicular (I_perp),
   and Depolarization Ratio (rho).
9. Standard Air Synthesis (78.084% N2 + 20.946% O2).
10. Instrument Line Shape (ILS) Convolution (Gaussian & Lorentzian).
=============================================================================
"""

import numpy as np

# Physical Constants (CODATA 2018 / NIST)
H_PLANCK = 6.62607015e-34    # J*s
C_LIGHT = 2.99792458e8       # m/s
C_LIGHT_CM = 2.99792458e10   # cm/s
K_BOLTZMANN = 1.380649e-23   # J/K
HC_OVER_K = (H_PLANCK * C_LIGHT_CM) / K_BOLTZMANN  # ~ 1.438777 cm*K

# Molecular Spectroscopic Constants
# Source: NIST Chemistry WebBook, Herzberg, and Long "The Raman Effect"
MOLECULAR_DATA = {
    "N2": {
        "name": "Nitrogen (N2)",
        "formula": "N₂",
        "nuclear_spin": 1.0,           # 14N has I = 1 (Boson)
        "electronic_state": "X 1Sigma_g+",
        "omega_e": 2358.57,            # cm^-1
        "omega_e_xe": 14.324,          # cm^-1
        "B_e": 1.99824,                # cm^-1
        "alpha_e": 0.01732,            # cm^-1
        "D_e": 5.76e-6,                # cm^-1
        # Polarizability parameters
        "gamma_squared": 0.50e-48,     # cm^6 (anisotropy gamma^2 at 532 nm)
        "sigma_vib_ref_532": 3.8e-31,  # cm^2/sr for Q-branch fundamental at 532 nm
        "vib_shift_fundamental": 2330.7, # cm^-1
        "rho_Q_fundamental": 0.035,    # Q-branch depolarization ratio
        "natural_abundance_air": 0.78084
    },
    "O2": {
        "name": "Oxygen (O2)",
        "formula": "O₂",
        "nuclear_spin": 0.0,           # 16O has I = 0 (Boson)
        "electronic_state": "X 3Sigma_g-",
        "omega_e": 1580.19,            # cm^-1
        "omega_e_xe": 11.98,           # cm^-1
        "B_e": 1.44563,                # cm^-1
        "alpha_e": 0.0158,             # cm^-1
        "D_e": 4.88e-6,                # cm^-1
        # Polarizability parameters
        "gamma_squared": 1.25e-48,     # cm^6
        "sigma_vib_ref_532": 5.1e-31,  # cm^2/sr for Q-branch fundamental at 532 nm
        "vib_shift_fundamental": 1555.6, # cm^-1
        "rho_Q_fundamental": 0.065,    # Q-branch depolarization ratio
        "natural_abundance_air": 0.20946
    },
    "H2O": {
        "name": "Water Vapor (H2O)",
        "formula": "H₂O",
        "nuclear_spin": 0.5,           # Two 1H nuclei (I=1/2), Ortho:Para = 3:1
        "electronic_state": "X 1A1",
        "omega_e": 3657.05,            # cm^-1 (nu_1 symmetric stretch)
        "omega_e_xe": 43.8,            # cm^-1
        "omega_e_nu2": 1594.75,        # cm^-1 (nu_2 bending mode)
        "B_e": 14.52,                  # cm^-1 (effective rotational constant)
        "alpha_e": 0.12,               # cm^-1
        "D_e": 3.2e-4,                 # cm^-1
        # Polarizability parameters
        "gamma_squared": 0.10e-48,     # cm^6
        "sigma_vib_ref_532": 9.5e-31,  # cm^2/sr for nu_1 band at 532 nm (~2.5x N2)
        "sigma_nu2_ref_532": 0.38e-31, # cm^2/sr for nu_2 bending band at 532 nm
        "vib_shift_fundamental": 3657.05, # cm^-1
        "rho_Q_fundamental": 0.05,     # nu_1 Q-branch depolarization ratio
        "natural_abundance_air": 0.010 # Standard boundary layer humid air ~ 1% vol (10,000 ppmv)
    }
}


def compute_collisional_broadening_hwhm(molecule: str, J: int,
                                        pressure_atm: float = 1.0,
                                        temperature_k: float = 296.0) -> float:
    """
    Computes collisional pressure broadening half-width at half-maximum (HWHM, cm^-1)
    for pure rotational Raman transitions using Scheme A (J-dependent empirical model).
    Based on Behrendt & Reichardt (2000) and HITRAN air-broadening parameters.
    """
    mol = molecule.upper()
    if "N2" in mol or "14N" in mol:
        # N2 J-dependent broadening (Behrendt & Reichardt 2000, Megie et al.)
        if J < 6.5:
            gamma_0 = 0.050 + 0.023 * (J / 6.5)
        else:
            gamma_0 = 0.020 + 0.053 * np.exp(-((J - 6.5) / 6.2)**2)
        gamma_0 = float(np.clip(gamma_0, 0.018, 0.075))
        n_temp = 0.70
    elif "O2" in mol or "16O" in mol:
        # O2 J-dependent broadening
        if J < 5.5:
            gamma_0 = 0.042 + 0.018 * (J / 5.5)
        else:
            gamma_0 = 0.018 + 0.042 * np.exp(-((J - 5.5) / 5.5)**2)
        gamma_0 = float(np.clip(gamma_0, 0.016, 0.062))
        n_temp = 0.75
    else:
        # H2O or others
        gamma_0 = 0.030 + 0.050 * np.exp(-J / 12.0)
        n_temp = 0.65

    # Scale with pressure and temperature: gamma(P, T) = gamma_0 * (P / P0) * (T0 / T)^n
    t_ratio = 296.0 / max(10.0, float(temperature_k))
    gamma = gamma_0 * max(0.0, float(pressure_atm)) * (t_ratio ** n_temp)
    return float(gamma)


def compute_voigt_fwhm_and_eta(f_G: float, f_L: float) -> tuple:
    """
    Computes total Voigt FWHM and mixing parameter eta using Olivero-Longbothum
    and Kielkopf/Thompson pseudo-Voigt expansion.
    - f_G: Gaussian FWHM
    - f_L: Lorentzian FWHM
    Returns: (f_V, eta) where V(x) = eta * L(x; f_V) + (1 - eta) * G(x; f_V)
    """
    if f_L <= 1e-12:
        return float(f_G), 0.0
    if f_G <= 1e-12:
        return float(f_L), 1.0
    f_V = 0.5346 * f_L + np.sqrt(0.2166 * f_L**2 + f_G**2)
    ratio = f_L / f_V
    eta = float(np.clip(1.36603 * ratio - 0.47719 * ratio**2 + 0.11116 * ratio**3, 0.0, 1.0))
    return float(f_V), eta


class RamanGasCalculator:
    def __init__(self, molecule: str = "N2", excitation_nm: float = 532.0,
                 temperature_k: float = 296.15, pressure_atm: float = 1.0):
        """
        molecule: 'N2' or 'O2'
        excitation_nm: Incident laser wavelength in nm
        temperature_k: Thermodynamic temperature in Kelvin
        pressure_atm: Atmospheric pressure in atm
        """
        if molecule not in MOLECULAR_DATA:
            raise ValueError(f"Molecule {molecule} not supported. Use 'N2', 'O2', or 'H2O'.")
        self.mol_key = molecule
        self.data = MOLECULAR_DATA[molecule]
        self.lambda_0_nm = float(excitation_nm)
        self.laser_wavenumber_cm = 1e7 / self.lambda_0_nm  # nu_0 in cm^-1
        self.T = max(1.0, float(temperature_k))
        self.P_atm = max(0.0, float(pressure_atm))

    def energy_level(self, v: int, J: int) -> float:
        """Computes rovibrational term value T(v, J) in cm^-1."""
        d = self.data
        G_v = d["omega_e"] * (v + 0.5) - d["omega_e_xe"] * (v + 0.5)**2
        B_v = d["B_e"] - d["alpha_e"] * (v + 0.5)
        D_v = d["D_e"]
        F_v = B_v * J * (J + 1) - D_v * (J * (J + 1))**2
        return G_v + F_v

    def nuclear_spin_weight(self, J: int) -> float:
        """
        Computes nuclear statistical weight g_J.
        N2 (14N, I=1): Even J: g_J = 6, Odd J: g_J = 3 (Ratio 2:1).
        O2 (16O, I=0, 3Sigma_g-): Even J forbidden (g_J = 0), Odd J allowed (g_J = 1).
        H2O (1H, I=1/2): Ortho (weight 3) and Para (weight 1).
        """
        if self.mol_key == "N2":
            return 6.0 if (J % 2 == 0) else 3.0
        elif self.mol_key == "O2":
            return 0.0 if (J % 2 == 0) else 1.0
        elif self.mol_key == "H2O":
            return 3.0 if (J % 2 != 0) else 1.0
        return 1.0

    def partition_function(self, v_max: int = 5, j_max: int = 90) -> float:
        """Computes total rovibrational partition function Q_tot(T)."""
        Q = 0.0
        E_00 = self.energy_level(0, 0) if self.mol_key in ("N2", "H2O") else self.energy_level(0, 1)

        for v in range(v_max + 1):
            for J in range(j_max + 1):
                g_J = self.nuclear_spin_weight(J)
                if g_J == 0:
                    continue
                E_vJ = self.energy_level(v, J) - E_00
                deg = (2 * J + 1) * g_J
                Q += deg * np.exp(-E_vJ * HC_OVER_K / self.T)
        return Q

    def boltzmann_population(self, v: int, J: int, Q_tot: float) -> float:
        """Calculates fraction of molecules in state (v, J)."""
        g_J = self.nuclear_spin_weight(J)
        if g_J == 0:
            return 0.0
        E_00 = self.energy_level(0, 0) if self.mol_key in ("N2", "H2O") else self.energy_level(0, 1)
        E_vJ = self.energy_level(v, J) - E_00
        deg = (2 * J + 1) * g_J
        return (deg * np.exp(-E_vJ * HC_OVER_K / self.T)) / Q_tot

    def apply_polarization(self, line: dict, pol_mode: str = "total") -> float:
        """
        Computes polarized cross-section component based on Placzek invariant theory:
        - Pure rotational and O/S branches are purely anisotropic (gamma^2):
          rho = 3/4 = 0.75.
          I_parallel = (4/7) * I_total
          I_perp     = (3/7) * I_total
        - Vibrational Q-branch:
          rho = rho_Q (typically ~0.035 for N2, ~0.065 for O2).
          I_parallel = (1 / (1 + rho_Q)) * I_total
          I_perp     = (rho_Q / (1 + rho_Q)) * I_total
        """
        sigma_tot = line["cross_section_cm2_sr"]
        branch = line.get("branch", "Q")

        if "depol_ratio" in line:
            rho = line["depol_ratio"]
        elif branch == "Q":
            rho = self.data["rho_Q_fundamental"]
        else:
            rho = 0.75  # Pure rotational or O/S branch depolarized line

        if pol_mode == "parallel":
            return sigma_tot / (1.0 + rho)
        elif pol_mode == "perpendicular":
            return (sigma_tot * rho) / (1.0 + rho)
        elif pol_mode == "depol_ratio":
            return rho
        else:
            return sigma_tot

    def compute_pure_rotational_lines(self, j_max: int = 50) -> list:
        """
        Computes pure rotational Raman transitions:
        - Stokes: S-branch (Delta J = +2)
        - Anti-Stokes: O-branch (Delta J = -2)
        """
        Q_tot = self.partition_function(v_max=4, j_max=80)
        lines = []
        d = self.data
        gamma2 = d["gamma_squared"]
        nu_0 = self.laser_wavenumber_cm
        const_factor = (64.0 * np.pi**4) / 45.0

        for J in range(j_max + 1):
            P_J = self.boltzmann_population(0, J, Q_tot)
            if P_J <= 1e-12:
                continue

            # 1. Stokes Transition: J -> J + 2 (S-branch)
            J_prime = J + 2
            if self.nuclear_spin_weight(J_prime) > 0:
                E_lower = self.energy_level(0, J)
                E_upper = self.energy_level(0, J_prime)
                delta_nu = E_upper - E_lower  # positive shift
                nu_s = nu_0 - delta_nu
                if nu_s > 0:
                    lambda_s_nm = 1e7 / nu_s
                    b_JJ = (3.0 * (J + 1) * (J + 2)) / (2.0 * (2 * J + 1) * (2 * J + 3))
                    dsigma = const_factor * (nu_s**4) * gamma2 * b_JJ * P_J

                    gamma_hwhm_cm = compute_collisional_broadening_hwhm(self.mol_key, J, self.P_atm, self.T)
                    fwhm_coll_cm = 2.0 * gamma_hwhm_cm
                    fwhm_coll_nm = fwhm_coll_cm * (lambda_s_nm**2) / 1e7

                    lines.append({
                        "molecule": self.data["formula"],
                        "type": "Pure Rotational",
                        "branch": "S",
                        "direction": "Stokes",
                        "v_lower": 0, "J_lower": J,
                        "v_upper": 0, "J_upper": J_prime,
                        "raman_shift_cm": float(delta_nu),
                        "scattered_wavenumber_cm": float(nu_s),
                        "wavelength_nm": float(lambda_s_nm),
                        "cross_section_cm2_sr": float(dsigma),
                        "relative_population": float(P_J),
                        "depol_ratio": 0.75,
                        "fwhm_coll_cm": float(fwhm_coll_cm),
                        "fwhm_coll_nm": float(fwhm_coll_nm),
                        "transition_label": f"{self.data['formula']} S({J})"
                    })

            # 2. Anti-Stokes Transition: J -> J - 2 (O-branch)
            if J >= 2:
                J_prime_as = J - 2
                if self.nuclear_spin_weight(J_prime_as) > 0:
                    E_lower_as = self.energy_level(0, J)
                    E_upper_as = self.energy_level(0, J_prime_as)
                    delta_nu_as = E_upper_as - E_lower_as  # negative shift
                    nu_as = nu_0 - delta_nu_as  # nu_0 + |delta_nu|
                    lambda_as_nm = 1e7 / nu_as
                    b_JJ_as = (3.0 * J * (J - 1)) / (2.0 * (2 * J + 1) * (2 * J - 1))
                    dsigma_as = const_factor * (nu_as**4) * gamma2 * b_JJ_as * P_J

                    gamma_hwhm_cm = compute_collisional_broadening_hwhm(self.mol_key, J, self.P_atm, self.T)
                    fwhm_coll_cm = 2.0 * gamma_hwhm_cm
                    fwhm_coll_nm = fwhm_coll_cm * (lambda_as_nm**2) / 1e7

                    lines.append({
                        "molecule": self.data["formula"],
                        "type": "Pure Rotational",
                        "branch": "O",
                        "direction": "Anti-Stokes",
                        "v_lower": 0, "J_lower": J,
                        "v_upper": 0, "J_upper": J_prime_as,
                        "raman_shift_cm": float(delta_nu_as),
                        "scattered_wavenumber_cm": float(nu_as),
                        "wavelength_nm": float(lambda_as_nm),
                        "cross_section_cm2_sr": float(dsigma_as),
                        "relative_population": float(P_J),
                        "depol_ratio": 0.75,
                        "fwhm_coll_cm": float(fwhm_coll_cm),
                        "fwhm_coll_nm": float(fwhm_coll_nm),
                        "transition_label": f"{self.data['formula']} O({J})"
                    })

        return lines

    def compute_vibrational_band(self, v_lower: int = 0, v_upper: int = 1,
                                 band_type_label: str = "Fundamental",
                                 j_max: int = 40) -> list:
        """
        Computes vibrational-rotational Raman transitions for any v_lower -> v_upper band:
        - Fundamental: v=0 -> 1
        - Hot band: v=1 -> 2
        - First overtone: v=0 -> 2
        """
        Q_tot = self.partition_function(v_max=4, j_max=80)
        lines = []
        d = self.data
        nu_0 = self.laser_wavenumber_cm

        # Vibrational cross section scaling:
        nu_ref_532 = 1e7 / 532.0
        delta_nu_vib_fund = d["vib_shift_fundamental"]
        cross_section_scale = ((nu_0 - delta_nu_vib_fund) / (nu_ref_532 - delta_nu_vib_fund))**4
        sigma_vib_base = d["sigma_vib_ref_532"] * cross_section_scale

        # Transition matrix element scaling factor:
        # Fundamental (0->1): factor = 1.0
        # Hot band (1->2): factor = 2.0 (scaled by matrix element (v+1)), but initial state population is P(1, J)
        # Overtone (0->2): suppressed by electrical/mechanical anharmonicity ~ (2*xe)^2 ~ 0.01
        if v_lower == 0 and v_upper == 1:
            band_factor = 1.0
        elif v_lower == 1 and v_upper == 2:
            band_factor = 2.0  # Matrix element |<2|q|1>|^2 = 2 * |<1|q|0>|^2
        elif v_lower == 0 and v_upper == 2:
            # First overtone anharmonicity suppression
            anharm_ratio = (2.0 * d["omega_e_xe"]) / d["omega_e"]
            band_factor = 0.5 * (anharm_ratio**2)  # ~ 0.005 - 0.015
        else:
            band_factor = 1.0

        for J in range(j_max + 1):
            P_vJ = self.boltzmann_population(v_lower, J, Q_tot)
            if P_vJ <= 1e-13:
                continue

            E_lower = self.energy_level(v_lower, J)

            # 1. Q-Branch (Delta J = 0)
            E_upper_Q = self.energy_level(v_upper, J)
            delta_nu_Q = E_upper_Q - E_lower
            nu_s_Q = nu_0 - delta_nu_Q
            if nu_s_Q > 0:
                lambda_s_Q = 1e7 / nu_s_Q
                # Q-branch fraction of the band is ~ 92%
                dsigma_Q = sigma_vib_base * band_factor * 0.92 * P_vJ

                lines.append({
                    "molecule": self.data["formula"],
                    "type": f"Vibrational ({band_type_label})",
                    "branch": "Q",
                    "direction": "Stokes",
                    "v_lower": v_lower, "J_lower": J,
                    "v_upper": v_upper, "J_upper": J,
                    "raman_shift_cm": float(delta_nu_Q),
                    "scattered_wavenumber_cm": float(nu_s_Q),
                    "wavelength_nm": float(lambda_s_Q),
                    "cross_section_cm2_sr": float(dsigma_Q),
                    "relative_population": float(P_vJ),
                    "depol_ratio": float(self.data["rho_Q_fundamental"]),
                    "transition_label": f"{self.data['formula']} {band_type_label[0]}Q({J})"
                })

            # 2. S-Branch (Delta J = +2)
            J_prime_S = J + 2
            if self.nuclear_spin_weight(J_prime_S) > 0:
                E_upper_S = self.energy_level(v_upper, J_prime_S)
                delta_nu_S = E_upper_S - E_lower
                nu_s_S = nu_0 - delta_nu_S
                if nu_s_S > 0:
                    lambda_s_S = 1e7 / nu_s_S
                    b_S = (3.0 * (J + 1) * (J + 2)) / (2.0 * (2 * J + 1) * (2 * J + 3))
                    dsigma_S = sigma_vib_base * band_factor * 0.04 * P_vJ * b_S

                    lines.append({
                        "molecule": self.data["formula"],
                        "type": f"Vibrational ({band_type_label})",
                        "branch": "S",
                        "direction": "Stokes",
                        "v_lower": v_lower, "J_lower": J,
                        "v_upper": v_upper, "J_upper": J_prime_S,
                        "raman_shift_cm": float(delta_nu_S),
                        "scattered_wavenumber_cm": float(nu_s_S),
                        "wavelength_nm": float(lambda_s_S),
                        "cross_section_cm2_sr": float(dsigma_S),
                        "relative_population": float(P_vJ),
                        "depol_ratio": 0.75,
                        "transition_label": f"{self.data['formula']} {band_type_label[0]}S({J})"
                    })

            # 3. O-Branch (Delta J = -2)
            if J >= 2:
                J_prime_O = J - 2
                if self.nuclear_spin_weight(J_prime_O) > 0:
                    E_upper_O = self.energy_level(v_upper, J_prime_O)
                    delta_nu_O = E_upper_O - E_lower
                    nu_s_O = nu_0 - delta_nu_O
                    if nu_s_O > 0:
                        lambda_s_O = 1e7 / nu_s_O
                        b_O = (3.0 * J * (J - 1)) / (2.0 * (2 * J + 1) * (2 * J - 1))
                        dsigma_O = sigma_vib_base * band_factor * 0.04 * P_vJ * b_O

                        lines.append({
                            "molecule": self.data["formula"],
                            "type": f"Vibrational ({band_type_label})",
                            "branch": "O",
                            "direction": "Stokes",
                            "v_lower": v_lower, "J_lower": J,
                            "v_upper": v_upper, "J_upper": J_prime_O,
                            "raman_shift_cm": float(delta_nu_O),
                            "scattered_wavenumber_cm": float(nu_s_O),
                            "wavelength_nm": float(lambda_s_O),
                            "cross_section_cm2_sr": float(dsigma_O),
                            "relative_population": float(P_vJ),
                            "depol_ratio": 0.75,
                            "transition_label": f"{self.data['formula']} {band_type_label[0]}O({J})"
                        })

        # For H2O: add nu_2 bending vibration (1594.8 cm^-1) during Fundamental mode
        if self.mol_key == "H2O" and band_type_label == "Fundamental":
            nu_2_shift = d["omega_e_nu2"]
            sigma_nu2 = d["sigma_nu2_ref_532"] * ((nu_0 - nu_2_shift) / (nu_ref_532 - nu_2_shift))**4
            for J in range(min(j_max, 25) + 1):
                P_vJ = self.boltzmann_population(0, J, Q_tot)
                if P_vJ <= 1e-13:
                    continue
                dnu_nu2 = nu_2_shift - d["alpha_e"] * J * (J + 1)
                nu_s_nu2 = nu_0 - dnu_nu2
                if nu_s_nu2 > 0:
                    lines.append({
                        "molecule": self.data["formula"],
                        "type": "Vibrational (Fundamental ν₂ Bending)",
                        "branch": "Q",
                        "direction": "Stokes",
                        "v_lower": 0, "J_lower": J,
                        "v_upper": 1, "J_upper": J,
                        "raman_shift_cm": float(dnu_nu2),
                        "scattered_wavenumber_cm": float(nu_s_nu2),
                        "wavelength_nm": float(1e7 / nu_s_nu2),
                        "cross_section_cm2_sr": float(sigma_nu2 * 0.90 * P_vJ),
                        "relative_population": float(P_vJ),
                        "depol_ratio": 0.08,
                        "transition_label": f"H₂O ν₂Q({J})"
                    })

        return lines

    def compute_all_transitions(self, include_pure_rot: bool = True,
                                include_fundamental: bool = True,
                                include_hot_bands: bool = False,
                                include_overtones: bool = False,
                                pol_mode: str = "total") -> list:
        """
        Aggregates selected transitions with polarization weighting applied.
        """
        all_lines = []
        if include_pure_rot:
            all_lines.extend(self.compute_pure_rotational_lines())
        if include_fundamental:
            all_lines.extend(self.compute_vibrational_band(v_lower=0, v_upper=1, band_type_label="Fundamental"))
        if include_hot_bands:
            all_lines.extend(self.compute_vibrational_band(v_lower=1, v_upper=2, band_type_label="Hot Band"))
        if include_overtones:
            all_lines.extend(self.compute_vibrational_band(v_lower=0, v_upper=2, band_type_label="Overtone"))

        # Apply polarization filter
        for line in all_lines:
            line["active_cross_section"] = self.apply_polarization(line, pol_mode)
            line["pol_mode"] = pol_mode

        return all_lines


def compute_air_spectrum(excitation_nm: float = 532.0, temperature_k: float = 296.15,
                         include_pure_rot: bool = True, include_fundamental: bool = True,
                         include_hot_bands: bool = False, include_overtones: bool = False,
                         pol_mode: str = "total", h2o_fraction: float = 0.01,
                         pressure_atm: float = 1.0) -> list:
    """
    Computes Air Raman spectrum with optional water vapor content and pressure broadening.
    h2o_fraction: Volume fraction of H2O (e.g. 0.01 for 1% humid air, 0.0 for dry air).
    pressure_atm: Atmospheric pressure in atm.
    """
    dry_scale = 1.0 - max(0.0, min(0.20, h2o_fraction))
    w_n2 = MOLECULAR_DATA["N2"]["natural_abundance_air"] * dry_scale
    w_o2 = MOLECULAR_DATA["O2"]["natural_abundance_air"] * dry_scale

    calc_n2 = RamanGasCalculator("N2", excitation_nm=excitation_nm, temperature_k=temperature_k,
                                pressure_atm=pressure_atm)
    lines_n2 = calc_n2.compute_all_transitions(include_pure_rot, include_fundamental,
                                               include_hot_bands, include_overtones, pol_mode)
    for l in lines_n2:
        l["cross_section_cm2_sr"] *= w_n2
        l["active_cross_section"] *= w_n2
        l["molecule_fraction"] = w_n2

    calc_o2 = RamanGasCalculator("O2", excitation_nm=excitation_nm, temperature_k=temperature_k,
                                pressure_atm=pressure_atm)
    lines_o2 = calc_o2.compute_all_transitions(include_pure_rot, include_fundamental,
                                               include_hot_bands, include_overtones, pol_mode)
    for l in lines_o2:
        l["cross_section_cm2_sr"] *= w_o2
        l["active_cross_section"] *= w_o2
        l["molecule_fraction"] = w_o2

    all_lines = lines_n2 + lines_o2

    if h2o_fraction > 0:
        w_h2o = h2o_fraction
        calc_h2o = RamanGasCalculator("H2O", excitation_nm=excitation_nm, temperature_k=temperature_k,
                                     pressure_atm=pressure_atm)
        lines_h2o = calc_h2o.compute_all_transitions(include_pure_rot, include_fundamental,
                                                     include_hot_bands, include_overtones, pol_mode)
        for l in lines_h2o:
            l["cross_section_cm2_sr"] *= w_h2o
            l["active_cross_section"] *= w_h2o
            l["molecule_fraction"] = w_h2o
        all_lines += lines_h2o

    return all_lines


def compute_effective_fwhm(inst_fwhm: float, laser_fwhm: float = 0.0,
                           enable_laser_conv: bool = False, profile: str = "gaussian") -> float:
    """
    Computes effective spectral FWHM from receiver instrument resolution and laser linewidth.
    - When enable_laser_conv is False: returns inst_fwhm directly (ideal monochromatic laser).
    - When enable_laser_conv is True:
      * For Gaussian profiles: combines in quadrature (Gaussian pulse line convolution):
        FWHM_eff = sqrt(FWHM_inst^2 + FWHM_laser^2)
      * For Lorentzian profiles: combines linearly (Cauchy distribution convolution theorem):
        FWHM_eff = FWHM_inst + FWHM_laser
    """
    if not enable_laser_conv or laser_fwhm <= 0.0:
        return float(inst_fwhm)
    if profile.lower() == "lorentzian":
        return float(inst_fwhm + laser_fwhm)
    return float(np.sqrt(inst_fwhm**2 + laser_fwhm**2))


def convolve_spectrum(lines: list, grid_x: np.ndarray, fwhm: float = 0.2,
                      laser_fwhm: float = 0.0, enable_laser_conv: bool = False,
                      enable_pressure_broadening: bool = False,
                      x_axis_mode: str = "wavelength", profile: str = "gaussian") -> np.ndarray:
    """
    Convolves stick spectrum with Instrument Line Shape (ILS), optional Laser pulse linewidth,
    and optional lower-atmosphere collisional pressure broadening (Voigt profile for pure rotational lines).
    - grid_x: Array of x values (wavelength in nm, or raman_shift in cm^-1).
    - fwhm: Receiver instrument spectral resolution / filter bandwidth FWHM.
    - laser_fwhm: Transmitter laser pulse linewidth FWHM (same unit).
    - enable_laser_conv: Toggle to enable/disable laser linewidth convolution.
    - enable_pressure_broadening: Toggle to enable/disable collisional pressure broadening on pure rotational lines.
    - x_axis_mode: 'wavelength' or 'raman_shift'.
    - profile: 'gaussian' or 'lorentzian'.
    Returns: continuous spectral intensity array.
    """
    eff_fwhm = compute_effective_fwhm(fwhm, laser_fwhm, enable_laser_conv, profile=profile)
    val_key = "wavelength_nm" if x_axis_mode == "wavelength" else "raman_shift_cm"
    fwhm_coll_key = "fwhm_coll_nm" if x_axis_mode == "wavelength" else "fwhm_coll_cm"
    continuous_spec = np.zeros_like(grid_x, dtype=np.float64)

    for line in lines:
        x_line = line[val_key]
        amp = line.get("active_cross_section", line["cross_section_cm2_sr"])
        is_pure_rot = (line.get("type") == "Pure Rotational")

        # Determine individual line broadening parameters
        if enable_pressure_broadening and is_pure_rot and (fwhm_coll_key in line) and line[fwhm_coll_key] > 0:
            f_L = line[fwhm_coll_key]
            if profile.lower() == "lorentzian":
                # Convolution of two Lorentzians is Lorentzian with f_tot = f_inst + f_L
                f_tot = eff_fwhm + f_L
                gamma = f_tot / 2.0
                cutoff = 20.0 * gamma
                norm = 1.0 / np.pi
                mask = (grid_x >= x_line - cutoff) & (grid_x <= x_line + cutoff)
                if np.any(mask):
                    diff = grid_x[mask] - x_line
                    continuous_spec[mask] += amp * (norm * gamma / (diff**2 + gamma**2))
            else:
                # Voigt synthesis: Gaussian instrument/laser (eff_fwhm) + Lorentzian collisional (f_L)
                f_V, eta = compute_voigt_fwhm_and_eta(eff_fwhm, f_L)
                sigma_v = f_V / (2.0 * np.sqrt(2.0 * np.log(2.0)))
                gamma_v = f_V / 2.0
                cutoff = max(4.0 * sigma_v, 20.0 * gamma_v)

                mask = (grid_x >= x_line - cutoff) & (grid_x <= x_line + cutoff)
                if np.any(mask):
                    diff = grid_x[mask] - x_line
                    norm_G = 1.0 / (sigma_v * np.sqrt(2.0 * np.pi))
                    y_G = norm_G * np.exp(-0.5 * (diff / sigma_v)**2)
                    norm_L = 1.0 / np.pi
                    y_L = (norm_L * gamma_v) / (diff**2 + gamma_v**2)
                    continuous_spec[mask] += amp * (eta * y_L + (1.0 - eta) * y_G)
        else:
            # Standard single/double convolution without pressure broadening
            if profile.lower() == "gaussian":
                sigma = eff_fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0)))
                cutoff = 4.0 * sigma
                norm = 1.0 / (sigma * np.sqrt(2.0 * np.pi))
                mask = (grid_x >= x_line - cutoff) & (grid_x <= x_line + cutoff)
                if np.any(mask):
                    diff = grid_x[mask] - x_line
                    continuous_spec[mask] += amp * norm * np.exp(-0.5 * (diff / sigma)**2)
            else:
                gamma = eff_fwhm / 2.0
                cutoff = 20.0 * gamma
                norm = 1.0 / np.pi
                mask = (grid_x >= x_line - cutoff) & (grid_x <= x_line + cutoff)
                if np.any(mask):
                    diff = grid_x[mask] - x_line
                    continuous_spec[mask] += amp * (norm * gamma / (diff**2 + gamma**2))

    return continuous_spec


if __name__ == "__main__":
    print("Testing physics calculation...")
    air_lines = compute_air_spectrum(excitation_nm=532.0, temperature_k=300.0,
                                     include_pure_rot=True, include_fundamental=True,
                                     include_hot_bands=True, include_overtones=True)
    print(f"Total lines in Air spectrum: {len(air_lines)}")
    # Print strongest line
    strongest = max(air_lines, key=lambda x: x["active_cross_section"])
    print(f"Strongest line: {strongest['transition_label']} at {strongest['wavelength_nm']:.3f} nm, "
          f"cross section = {strongest['active_cross_section']:.3e} cm^2/sr")
