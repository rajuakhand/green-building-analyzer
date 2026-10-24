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


def test_zero_quantity_and_zero_factors():
    materials = pd.DataFrame({
        "material": ["Concrete"],
        "quantity": [0],
        "unit_cost": [0],
        "emission_factor": [0],
    })

    result = calculate_footprint(materials)
    summary = summarize_footprint(result)

    assert result.loc[0, "estimated_cost"] == 0
    assert result.loc[0, "carbon_kg_co2e"] == 0
    assert summary["total_cost"] == 0
    assert summary["total_carbon_kg"] == 0


def test_multiple_materials_total():
    materials = pd.DataFrame({
        "material": ["Concrete", "Steel"],
        "quantity": [100, 20],
        "unit_cost": [5, 10],
        "emission_factor": [0.76, 1.5],
    })

    result = calculate_footprint(materials)
    summary = summarize_footprint(result)

    assert result["estimated_cost"].tolist() == [500, 200]
    assert result["carbon_kg_co2e"].tolist() == [76, 30]
    assert summary["total_cost"] == 700
    assert summary["total_carbon_kg"] == 106


@pytest.mark.parametrize(
    ("column", "value", "error"),
    [
        ("quantity", -1, "Quantity cannot be negative."),
        ("unit_cost", -1, "Unit cost cannot be negative."),
        ("emission_factor", -1, "Emission factor cannot be negative."),
    ],
)
def test_negative_values_rejected(column, value, error):
    materials = pd.DataFrame({
        "material": ["Concrete"],
        "quantity": [10],
        "unit_cost": [5],
        "emission_factor": [0.76],
    })
    materials[column] = value

    with pytest.raises(ValueError, match=error):
        calculate_footprint(materials)


def test_missing_required_column_rejected():
    materials = pd.DataFrame({
        "material": ["Concrete"],
        "quantity": [10],
        "unit_cost": [5],
    })

    with pytest.raises(ValueError, match="emission_factor"):
        calculate_footprint(materials)


def test_non_numeric_quantity_rejected():
    materials = pd.DataFrame({
        "material": ["Concrete"],
        "quantity": ["not-a-number"],
        "unit_cost": [5],
        "emission_factor": [0.76],
    })

    with pytest.raises((ValueError, TypeError)):
        calculate_footprint(materials)


def test_numeric_strings_are_converted():
    materials = pd.DataFrame({
        "material": ["Concrete"],
        "quantity": ["10"],
        "unit_cost": ["5"],
        "emission_factor": ["0.76"],
    })

    result = calculate_footprint(materials)

    assert result.loc[0, "estimated_cost"] == 50
    assert result.loc[0, "carbon_kg_co2e"] == pytest.approx(7.6)
