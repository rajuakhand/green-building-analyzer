
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.calculator import calculate_footprint, summarize_footprint
from src.ai_engine import get_ai_recommendations


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Green Building Analyzer",
    page_icon="🌱",
    layout="wide",
)

st.title("🌱 AI-Powered Smart Green Building Analyzer")
st.caption("Construction Material Cost & Carbon Footprint Analysis")


# --------------------------------------------------
# Load Material Data from CSV
# --------------------------------------------------

DATA_FILE = Path(__file__).resolve().parent / "data" / "materials.csv"

try:
    materials_df = pd.read_csv(DATA_FILE)

    required_columns = {
        "material",
        "unit",
        "emission_factor",
        "unit_cost",
    }

    missing_columns = required_columns - set(materials_df.columns)

    if missing_columns:
        st.error(
            "Materials CSV is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )
        st.stop()

    if materials_df.empty:
        st.error("The materials.csv file contains no material data.")
        st.stop()

    materials_df["emission_factor"] = pd.to_numeric(
        materials_df["emission_factor"], errors="raise"
    )
    materials_df["unit_cost"] = pd.to_numeric(
        materials_df["unit_cost"], errors="raise"
    )

    if materials_df["material"].isna().any():
        raise ValueError("Material names cannot be empty.")

    if materials_df["material"].astype(str).str.strip().eq("").any():
        raise ValueError("Material names cannot be empty.")

    if materials_df["material"].duplicated().any():
        raise ValueError("Material names must be unique.")

    if materials_df["unit"].isna().any():
        raise ValueError("Material units cannot be empty.")

    if (
        materials_df["emission_factor"].isna().any()
        or materials_df["unit_cost"].isna().any()
    ):
        raise ValueError("Emission factors and unit costs must be valid numbers.")

    if not materials_df["emission_factor"].map(
        lambda value: pd.notna(value) and abs(value) != float("inf")
    ).all():
        raise ValueError("Emission factors must be finite numbers.")

    if not materials_df["unit_cost"].map(
        lambda value: pd.notna(value) and abs(value) != float("inf")
    ).all():
        raise ValueError("Unit costs must be finite numbers.")

    if (materials_df["emission_factor"] < 0).any():
        raise ValueError("Emission factors cannot be negative.")

    if (materials_df["unit_cost"] < 0).any():
        raise ValueError("Unit costs cannot be negative.")

except FileNotFoundError:
    st.error("Material data file not found: data/materials.csv")
    st.stop()

except (ValueError, pd.errors.ParserError) as error:
    st.error(f"Unable to read material data: {error}")
    st.stop()


# --------------------------------------------------
# Sidebar: Material Inputs
# --------------------------------------------------

st.sidebar.header("Material Details")
st.sidebar.info(
    "Enter the quantity and estimated cost for each material."
)

rows = []

for _, item in materials_df.iterrows():
    material_name = str(item["material"])
    unit = str(item["unit"])

    st.sidebar.subheader(material_name)

    quantity = st.sidebar.number_input(
        f"Quantity ({unit}) — {material_name}",
        min_value=0.0,
        value=100.0,
        step=10.0,
        key=f"quantity_{material_name}",
    )

    unit_cost = st.sidebar.number_input(
        f"Cost per {unit} (INR) — {material_name}",
        min_value=0.0,
        value=float(item["unit_cost"]),
        step=0.1,
        key=f"cost_{material_name}",
    )

    rows.append(
        {
            "material": material_name,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "emission_factor": float(item["emission_factor"]),
        }
    )


# --------------------------------------------------
# Calculate Carbon Footprint and Cost
# --------------------------------------------------

try:
    df = calculate_footprint(pd.DataFrame(rows))
    summary = summarize_footprint(df)

except (ValueError, KeyError) as error:
    st.error(f"Calculation failed: {error}")
    st.stop()


# --------------------------------------------------
# Dashboard Metrics
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Estimated Total Cost",
    f"₹{summary['total_cost']:,.2f}",
)

col2.metric(
    "Estimated Carbon Footprint",
    f"{summary['total_carbon_kg']:,.2f} kg CO₂e",
)

col3.metric(
    "Materials Analyzed",
    len(df),
)


# --------------------------------------------------
# Material Carbon Analysis
# --------------------------------------------------

st.subheader("📊 Material Analysis")

fig = px.bar(
    df,
    x="material",
    y="carbon_kg_co2e",
    color="material",
    title="Estimated Carbon Footprint by Material",
    labels={
        "material": "Construction Material",
        "carbon_kg_co2e": "Carbon (kg CO₂e)",
    },
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Detailed Results
# --------------------------------------------------

st.subheader("📋 Detailed Results")

st.dataframe(
    df[
        [
            "material",
            "quantity",
            "unit_cost",
            "estimated_cost",
            "carbon_kg_co2e",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Download Results
# --------------------------------------------------

csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Results (CSV)",
    data=csv_data,
    file_name="green_building_analysis.csv",
    mime="text/csv",
)


# --------------------------------------------------
# Data Disclaimer
# --------------------------------------------------

st.warning(
    "Demo only: emission factors and prices are illustrative assumptions, "
    "not verified project-specific environmental data. "
    "Verify material units, emission-factor sources, and local prices "
    "before making real-world decisions."
)


# --------------------------------------------------
# AI-Powered Recommendations
# --------------------------------------------------

st.subheader("🤖 AI-Powered Green Building Recommendations")

if st.button("Generate AI Recommendations"):
    with st.spinner("AI is analyzing your materials..."):
        try:
            recommendations = get_ai_recommendations(
                materials=df,
                total_carbon_kg=summary["total_carbon_kg"],
                total_cost=summary["total_cost"],
            )

            st.markdown(recommendations)

        except Exception:
            st.error(
                "AI recommendations are temporarily unavailable. "
                "Please try again later."
            )
