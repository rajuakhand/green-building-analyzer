
import pandas as pd


def calculate_footprint(materials: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate estimated embodied carbon and material cost.

    Required columns:
    material, quantity, unit_cost, emission_factor
    """
    required = {
        "material",
        "quantity",
        "unit_cost",
        "emission_factor",
    }

    missing = required - set(materials.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")

    result = materials.copy()

    for column in ["quantity", "unit_cost", "emission_factor"]:
        result[column] = pd.to_numeric(result[column], errors="raise")

    if (result["quantity"] < 0).any():
        raise ValueError("Quantity cannot be negative.")

    if (result["unit_cost"] < 0).any():
        raise ValueError("Unit cost cannot be negative.")

    if (result["emission_factor"] < 0).any():
        raise ValueError("Emission factor cannot be negative.")

    result["estimated_cost"] = (
        result["quantity"] * result["unit_cost"]
    )

    result["carbon_kg_co2e"] = (
        result["quantity"] * result["emission_factor"]
    )

    return result


def summarize_footprint(result: pd.DataFrame) -> dict:
    return {
        "total_cost": float(result["estimated_cost"].sum()),
        "total_carbon_kg": float(result["carbon_kg_co2e"].sum()),
    }

