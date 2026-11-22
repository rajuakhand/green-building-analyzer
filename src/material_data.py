import math
from pathlib import Path
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
def load_material_factors(path: str | Path) -> pd.DataFrame:
    """Load and perform structural validation for the research material-factor catalogue."""
    required_columns = {
        "material_id",
        "broad_category",
        "material",
        "gwp_cf",
        "gwp_unit",
        "energy_cf",
        "energy_unit",
        "boundary",
        "geography",
        "verification_status",
        "source_tables",
    }

    df = pd.read_csv(path)

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"Material factors file is missing columns: {', '.join(sorted(missing))}"
        )

    if df.empty:
        raise ValueError("Material factors file contains no records.")

    if df["material_id"].isna().any():
        raise ValueError("Material factors file contains missing material_id values.")

    if df["material_id"].duplicated().any():
        duplicates = df.loc[df["material_id"].duplicated(), "material_id"].tolist()
        raise ValueError(f"Duplicate material_id values found: {duplicates}")

    for column in ["gwp_cf", "energy_cf"]:
        df[column] = pd.to_numeric(df[column], errors="raise")

        if df[column].isna().any():
            raise ValueError(f"{column} contains missing values.")

        if not df[column].map(math.isfinite).all():
            raise ValueError(f"{column} contains non-finite values.")

        if (df[column] < 0).any():
            raise ValueError(f"{column} contains negative values.")

    if df["material"].isna().any():
        raise ValueError("Material factors file contains missing material names.")

    if df["source_tables"].isna().any():
        raise ValueError("Material factors file contains missing source references.")

    return df