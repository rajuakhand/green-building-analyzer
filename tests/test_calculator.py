import pandas as pd
import pytest
from src.calculator import calculate_footprint, summarize_footprint

def test_calculate_footprint_success():
    data = pd.DataFrame({
        "material": ["Cement", "Sand"],
        "quantity": [100.0, 200.0],
        "unit_cost": [10.0, 5.0],
        "emission_factor": [0.76, 0.01]
    })
    result = calculate_footprint(data)
    assert "estimated_cost" in result.columns
    assert "carbon_kg_co2e" in result.columns
    assert result.loc[result["material"] == "Cement", "estimated_cost"].values[0] == 1000.0
    assert result.loc[result["material"] == "Cement", "carbon_kg_co2e"].values[0] == 76.0

def test_summarize_footprint():
    data = pd.DataFrame({
        "estimated_cost": [1000.0, 500.0],
        "carbon_kg_co2e": [76.0, 2.0]
    })
    summary = summarize_footprint(data)
    assert summary["total_cost"] == 1500.0
    assert summary["total_carbon_kg"] == 78.0

def test_calculate_footprint_negative_value():
    import pytest
    data = pd.DataFrame({
        "material": ["Cement"],
        "quantity": [-10.0],
        "unit_cost": [10.0],
        "emission_factor": [0.76]
    })
    with pytest.raises(ValueError):
        calculate_footprint(data)
