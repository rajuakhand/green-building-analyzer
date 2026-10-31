import pandas as pd
import pytest

from src.material_data import validate_materials


def valid_materials():
    return pd.DataFrame({
        "material": ["Concrete", "Steel"],
        "unit": ["kg", "kg"],
        "emission_factor": [0.13, 1.5],
        "unit_cost": [5.0, 10.0],
        "source": ["Verified source", "Verified source"],
    })


def test_valid_materials_accepted():
    result = validate_materials(valid_materials())

    assert len(result) == 2
    assert result["emission_factor"].tolist() == [0.13, 1.5]


@pytest.mark.parametrize(
    "column",
    ["emission_factor", "unit_cost"],
)
@pytest.mark.parametrize(
    "value",
    [float("nan"), float("inf"), float("-inf"), -1],
)
def test_invalid_numeric_values_rejected(column, value):
    materials = valid_materials()
    materials.loc[0, column] = value

    with pytest.raises(ValueError):
        validate_materials(materials)

def test_non_numeric_values_rejected():
    materials = valid_materials()
    materials["emission_factor"] = materials["emission_factor"].astype(object)
    materials.loc[0, "emission_factor"] = "unknown"

    with pytest.raises(ValueError, match="valid numeric values"):
        validate_materials(materials)


def test_empty_material_name_rejected():
    materials = valid_materials()
    materials.loc[0, "material"] = " "

    with pytest.raises(ValueError, match="Material names cannot be empty"):
        validate_materials(materials)


def test_duplicate_material_rejected():
    materials = valid_materials()
    materials.loc[1, "material"] = "Concrete"

    with pytest.raises(ValueError, match="unique name"):
        validate_materials(materials)


def test_missing_required_column_rejected():
    materials = valid_materials().drop(columns=["unit"])

    with pytest.raises(ValueError, match="missing required columns"):
        validate_materials(materials)


def test_empty_dataframe_rejected():
    materials = valid_materials().iloc[0:0]

    with pytest.raises(ValueError, match="No material data"):
        validate_materials(materials)
