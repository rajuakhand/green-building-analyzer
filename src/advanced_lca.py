"""Transparent, input-driven life-cycle carbon calculations."""

from numbers import Real

import pandas as pd


def calculate_lca(
    embodied_carbon_kg: float,
    transport_tonnes: float,
    transport_distance_km: float,
    transport_factor_kg_per_tonne_km: float,
    annual_energy_kwh: float,
    building_lifetime_years: int,
    electricity_factor_kg_per_kwh: float,
    end_of_life_carbon_kg: float = 0.0,
) -> dict:
    """
    Calculate a preliminary life-cycle carbon estimate.

    All emission factors must use the units documented in the argument names.
    Transport mass is entered in tonnes explicitly to avoid assuming that
    every material quantity in the existing dataset uses kilograms.
    End-of-life emissions are a user-provided estimate, not an assumed factor.
    """

    values = {
        "embodied_carbon_kg": embodied_carbon_kg,
        "transport_tonnes": transport_tonnes,
        "transport_distance_km": transport_distance_km,
        "transport_factor_kg_per_tonne_km": (
            transport_factor_kg_per_tonne_km
        ),
        "annual_energy_kwh": annual_energy_kwh,
        "electricity_factor_kg_per_kwh": electricity_factor_kg_per_kwh,
        "end_of_life_carbon_kg": end_of_life_carbon_kg,
    }

    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"{name} must be a numeric value.")
        if not pd.notna(value) or value < 0:
            raise ValueError(f"{name} must be a finite, non-negative value.")
        if value == float("inf") or value == float("-inf"):
            raise ValueError(f"{name} must be finite.")

    if (
        isinstance(building_lifetime_years, bool)
        or not isinstance(building_lifetime_years, int)
        or building_lifetime_years <= 0
    ):
        raise ValueError("Building lifetime must be a positive whole number.")

    transport_carbon = (
        transport_tonnes
        * transport_distance_km
        * transport_factor_kg_per_tonne_km
    )

    operational_carbon = (
        annual_energy_kwh
        * building_lifetime_years
        * electricity_factor_kg_per_kwh
    )

    total_carbon = (
        embodied_carbon_kg
        + transport_carbon
        + operational_carbon
        + end_of_life_carbon_kg
    )

    breakdown = {
        "Embodied carbon (kg CO2e)": float(embodied_carbon_kg),
        "Transport carbon (kg CO2e)": float(transport_carbon),
        "Operational energy carbon (kg CO2e)": float(operational_carbon),
        "End-of-life carbon (kg CO2e)": float(end_of_life_carbon_kg),
    }

    return {
        "breakdown": breakdown,
        "total_lifecycle_carbon_kg": float(total_carbon),
        "building_lifetime_years": building_lifetime_years,
    }
