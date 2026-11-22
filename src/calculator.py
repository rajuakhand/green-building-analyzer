
import math
import pandas as pd


def _get_denominator(factor_unit: str) -> str:
    """Extract denominator from a factor unit like 'kg CO2e/1000 nos'."""
    if "/" not in factor_unit:
        return factor_unit.strip()

    return factor_unit.split("/", 1)[1].strip()


def _units_match(quantity_unit: str, factor_unit: str) -> bool:
    """Check whether quantity unit matches factor denominator."""
    denominator = _get_denominator(factor_unit)

    return quantity_unit.strip().lower() == denominator.lower()


def _clean_unit(value) -> str:
    """Safely convert a unit value to a cleaned string."""
    if pd.isna(value):
        return ""

    return str(value).strip()


def calculate_footprint(materials: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate estimated material cost, embodied carbon and energy.

    Required columns:
        material, quantity, unit_cost, emission_factor

    Optional columns:
        quantity_unit, gwp_unit, energy_factor, energy_unit
    """

    required = {
        "material",
        "quantity",
        "unit_cost",
        "emission_factor",
    }

    missing = required - set(materials.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {', '.join(sorted(missing))}"
        )

    result = materials.copy()

    # Validate required numeric columns.
    for column in ["quantity", "unit_cost", "emission_factor"]:

        result[column] = pd.to_numeric(
            result[column],
            errors="raise"
        )

        if not result[column].map(
            lambda value: (
                pd.notna(value) and math.isfinite(value)
            )
        ).all():

            raise ValueError(
                f"{column} must contain only finite numeric values."
            )

    # Validate non-negative values.
    if (result["quantity"] < 0).any():
        raise ValueError("Quantity cannot be negative.")

    if (result["unit_cost"] < 0).any():
        raise ValueError("Unit cost cannot be negative.")

    if (result["emission_factor"] < 0).any():
        raise ValueError("Emission factor cannot be negative.")

    # --------------------------------------------------
    # GWP UNIT VALIDATION
    # --------------------------------------------------

    has_quantity_unit = "quantity_unit" in result.columns
    has_gwp_unit = "gwp_unit" in result.columns

    # Both columns must be provided together.
    if has_quantity_unit != has_gwp_unit:
        raise ValueError(
            "Both quantity_unit and gwp_unit columns "
            "must be provided together."
        )

    if has_quantity_unit and has_gwp_unit:

        for _, row in result.iterrows():

            q_unit = _clean_unit(row["quantity_unit"])
            g_unit = _clean_unit(row["gwp_unit"])

            if not q_unit or not g_unit:
                raise ValueError(
                    "Both quantity_unit and gwp_unit must be "
                    f"provided for material '{row['material']}'."
                )

            if not _units_match(q_unit, g_unit):
                raise ValueError(
                    f"Unit mismatch for material '{row['material']}': "
                    f"quantity unit '{q_unit}' does not match "
                    f"factor denominator "
                    f"'{_get_denominator(g_unit)}'."
                )

    # --------------------------------------------------
    # COST CALCULATION
    # --------------------------------------------------

    result["estimated_cost"] = (
        result["quantity"] * result["unit_cost"]
    )

    # --------------------------------------------------
    # GWP / CARBON CALCULATION
    # --------------------------------------------------

    result["carbon_kg_co2e"] = (
        result["quantity"] * result["emission_factor"]
    )

    # --------------------------------------------------
    # ENERGY CALCULATION AND VALIDATION
    # --------------------------------------------------

    if "energy_factor" in result.columns:

        result["energy_factor"] = pd.to_numeric(
            result["energy_factor"],
            errors="raise"
        )

        # Reject NaN and infinite energy factors.
        if not result["energy_factor"].map(
            lambda value: (
                pd.notna(value) and math.isfinite(value)
            )
        ).all():

            raise ValueError(
                "energy_factor must contain only finite numeric values."
            )

        # Reject negative energy factors.
        if (result["energy_factor"] < 0).any():
            raise ValueError(
                "energy_factor cannot be negative."
            )

        has_energy_unit = "energy_unit" in result.columns

        # If either unit column is supplied, both are required.
        if has_quantity_unit != has_energy_unit:
            raise ValueError(
                "Both quantity_unit and energy_unit must be "
                "provided together for energy unit validation."
            )

        if has_quantity_unit and has_energy_unit:

            for _, row in result.iterrows():

                q_unit = _clean_unit(row["quantity_unit"])
                e_unit = _clean_unit(row["energy_unit"])

                if not q_unit or not e_unit:
                    raise ValueError(
                        "Both quantity_unit and energy_unit must "
                        "be provided for material "
                        f"'{row['material']}'."
                    )

                if not _units_match(q_unit, e_unit):
                    raise ValueError(
                        f"Energy unit mismatch for material "
                        f"'{row['material']}': "
                        f"quantity unit '{q_unit}' does not match "
                        f"energy factor denominator "
                        f"'{_get_denominator(e_unit)}'."
                    )

        # Energy remains separate from carbon.
        result["energy_mj"] = (
            result["quantity"] * result["energy_factor"]
        )

    return result


def summarize_footprint(result: pd.DataFrame) -> dict:
    """Summarize total material cost, carbon and energy."""

    summary = {
        "total_cost": float(
            result["estimated_cost"].sum()
        ),
        "total_carbon_kg": float(
            result["carbon_kg_co2e"].sum()
        ),
    }

    if "energy_mj" in result.columns:

        summary["total_energy_mj"] = float(
            result["energy_mj"].sum()
        )

    return summary
def calculate_research_footprint(materials: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate GWP and energy from the research material-factor catalogue.

    Required columns:
        material_id, material, quantity, quantity_unit,
        gwp_cf, gwp_unit, energy_cf, energy_unit,
        boundary, geography, verification_status

    No material cost is calculated.
    No automatic unit conversion is performed.
    """

    required = {
        "material_id",
        "material",
        "quantity",
        "quantity_unit",
        "gwp_cf",
        "gwp_unit",
        "energy_cf",
        "energy_unit",
        "boundary",
        "geography",
        "verification_status",
    }

    missing = required - set(materials.columns)

    if missing:
        raise ValueError(
            f"Missing research calculation columns: "
            f"{', '.join(sorted(missing))}"
        )

    if materials.empty:
        raise ValueError("Select at least one research material.")

    result = materials.copy()

    # Validate numeric inputs.
    for column in ["quantity", "gwp_cf", "energy_cf"]:
        result[column] = pd.to_numeric(
            result[column],
            errors="raise",
        )

        if not result[column].map(
            lambda value: (
                pd.notna(value) and math.isfinite(value)
            )
        ).all():
            raise ValueError(
                f"{column} must contain only finite numeric values."
            )

        if (result[column] < 0).any():
            raise ValueError(
                f"{column} cannot contain negative values."
            )

    # Validate units and required text fields.
    for _, row in result.iterrows():
        material_name = str(row["material"])

        quantity_unit = _clean_unit(row["quantity_unit"])
        gwp_unit = _clean_unit(row["gwp_unit"])
        energy_unit = _clean_unit(row["energy_unit"])

        if not quantity_unit or not gwp_unit or not energy_unit:
            raise ValueError(
                f"Missing unit information for material '{material_name}'."
            )

        if not _units_match(quantity_unit, gwp_unit):
            raise ValueError(
                f"GWP unit mismatch for material '{material_name}': "
                f"quantity unit '{quantity_unit}' does not match "
                f"factor denominator '{_get_denominator(gwp_unit)}'."
            )

        if not _units_match(quantity_unit, energy_unit):
            raise ValueError(
                f"Energy unit mismatch for material '{material_name}': "
                f"quantity unit '{quantity_unit}' does not match "
                f"factor denominator '{_get_denominator(energy_unit)}'."
            )

        for column in [
            "material_id",
            "material",
            "boundary",
            "geography",
            "verification_status",
        ]:
            if not _clean_unit(row[column]):
                raise ValueError(
                    f"Missing {column} for material '{material_name}'."
                )

    # Calculate carbon and energy separately.
    result["carbon_kg_co2e"] = (
        result["quantity"] * result["gwp_cf"]
    )

    result["energy_mj"] = (
        result["quantity"] * result["energy_cf"]
    )

    return result


def summarize_research_footprint(result: pd.DataFrame) -> dict:
    """Summarize research GWP and energy without mixing boundaries."""

    if result.empty:
        raise ValueError("No research material results to summarize.")

    for column in ["boundary", "geography"]:
        if result[column].nunique(dropna=False) != 1:
            raise ValueError(
                f"Cannot combine research results with different "
                f"{column} values."
            )

    return {
        "total_carbon_kg_co2e": float(
            result["carbon_kg_co2e"].sum()
        ),
        "total_energy_mj": float(
            result["energy_mj"].sum()
        ),
        "boundary": str(result["boundary"].iloc[0]),
        "geography": str(result["geography"].iloc[0]),
        "material_count": int(len(result)),
    }