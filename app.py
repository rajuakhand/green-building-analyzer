
import streamlit as st
import pandas as pd
import plotly.express as px

from src.calculator import calculate_footprint, summarize_footprint
from src.ai_engine import get_ai_recommendations


st.set_page_config(
    page_title="Green Building Analyzer",
    page_icon="🌱",
    layout="wide",
)

st.title("🌱 AI-Powered Smart Green Building Analyzer")
st.caption("Construction Material Cost & Carbon Footprint Analysis")


# Sidebar: Material Details
st.sidebar.header("Material Details")
st.sidebar.info(
    "Enter the quantity and estimated values for each material."
)

materials = [
    {"material": "Cement", "factor": 0.90, "unit": "kg"},
    {"material": "Sand", "factor": 0.01, "unit": "kg"},
    {"material": "Aggregate", "factor": 0.005, "unit": "kg"},
    {"material": "Concrete", "factor": 0.13, "unit": "kg"},
]

rows = []

for item in materials:
    st.sidebar.subheader(item["material"])

    quantity = st.sidebar.number_input(
        f"Quantity (kg) — {item['material']}",
        min_value=0.0,
        value=100.0,
        step=10.0,
        key=f"quantity_{item['material']}",
    )

    unit_cost = st.sidebar.number_input(
        f"Cost per kg — {item['material']}",
        min_value=0.0,
        value=1.0,
        step=0.1,
        key=f"cost_{item['material']}",
    )

    rows.append(
        {
            "material": item["material"],
            "quantity": quantity,
            "unit_cost": unit_cost,
            "emission_factor": item["factor"],
        }
    )


# Calculate Carbon Footprint and Cost
df = calculate_footprint(pd.DataFrame(rows))
summary = summarize_footprint(df)


# Dashboard Metrics
col1, col2, col3 = st.columns(3)

col1.metric(
    "Estimated Total Cost",
    f"{summary['total_cost']:,.2f}",
)

col2.metric(
    "Estimated Carbon Footprint",
    f"{summary['total_carbon_kg']:,.2f} kg CO₂e",
)

col3.metric(
    "Materials Selected",
    len(df),
)


# Material Carbon Analysis
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


# Detailed Results
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


# Important Disclaimer
st.warning(
    "Demo only: emission factors and prices are illustrative assumptions, "
    "not verified project-specific environmental data. Replace them with "
    "reliable, region-appropriate data before making real decisions."
)


# Gemini AI Recommendations
st.subheader("🤖 AI-Powered Green Building Recommendations")

if st.button("Generate AI Recommendations"):
    with st.spinner("Gemini AI is analyzing your materials..."):
        recommendations = get_ai_recommendations(
            materials=df,
            total_carbon_kg=summary["total_carbon_kg"],
            total_cost=summary["total_cost"],
        )

        st.markdown(recommendations)
