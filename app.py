
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
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# Custom Styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(46, 125, 50, 0.06) 0%, rgba(46, 125, 50, 0.01) 100%);
        border: 1px solid rgba(46, 125, 50, 0.25);
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: rgba(46, 125, 50, 0.5);
        box-shadow: 0 6px 12px -2px rgba(46, 125, 50, 0.1);
    }

    .hero-caption {
        font-size: 1.1rem;
        color: #2e7d32;
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🌱 Green Building Analyzer")

st.markdown(
    '<p class="hero-caption">'
    "AI-powered construction material cost and carbon footprint analysis"
    "</p>",
    unsafe_allow_html=True,
)

st.divider()


# --------------------------------------------------
# Load Material Data
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
        st.error("No material data found in materials.csv.")
        st.stop()

    materials_df["material"] = materials_df["material"].astype("string").str.strip()
    materials_df["unit"] = materials_df["unit"].astype("string").str.strip()

    if (
        materials_df["material"].isna().any()
        or materials_df["material"].eq("").any()
    ):
        st.error("Material names cannot be empty.")
        st.stop()

    if (
        materials_df["unit"].isna().any()
        or materials_df["unit"].eq("").any()
    ):
        st.error("Material units cannot be empty.")
        st.stop()

    if materials_df["material"].duplicated().any():
        st.error("Each material must have a unique name.")
        st.stop()

    for column in ["emission_factor", "unit_cost"]:
        materials_df[column] = pd.to_numeric(
            materials_df[column],
            errors="raise",
        )

        if not materials_df[column].map(
            lambda value: pd.notna(value) and abs(value) != float("inf")
        ).all():
            st.error(f"{column} must contain finite numeric values.")
            st.stop()

        if (materials_df[column] < 0).any():
            st.error(f"{column} cannot contain negative values.")
            st.stop()

except FileNotFoundError:
    st.error("Material data file not found: data/materials.csv")
    st.stop()

except (ValueError, pd.errors.ParserError) as error:
    st.error(f"Unable to load material data: {error}")
    st.stop()


# --------------------------------------------------
# Sidebar Inputs
# --------------------------------------------------

st.sidebar.title("🏗️ Project Inputs")
st.sidebar.caption("Adjust material quantities and unit costs.")

st.sidebar.info(
    "Quantities and prices are user inputs. "
    "Emission factors come from the project's CSV data."
)

rows = []

for _, item in materials_df.iterrows():
    material_name = str(item["material"])
    unit = str(item["unit"])

    with st.sidebar.expander(material_name, expanded=True):
        quantity = st.number_input(
            f"Quantity ({unit})",
            min_value=0.0,
            value=100.0,
            step=10.0,
            key=f"quantity_{material_name}",
        )

        unit_cost = st.number_input(
            f"Cost per {unit} (INR)",
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
            "unit": unit,
        }
    )


# --------------------------------------------------
# Calculations
# --------------------------------------------------

try:
    input_df = pd.DataFrame(rows)

    df = calculate_footprint(
        input_df[
            ["material", "quantity", "unit_cost", "emission_factor"]
        ]
    )

    df["unit"] = input_df["unit"].values

    summary = summarize_footprint(df)

except (ValueError, KeyError) as error:
    st.error(f"Calculation failed: {error}")
    st.stop()


# --------------------------------------------------
# KPI Dashboard
# --------------------------------------------------

st.subheader("📊 Project Overview")

total_cost = summary["total_cost"]
total_carbon = summary["total_carbon_kg"]

carbon_col, cost_col, material_col = st.columns(3)

carbon_col.metric(
    "Estimated Carbon Footprint",
    f"{total_carbon:,.2f} kg CO₂e",
)

cost_col.metric(
    "Estimated Material Cost",
    f"₹{total_cost:,.2f}",
)

material_col.metric(
    "Materials Analyzed",
    f"{len(df)}",
)

st.caption(
    "Results are estimates based on the selected quantities "
    "and the emission factors supplied in the project data."
)

st.divider()


# --------------------------------------------------
# Carbon Analysis
# --------------------------------------------------

st.subheader("🌍 Carbon Footprint by Material")

chart_df = df.sort_values("carbon_kg_co2e", ascending=False)

fig = px.bar(
    chart_df,
    x="material",
    y="carbon_kg_co2e",
    color="material",
    text="carbon_kg_co2e",
    labels={
        "material": "Construction Material",
        "carbon_kg_co2e": "Estimated Carbon (kg CO₂e)",
    },
    title="Estimated Embodied Carbon",
)

fig.update_traces(
    texttemplate="%{text:,.2f}",
    textposition="outside",
    cliponaxis=False,
)

fig.update_layout(
    showlegend=False,
    margin=dict(l=20, r=20, t=60, b=20),
    yaxis_title="Carbon (kg CO₂e)",
    xaxis_title="Material",
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Material Contribution
# --------------------------------------------------

st.subheader("📌 Material Contribution")

contribution_df = df[
    ["material", "carbon_kg_co2e"]
].copy()

if total_carbon > 0:
    contribution_df["carbon_share_percent"] = (
        contribution_df["carbon_kg_co2e"] / total_carbon * 100
    )
else:
    contribution_df["carbon_share_percent"] = 0.0

contribution_df = contribution_df.sort_values(
    "carbon_kg_co2e",
    ascending=False,
)

st.dataframe(
    contribution_df.rename(
        columns={
            "material": "Material",
            "carbon_kg_co2e": "Carbon (kg CO₂e)",
            "carbon_share_percent": "Carbon Share (%)",
        }
    ).style.format(
        {
            "Carbon (kg CO₂e)": "{:,.2f}",
            "Carbon Share (%)": "{:.2f}%",
        }
    ),
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Detailed Results
# --------------------------------------------------

st.subheader("📋 Detailed Material Results")

display_df = df[
    [
        "material",
        "unit",
        "quantity",
        "unit_cost",
        "estimated_cost",
        "emission_factor",
        "carbon_kg_co2e",
    ]
].rename(
    columns={
        "material": "Material",
        "unit": "Unit",
        "quantity": "Quantity",
        "unit_cost": "Unit Cost (INR)",
        "estimated_cost": "Estimated Cost (INR)",
        "emission_factor": "Emission Factor",
        "carbon_kg_co2e": "Carbon (kg CO₂e)",
    }
)

st.dataframe(
    display_df.style.format(
        {
            "Quantity": "{:,.2f}",
            "Unit Cost (INR)": "₹{:,.2f}",
            "Estimated Cost (INR)": "₹{:,.2f}",
            "Emission Factor": "{:,.4f}",
            "Carbon (kg CO₂e)": "{:,.2f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Download Report
# --------------------------------------------------

st.subheader("📥 Export Your Analysis")

csv_data = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="Download Detailed Results (CSV)",
    data=csv_data,
    file_name="green_building_analysis.csv",
    mime="text/csv",
    use_container_width=False,
)


# --------------------------------------------------
# Data Quality Disclaimer
# --------------------------------------------------

st.warning(
    "**Demo data disclaimer:** Emission factors and default prices "
    "are illustrative and have not been independently verified. "
    "Confirm units, local prices, and emission-factor sources before "
    "using these results for real construction decisions."
)

st.info(
    "**Important:** If the concrete quantity already includes cement, "
    "sand, and aggregate, counting both concrete and its ingredients "
    "may double-count carbon emissions and material costs."
)


# --------------------------------------------------
# AI Recommendations
# --------------------------------------------------

st.divider()
st.subheader("🤖 AI-Powered Sustainability Advisor")

st.write(
    "Generate recommendations for carbon reduction, material selection, "
    "cost optimization, and data limitations."
)

if st.button(
    "Generate AI Recommendations",
    type="primary",
    use_container_width=True,
):
    with st.spinner("Analyzing material data with Gemini AI..."):
        recommendations = get_ai_recommendations(
            materials=df,
            total_carbon_kg=total_carbon,
            total_cost=total_cost,
        )

    st.markdown(recommendations)

st.divider()

st.caption(
    "Green Building Analyzer | AI-assisted estimates for educational "
    "and preliminary planning purposes. Not a certified life-cycle assessment."
)
