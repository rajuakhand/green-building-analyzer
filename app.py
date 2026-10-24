from io import BytesIO
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from fpdf import FPDF

from src.calculator import calculate_footprint, summarize_footprint
from src.advanced_lca import calculate_lca
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
# Local / Cloud API configuration
# --------------------------------------------------
def get_google_api_key():
    """Read a key from Streamlit Secrets or environment variables safely."""
    for key_name in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        try:
            value = st.secrets.get(key_name)
            if value:
                return str(value)
        except Exception:
            # Local machine may not have a Streamlit secrets.toml file.
            # Continue by checking environment variables.
            pass

        value = os.getenv(key_name)
        if value:
            return value

    return None


# Do not print or display the API key.
api_key_available = bool(get_google_api_key())


# --------------------------------------------------
# PDF Report Generator
# --------------------------------------------------
def pdf_safe_text(value):
    """
    FPDF core fonts use a limited character set.
    Replace unsupported characters so report generation won't fail
    when AI output contains Unicode symbols or emoji.
    """
    text = str(value if value is not None else "")
    replacements = {
        "CO₂e": "CO2e",
        "CO₂": "CO2",
        "₹": "INR ",
        "–": "-",
        "—": "-",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "•": "-",
        "×": "x",
        "≥": ">=",
        "≤": "<=",
        "→": "->",
        "₂": "2",
        "₃": "3",
        "🌱": "",
        "🏢": "",
        "🤖": "",
        "📊": "",
        "📌": "",
        "📋": "",
        "📥": "",
        "⚠️": "Warning: ",
        "✅": "[OK] ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Keep Latin-1 characters supported by FPDF's built-in Arial font.
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_pdf_report(results_df, total_cost, total_carbon, recommendations, lca_breakdown=None, total_lifecycle_carbon=None):
    """Create a PDF report using the current calculated results."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_title("Green Building Analyzer Report")
    pdf.set_author("Green Building Analyzer")

    pdf.set_font("Arial", "B", 17)
    pdf.cell(0, 11, "Green Building Analyzer", ln=True, align="C")

    pdf.set_font("Arial", "", 10)
    pdf.cell(
        0,
        7,
        "Estimated Construction Material Cost and Carbon Report",
        ln=True,
        align="C",
    )
    pdf.ln(5)

    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(
        0,
        5,
        "Purpose: preliminary planning and educational estimates. "
        "This report is not a certified life-cycle assessment.",
    )
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "1. Project Summary", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"Estimated material cost: INR {total_cost:,.2f}", ln=True)
    pdf.cell(0, 7, f"Estimated carbon footprint: {total_carbon:,.2f} kg CO2e", ln=True)
    pdf.cell(0, 7, f"Materials analyzed: {len(results_df)}", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "2. Life-Cycle Carbon Summary", ln=True)
    pdf.set_font("Arial", "", 9)

    if lca_breakdown is not None and total_lifecycle_carbon is not None:
        pdf.cell(
            0, 6,
            f"Estimated total life-cycle carbon: {total_lifecycle_carbon:,.2f} kg CO2e",
            ln=True,
        )
        for stage, carbon in lca_breakdown.items():
            pdf.multi_cell(
                0, 6,
                pdf_safe_text(f"{stage}: {float(carbon):,.2f} kg CO2e"),
                new_x="LMARGIN",
                new_y="NEXT",
            )
    else:
        pdf.multi_cell(
            0, 6,
            "Life-cycle stage breakdown was not provided for this report.",
            new_x="LMARGIN",
            new_y="NEXT",
        )

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "3. Material-wise Results", ln=True)

    # Table headings
    col_widths = [48, 20, 27, 30, 30, 30]
    headers = ["Material", "Unit", "Quantity", "Unit cost (INR)", "Cost (INR)", "Carbon (kg CO2e)"]

    pdf.set_font("Arial", "B", 8)
    for width, header in zip(col_widths, headers):
        pdf.cell(width, 8, pdf_safe_text(header), border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for _, row in results_df.iterrows():
        values = [
            pdf_safe_text(row.get("material", ""))[:27],
            pdf_safe_text(row.get("unit", ""))[:10],
            f"{float(row.get('quantity', 0)):,.2f}",
            f"{float(row.get('unit_cost', 0)):,.2f}",
            f"{float(row.get('estimated_cost', 0)):,.2f}",
            f"{float(row.get('carbon_kg_co2e', 0)):,.2f}",
        ]

        # Add a new page before the table row if necessary.
        if pdf.get_y() > 265:
            pdf.add_page()
            pdf.set_font("Arial", "B", 8)
            for width, header in zip(col_widths, headers):
                pdf.cell(width, 8, pdf_safe_text(header), border=1)
            pdf.ln()
            pdf.set_font("Arial", "", 8)

        for width, value in zip(col_widths, values):
            pdf.cell(width, 7, pdf_safe_text(value), border=1)
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "4. AI Recommendations", ln=True)
    pdf.set_font("Arial", "", 9)

    recommendation_text = recommendations or (
        "No AI recommendations were generated during this session."
    )
    pdf.multi_cell(0, 5, pdf_safe_text(recommendation_text))

    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "5. Data Limitations and Assumptions", ln=True)
    pdf.set_font("Arial", "", 9)
    limitations = (
        "- Results depend on the material quantities and emission factors "
        "provided to the application.\n"
        "- Emission factors and default prices may be illustrative and "
        "must be independently verified before real-world decisions.\n"
        "- Ensure each quantity unit matches its emission-factor unit.\n"
        "- If concrete includes cement, sand, and aggregate, counting both "
        "the concrete and its ingredients may double-count emissions.\n"
        "- This report does not claim to be a complete or certified "
        "whole-life carbon assessment."
    )
    pdf.multi_cell(0, 5, pdf_safe_text(limitations))

    # fpdf2 returns bytes/bytearray with output(); handle supported versions.
    output = pdf.output()
    if isinstance(output, bytearray):
        return bytes(output)
    if isinstance(output, bytes):
        return output
    # Compatibility fallback for older FPDF versions.
    return bytes(output)


# --------------------------------------------------
# Custom Styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFFFF;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #173F35;
        letter-spacing: -0.02em;
    }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #DDE5DF;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(23, 63, 53, 0.05);
    }

    div[data-testid="stMetricLabel"] {
        color: #52645B;
    }

    div[data-testid="stMetricValue"] {
        color: #173F35;
        font-weight: 700;
    }

    .hero-caption {
        color: #52645B;
        font-size: 1.05rem;
        line-height: 1.6;
        margin-top: -0.4rem;
    }

    div.stButton > button,
    div[data-testid="stDownloadButton"] > button {
        background-color: #087F5B;
        color: #FFFFFF;
        border: 1px solid #087F5B;
        border-radius: 10px;
        padding: 0.55rem 1rem;
        font-weight: 600;
        transition: background-color 0.2s ease;
    }

    div.stButton > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #066849;
        border-color: #066849;
        color: #FFFFFF;
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        border: 1px solid #E2E8E3;
        border-radius: 10px;
        overflow: hidden;
    }

    hr {
        border-color: #E2E8E3;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        div[data-testid="stMetric"] {
            padding: 14px;
        }
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

    if materials_df["material"].isna().any() or materials_df["material"].eq("").any():
        st.error("Material names cannot be empty.")
        st.stop()

    if materials_df["unit"].isna().any() or materials_df["unit"].eq("").any():
        st.error("Material units cannot be empty.")
        st.stop()

    if materials_df["material"].duplicated().any():
        st.error("Each material must have a unique name.")
        st.stop()

    for column in ["emission_factor", "unit_cost"]:
        materials_df[column] = pd.to_numeric(materials_df[column], errors="raise")

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
# Advanced LCA Inputs
# --------------------------------------------------
st.sidebar.divider()
st.sidebar.subheader("🌍 Advanced Life-Cycle Assessment")
st.sidebar.caption(
    "Optional estimates for transport, operational electricity, "
    "and end-of-life carbon. Verify all factors for your project."
)

with st.sidebar.expander("Transport emissions", expanded=False):
    transport_tonnes = st.number_input(
        "Transported material mass (tonnes)",
        min_value=0.0,
        value=0.0,
        step=1.0,
        key="lca_transport_tonnes",
    )
    transport_distance_km = st.number_input(
        "One-way transport distance (km)",
        min_value=0.0,
        value=0.0,
        step=10.0,
        key="lca_transport_distance_km",
    )
    transport_factor = st.number_input(
        "Transport factor (kg CO2e / tonne-km)",
        min_value=0.0,
        value=0.0,
        step=0.01,
        format="%.4f",
        key="lca_transport_factor",
        help="Enter a verified factor for the relevant vehicle and fuel.",
    )

with st.sidebar.expander("Operational electricity", expanded=False):
    annual_energy_kwh = st.number_input(
        "Annual electricity use (kWh)",
        min_value=0.0,
        value=0.0,
        step=100.0,
        key="lca_annual_energy_kwh",
    )
    building_lifetime_years = st.number_input(
        "Building lifetime (years)",
        min_value=1,
        value=50,
        step=1,
        key="lca_building_lifetime_years",
    )
    electricity_factor = st.number_input(
        "Electricity factor (kg CO2e / kWh)",
        min_value=0.0,
        value=0.0,
        step=0.01,
        format="%.4f",
        key="lca_electricity_factor",
        help="Enter a verified grid emission factor for the relevant location.",
    )

with st.sidebar.expander("End-of-life estimate", expanded=False):
    end_of_life_carbon_kg = st.number_input(
        "End-of-life emissions (kg CO2e)",
        min_value=0.0,
        value=0.0,
        step=100.0,
        key="lca_end_of_life_carbon_kg",
        help="Enter a documented estimate; zero means no impact has been entered.",
    )


# --------------------------------------------------
# Calculations
# --------------------------------------------------
try:
    input_df = pd.DataFrame(rows)
    df = calculate_footprint(
        input_df[["material", "quantity", "unit_cost", "emission_factor"]]
    )
    df["unit"] = input_df["unit"].values
    summary = summarize_footprint(df)
except (ValueError, KeyError) as error:
    st.error(f"Calculation failed: {error}")
    st.stop()

total_cost = summary["total_cost"]
total_carbon = summary["total_carbon_kg"]

lca_result = calculate_lca(
    embodied_carbon_kg=total_carbon,
    transport_tonnes=transport_tonnes,
    transport_distance_km=transport_distance_km,
    transport_factor_kg_per_tonne_km=transport_factor,
    annual_energy_kwh=annual_energy_kwh,
    building_lifetime_years=int(building_lifetime_years),
    electricity_factor_kg_per_kwh=electricity_factor,
    end_of_life_carbon_kg=end_of_life_carbon_kg,
)
lca_breakdown_df = pd.DataFrame(
    [
        {"Life-Cycle Stage": stage, "Carbon (kg CO2e)": carbon}
        for stage, carbon in lca_result["breakdown"].items()
    ]
)
total_lifecycle_carbon = lca_result["total_lifecycle_carbon_kg"]



# --------------------------------------------------
# Session state for AI recommendations
# --------------------------------------------------
if "ai_recommendations_text" not in st.session_state:
    st.session_state["ai_recommendations_text"] = ""


# --------------------------------------------------
# KPI Dashboard
# --------------------------------------------------
st.subheader("📊 Project Overview")
carbon_col, cost_col, material_col = st.columns(3)

carbon_col.metric("Estimated Carbon Footprint", f"{total_carbon:,.2f} kg CO₂e")
cost_col.metric("Estimated Material Cost", f"₹{total_cost:,.2f}")
material_col.metric("Materials Analyzed", f"{len(df)}")

st.caption(
    "Results are estimates based on the selected quantities "
    "and the emission factors supplied in the project data."
)

# --------------------------------------------------
# Advanced LCA Dashboard
# --------------------------------------------------
st.subheader("🌍 Advanced Life-Cycle Carbon Assessment")
st.metric(
    "Estimated Total Life-Cycle Carbon",
    f"{total_lifecycle_carbon:,.2f} kg CO₂e",
)
st.caption(
    "Includes embodied material carbon, transport, operational electricity, "
    "and the user-entered end-of-life estimate. Zero-valued inputs mean "
    "no impact has been entered for that category; they do not prove "
    "the real-world impact is zero."
)

lca_fig = px.bar(
    lca_breakdown_df,
    x="Carbon (kg CO2e)",
    y="Life-Cycle Stage",
    orientation="h",
    text="Carbon (kg CO2e)",
    title="Carbon by Life-Cycle Stage",
    labels={
        "Carbon (kg CO2e)": "Estimated Carbon (kg CO₂e)",
        "Life-Cycle Stage": "Life-Cycle Stage",
    },
)
lca_fig.update_traces(
    texttemplate="%{text:,.2f}",
    textposition="outside",
    cliponaxis=False,
)
lca_fig.update_layout(
    showlegend=False,
    margin=dict(l=20, r=30, t=60, b=20),
)
st.plotly_chart(lca_fig, use_container_width=True)

st.dataframe(
    lca_breakdown_df.style.format({"Carbon (kg CO2e)": "{:,.2f}"}),
    use_container_width=True,
    hide_index=True,
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
fig.update_traces(texttemplate="%{text:,.2f}", textposition="outside", cliponaxis=False)
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
contribution_df = df[["material", "carbon_kg_co2e"]].copy()

if total_carbon > 0:
    contribution_df["carbon_share_percent"] = (
        contribution_df["carbon_kg_co2e"] / total_carbon * 100
    )
else:
    contribution_df["carbon_share_percent"] = 0.0

contribution_df = contribution_df.sort_values("carbon_kg_co2e", ascending=False)

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
# CSV Export
# --------------------------------------------------
st.subheader("📥 Export Your Analysis")
csv_output = df.to_csv(index=False)

lca_csv_summary = lca_breakdown_df.to_csv(index=False)
lca_total_csv = pd.DataFrame(
    [{
        "Life-Cycle Stage": "TOTAL LIFE-CYCLE CARBON",
        "Carbon (kg CO2e)": total_lifecycle_carbon,
    }]
).to_csv(index=False)

csv_data = (
    csv_output
    + "\\n"
    + "Life-Cycle Carbon Summary\\n"
    + lca_csv_summary
    + lca_total_csv
).encode("utf-8-sig")
st.download_button(
    label="Download Detailed Results (CSV)",
    data=csv_data,
    file_name="green_building_analysis.csv",
    mime="text/csv",
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

if st.button("Generate AI Recommendations", type="primary", use_container_width=True):
    if not api_key_available:
        st.error(
            "Gemini API key not found. Configure GOOGLE_API_KEY or "
            "GEMINI_API_KEY in Streamlit Secrets or environment variables."
        )
    else:
        try:
            with st.spinner("Analyzing material data with Gemini AI..."):
                recommendations = get_ai_recommendations(
                    materials=df,
                    total_carbon_kg=total_carbon,
                    total_cost=total_cost,
                )
            st.session_state["ai_recommendations_text"] = str(recommendations or "")
        except Exception as error:
            st.error(
                "AI recommendations could not be generated. "
                "Check the configured API key and the AI module settings."
            )
            # Do not print secrets. The exception message can sometimes contain
            # implementation details, so keep the user-facing error generic.
            st.caption(f"Error type: {type(error).__name__}: {error!r}")

if st.session_state["ai_recommendations_text"]:
    st.markdown("### AI Recommendations")
    st.markdown(st.session_state["ai_recommendations_text"])


# --------------------------------------------------
# PDF Report
# --------------------------------------------------
st.divider()
st.subheader("📄 PDF Report Generator")
st.write(
    "Download a report containing the current calculation results, "
    "material-level breakdown, and AI recommendations if generated."
)

try:
    pdf_bytes = generate_pdf_report(
        results_df=df,
        total_cost=total_cost,
        total_carbon=total_carbon,
        recommendations=st.session_state["ai_recommendations_text"],
        lca_breakdown=lca_result["breakdown"],
        total_lifecycle_carbon=total_lifecycle_carbon,
    )
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name="Green_Building_Analyzer_Report.pdf",
        mime="application/pdf",
        help="Creates a PDF using the current quantities and costs.",
    )
except Exception as error:
    st.error("PDF report generation failed.")
    st.caption(f"Error type: {type(error).__name__}: {error}")
    st.exception(error)


# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption(
    "Green Building Analyzer | AI-assisted estimates for educational "
    "and preliminary planning purposes. Not a certified life-cycle assessment."
)
