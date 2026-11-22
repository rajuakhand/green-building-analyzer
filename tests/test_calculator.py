import pandas as pd
import pytest
from src.calculator import (
    calculate_footprint,
    summarize_footprint,
    calculate_research_footprint,
    summarize_research_footprint,
)

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

@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("quantity", float("nan")),
        ("quantity", float("inf")),
        ("quantity", float("-inf")),
        ("unit_cost", float("nan")),
        ("unit_cost", float("inf")),
        ("unit_cost", float("-inf")),
        ("emission_factor", float("nan")),
        ("emission_factor", float("inf")),
        ("emission_factor", float("-inf")),
    ],
)
def test_non_finite_values_rejected(column, value):
    materials = pd.DataFrame({
        "material": ["Concrete"],
        "quantity": [10],
        "unit_cost": [5],
        "emission_factor": [0.76],
    })

    materials[column] = value

    with pytest.raises(ValueError, match="finite numeric values"):
        calculate_footprint(materials)
def test_unit_mismatch_rejected():
    df = pd.DataFrame({
        "material": ["Bricks"],
        "quantity": [2],
        "unit_cost": [10],
        "emission_factor": [1120],
        "quantity_unit": ["nos"],
        "gwp_unit": ["kg CO2e/1000 nos"],
    })
    with pytest.raises(ValueError, match="Unit mismatch"):
        calculate_footprint(df)


def test_unit_match_passes():
    df = pd.DataFrame({
        "material": ["Bricks"],
        "quantity": [2],
        "unit_cost": [10],
        "emission_factor": [1120],
        "quantity_unit": ["1000 nos"],
        "gwp_unit": ["kg CO2e/1000 nos"],
    })
    result = calculate_footprint(df)
    assert result["carbon_kg_co2e"].iloc[0] == 2240


def test_energy_calculated_separately():
    df = pd.DataFrame({
        "material": ["Cement"],
        "quantity": [1],
        "unit_cost": [100],
        "emission_factor": [910],
        "energy_factor": [6400],
    })
    result = calculate_footprint(df)
    assert result["energy_mj"].iloc[0] == 6400
    assert result["carbon_kg_co2e"].iloc[0] == 910
def test_energy_unit_mismatch_rejected():
    df = pd.DataFrame({
        "material": ["Cement"],
        "quantity": [1],
        "unit_cost": [100],
        "emission_factor": [910],
        "quantity_unit": ["tonne"],
        "gwp_unit": ["kg CO2e/tonne"],
        "energy_factor": [6400],
        "energy_unit": ["MJ/kg"],
    })

    with pytest.raises(ValueError, match="Energy unit mismatch"):
        calculate_footprint(df)


def test_partial_gwp_units_rejected():
    df = pd.DataFrame({
        "material": ["Bricks"],
        "quantity": [2],
        "unit_cost": [10],
        "emission_factor": [1120],
        "quantity_unit": ["1000 nos"],
    })

    with pytest.raises(
        ValueError,
        match="Both quantity_unit and gwp_unit"
    ):
        calculate_footprint(df)
        from src.calculator import (
    calculate_research_footprint,
    summarize_research_footprint,
)


def research_test_data():
    return pd.DataFrame({
        "material_id": ["MAT-002"],
        "material": ["Portland cement"],
        "quantity": [10.0],
        "quantity_unit": ["tonne"],
        "gwp_cf": [910.0],
        "gwp_unit": ["kg CO2e/tonne"],
        "energy_cf": [6400.0],
        "energy_unit": ["MJ/tonne"],
        "boundary": ["Cradle-to-gate"],
        "geography": ["India"],
        "verification_status": ["Verified-from-paper-SI"],
    })


def test_research_calculation_for_portland_cement():
    result = calculate_research_footprint(research_test_data())

    assert result.loc[0, "carbon_kg_co2e"] == 9100.0
    assert result.loc[0, "energy_mj"] == 64000.0


def test_research_summary():
    result = calculate_research_footprint(research_test_data())
    summary = summarize_research_footprint(result)

    assert summary["total_carbon_kg_co2e"] == 9100.0
    assert summary["total_energy_mj"] == 64000.0
    assert summary["boundary"] == "Cradle-to-gate"
    assert summary["geography"] == "India"
    assert summary["material_count"] == 1


def test_research_gwp_unit_mismatch_rejected():
    data = research_test_data()
    data.loc[0, "quantity_unit"] = "kg"

    with pytest.raises(ValueError, match="GWP unit mismatch"):
        calculate_research_footprint(data)


def test_research_energy_unit_mismatch_rejected():
    data = research_test_data()
    data.loc[0, "energy_unit"] = "MJ/kg"

    with pytest.raises(ValueError, match="Energy unit mismatch"):
        calculate_research_footprint(data)


def test_research_negative_quantity_rejected():
    data = research_test_data()
    data.loc[0, "quantity"] = -1

    with pytest.raises(ValueError, match="quantity cannot"):
        calculate_research_footprint(data)


def test_research_non_finite_factor_rejected():
    data = research_test_data()
    data.loc[0, "gwp_cf"] = float("inf")

    with pytest.raises(ValueError, match="finite numeric values"):
        calculate_research_footprint(data)


def test_research_empty_input_rejected():
    data = research_test_data().iloc[0:0]

    with pytest.raises(ValueError, match="Select at least one"):
        calculate_research_footprint(data)


def test_research_different_boundaries_cannot_be_summarized():
    data = research_test_data()
    second = research_test_data()
    second.loc[0, "material_id"] = "MAT-003"
    second.loc[0, "material"] = "Test material"
    second.loc[0, "boundary"] = "Use-stage"

    combined = pd.concat([data, second], ignore_index=True)
    result = calculate_research_footprint(combined)

    with pytest.raises(ValueError, match="different boundary"):
        summarize_research_footprint(result)