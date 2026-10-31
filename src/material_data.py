import math

import pandas as pd


REQUIRED_COLUMNS = {
    "material",
    "unit",
    "emission_factor",
    "unit_cost",
}


def validate_materials(materials: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize material database records."""

    result = materials.copy()

    missing_columns = REQUIRED_COLUMNS - set(result.columns)
    if missing_columns:
        raise ValueError(
            "Materials CSV is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if result.empty:
        raise ValueError("No material data found in materials.csv.")

    result["material"] = result["material"].astype("string").str.strip()
    result["unit"] = result["unit"].astype("string").str.strip()

    if result["material"].isna().any() or result["material"].eq("").any():
        raise ValueError("Material names cannot be empty.")

    if result["unit"].isna().any() or result["unit"].eq("").any():
        raise ValueError("Material units cannot be empty.")

    if result["material"].duplicated().any():
        raise ValueError("Each material must have a unique name.")

    for column in ["emission_factor", "unit_cost"]:
        try:
            result[column] = pd.to_numeric(result[column], errors="raise")
        except (ValueError, TypeError):
            raise ValueError(
                f"{column} must contain valid numeric values."
            ) from None

        finite_values = result[column].map(
            lambda value: pd.notna(value) and math.isfinite(value)
        )

        if not finite_values.all():
            raise ValueError(
                f"{column} must contain only finite numeric values."
            )

        if (result[column] < 0).any():
            raise ValueError(f"{column} cannot contain negative values.")

    return result
