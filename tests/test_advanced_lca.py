import pytest

from src.advanced_lca import calculate_lca


def test_calculate_lca_success():
    result = calculate_lca(
        embodied_carbon_kg=1000,
        transport_tonnes=2,
        transport_distance_km=50,
        transport_factor_kg_per_tonne_km=0.1,
        annual_energy_kwh=1000,
        building_lifetime_years=10,
        electricity_factor_kg_per_kwh=0.5,
        end_of_life_carbon_kg=100,
    )

    assert result["breakdown"]["Transport carbon (kg CO2e)"] == 10
    assert result["breakdown"]["Operational energy carbon (kg CO2e)"] == 5000
    assert result["total_lifecycle_carbon_kg"] == 6110


def test_lca_rejects_negative_inputs():
    with pytest.raises(ValueError):
        calculate_lca(
            embodied_carbon_kg=-1,
            transport_tonnes=0,
            transport_distance_km=0,
            transport_factor_kg_per_tonne_km=0,
            annual_energy_kwh=0,
            building_lifetime_years=1,
            electricity_factor_kg_per_kwh=0,
        )


def test_lca_rejects_zero_building_lifetime():
    with pytest.raises(ValueError):
        calculate_lca(
            embodied_carbon_kg=0,
            transport_tonnes=0,
            transport_distance_km=0,
            transport_factor_kg_per_tonne_km=0,
            annual_energy_kwh=0,
            building_lifetime_years=0,
            electricity_factor_kg_per_kwh=0,
        )


def test_lca_zero_inputs_give_zero_total():
    result = calculate_lca(
        embodied_carbon_kg=0,
        transport_tonnes=0,
        transport_distance_km=0,
        transport_factor_kg_per_tonne_km=0,
        annual_energy_kwh=0,
        building_lifetime_years=50,
        electricity_factor_kg_per_kwh=0,
    )

    assert result["total_lifecycle_carbon_kg"] == 0
