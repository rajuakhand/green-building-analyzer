from io import BytesIO
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from fpdf import FPDF

from src.calculator import (
    calculate_footprint,
    summarize_footprint,
    calculate_research_footprint,
    summarize_research_footprint,
)
from src.advanced_lca import calculate_lca
from src.ai_engine import get_ai_recommendations
from src.material_data import validate_materials
from src.material_data import load_material_factors
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
# Authentication (Streamlit session state based)
# --------------------------------------------------

USERS_KEY = "gba.users.v1"
SESSION_KEY = "gba.session.v1"


def _load_users():
    try:
        raw = st.session_state.get(USERS_KEY)
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return {}


def _save_users(users):
    st.session_state[USERS_KEY] = json.dumps(users)


def _load_session():
    try:
        raw = st.session_state.get(SESSION_KEY)
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None


def _save_session(session):
    st.session_state[SESSION_KEY] = json.dumps(session)


def _clear_session():
    if SESSION_KEY in st.session_state:
        del st.session_state[SESSION_KEY]


def register_user(email, password, mobile=""):
    users = _load_users()
    if email in users:
        return {"success": False, "error": "User already exists."}
    users[email] = {
        "email": email,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "mobile": mobile or "",
        "created_at": datetime.now().isoformat(),
        "role": "user",
    }
    _save_users(users)
    return {"success": True}


def login_user(email, password):
    users = _load_users()
    user = users.get(email)
    if not user:
        return {"success": False, "error": "Invalid email or password."}
    if user["password"] != hashlib.sha256(password.encode()).hexdigest():
        return {"success": False, "error": "Invalid email or password."}
    session = {
        "email": email,
        "role": user["role"],
        "logged_in_at": datetime.now().isoformat(),
    }
    _save_session(session)
    return {"success": True, "user": user}


def login_with_mobile(mobile, sms_code):
    if not sms_code or not sms_code.isdigit() or len(sms_code) != 6:
        return {"success": False, "error": "Invalid SMS code."}
    users = _load_users()
    user = next((u for u in users.values() if u.get("mobile") == mobile), None)
    if not user:
        return {"success": False, "error": "Mobile not registered."}
    session = {
        "email": user["email"],
        "role": user["role"],
        "logged_in_at": datetime.now().isoformat(),
        "mobile": mobile,
    }
    _save_session(session)
    return {"success": True, "user": user}


def logout():
    _clear_session()


def is_authenticated():
    return _load_session() is not None


def get_current_user():
    session = _load_session()
    if not session:
        return None
    users = _load_users()
    return users.get(session["email"])


# --------------------------------------------------
# Unit Conversion
# --------------------------------------------------

UNIT_TO_BASE = {
    "kg": {"to_base": 1, "category": "mass", "base_unit": "kg"},
    "kilogram": {"to_base": 1, "category": "mass", "base_unit": "kg"},
    "tonne": {"to_base": 1000, "category": "mass", "base_unit": "kg"},
    "ton": {"to_base": 1000, "category": "mass", "base_unit": "kg"},
    "ton (吨)": {"to_base": 1000, "category": "mass", "base_unit": "kg"},
    "quintal": {"to_base": 100, "category": "mass", "base_unit": "kg"},
    "jin": {"to_base": 0.5, "category": "mass", "base_unit": "kg"},
    "jin (斤)": {"to_base": 0.5, "category": "mass", "base_unit": "kg"},
    "liang": {"to_base": 0.05, "category": "mass", "base_unit": "kg"},
    "liang (两)": {"to_base": 0.05, "category": "mass", "base_unit": "kg"},
    "g": {"to_base": 0.001, "category": "mass", "base_unit": "kg"},
    "gram": {"to_base": 0.001, "category": "mass", "base_unit": "kg"},
    "lb": {"to_base": 0.453592, "category": "mass", "base_unit": "kg"},
    "pound": {"to_base": 0.453592, "category": "mass", "base_unit": "kg"},
    "m3": {"to_base": 1, "category": "volume", "base_unit": "m3"},
    "m³": {"to_base": 1, "category": "volume", "base_unit": "m3"},
    "cubic_meter": {"to_base": 1, "category": "volume", "base_unit": "m3"},
    "liter": {"to_base": 0.001, "category": "volume", "base_unit": "m3"},
    "litre": {"to_base": 0.001, "category": "volume", "base_unit": "m3"},
    "ml": {"to_base": 0.000001, "category": "volume", "base_unit": "m3"},
    "gallon": {"to_base": 0.00378541, "category": "volume", "base_unit": "m3"},
    "pcs": {"to_base": 1, "category": "count", "base_unit": "pcs"},
    "piece": {"to_base": 1, "category": "count", "base_unit": "pcs"},
    "thousand pcs": {"to_base": 1000, "category": "count", "base_unit": "pcs"},
    "dozen": {"to_base": 12, "category": "count", "base_unit": "pcs"},
    "bag": {"to_base": 1, "category": "count", "base_unit": "pcs"},
    "bag (包)": {"to_base": 1, "category": "count", "base_unit": "pcs"},
    "roll": {"to_base": 1, "category": "count", "base_unit": "pcs"},
    "bundle": {"to_base": 1, "category": "count", "base_unit": "pcs"},
}


def convert_unit(value, from_unit, to_unit):
    from_info = UNIT_TO_BASE.get(from_unit)
    to_info = UNIT_TO_BASE.get(to_unit)
    if not from_info or not to_info:
        return None
    if from_info["category"] != to_info["category"]:
        return None
    base_value = value * from_info["to_base"]
    return base_value / to_info["to_base"]


def get_units_by_category(category):
    return [u for u, info in UNIT_TO_BASE.items() if info["category"] == category]


def get_base_unit(unit):
    info = UNIT_TO_BASE.get(unit)
    return info["base_unit"] if info else None


def is_valid_unit(unit):
    return unit in UNIT_TO_BASE


def get_unit_label(unit):
    labels = {
        "kg": "kg",
        "tonne": "ton (吨)",
        "ton": "ton (吨)",
        "ton (吨)": "ton (吨)",
        "quintal": "quintal",
        "jin": "jin (斤)",
        "jin (斤)": "jin (斤)",
        "liang": "liang (两)",
        "liang (两)": "liang (两)",
        "g": "g",
        "lb": "lb",
        "m3": "m³",
        "m³": "m³",
        "liter": "liter",
        "pcs": "pcs",
        "thousand pcs": "1000 pcs",
        "dozen": "dozen",
        "bag": "bag (包)",
        "bag (包)": "bag (包)",
    }
    return labels.get(unit, unit)


# --------------------------------------------------
# Project Storage (per-user)
# --------------------------------------------------

PROJECTS_KEY_PREFIX = "gba.projects.v1."


def _user_projects_key(email):
    return f"{PROJECTS_KEY_PREFIX}{email}"


def _load_user_projects(email):
    try:
        raw = st.session_state.get(_user_projects_key(email))
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return {}


def _save_user_projects(email, projects):
    st.session_state[_user_projects_key(email)] = json.dumps(projects)


def save_project(name):
    if not is_authenticated():
        raise Exception("Authentication required. Please sign in to save projects.")
    user = get_current_user()
    projects = _load_user_projects(user["email"])
    projects[name] = {
        "quantities": st.session_state.get("material_quantities", {}),
        "unit_costs": st.session_state.get("material_unit_costs", {}),
        "material_units": st.session_state.get("material_units", {}),
        "lca": st.session_state.get("lca_inputs", {}),
        "project": st.session_state.get("project_details", {}),
        "saved_at": datetime.now().isoformat(),
        "owner": user["email"],
    }
    _save_user_projects(user["email"], projects)
    return projects


def list_projects():
    if not is_authenticated():
        return []
    user = get_current_user()
    return list(_load_user_projects(user["email"]).keys())


def load_project(name):
    if not is_authenticated():
        raise Exception("Authentication required. Please sign in to load projects.")
    user = get_current_user()
    projects = _load_user_projects(user["email"])
    saved = projects.get(name)
    if not saved:
        return False
    st.session_state["material_quantities"] = saved.get("quantities", {})
    st.session_state["material_unit_costs"] = saved.get("unit_costs", {})
    st.session_state["material_units"] = saved.get("material_units", {})
    st.session_state["lca_inputs"] = saved.get("lca", {})
    st.session_state["project_details"] = saved.get("project", {})
    return True


def delete_project(name):
    if not is_authenticated():
        raise Exception("Authentication required. Please sign in to delete projects.")
    user = get_current_user()
    projects = _load_user_projects(user["email"])
    if name in projects:
        del projects[name]
    _save_user_projects(user["email"], projects)
    return projects


# --------------------------------------------------

@st.cache_data(ttl="15m", max_entries=30)
def get_cached_ai_recommendations(
    materials_df,
    total_carbon,
    total_cost,
    api_key,
):
    """Reuse identical recent AI reports and avoid unnecessary API calls."""
    return get_ai_recommendations(
        materials=materials_df,
        total_carbon_kg=total_carbon,
        total_cost=total_cost,
        api_key=api_key,
    )


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

    materials_df = validate_materials(materials_df)

    warning_mask = pd.Series(False, index=materials_df.index)

    for column in ["source", "verification_status"]:
        if column in materials_df.columns:
            warning_mask |= materials_df[column].astype("string").str.contains(
                r"demo|not verified|unverified|illustrative|needs.review",
                case=False,
                na=False,
            )

    if warning_mask.any():
        demo_materials = ", ".join(
            materials_df.loc[warning_mask, "material"].astype(str)
        )

        st.warning(
            "Research data-quality notice: One or more material emission "
            "factors are illustrative or have not been independently verified. "
            f"Affected material(s): {demo_materials}. Results involving these "
            "factors must not be interpreted as validated environmental "
            "impact estimates or used to support comparative research claims. "
            "Verify the factor against a traceable source, including its "
            "functional unit, system boundary, material specification, "
            "geographical scope, and reference year before publication."
        )
except FileNotFoundError:
    st.error("Material data file not found: data/materials.csv")
    st.stop()
except (ValueError, pd.errors.ParserError) as error:
    st.error(f"Unable to load material data: {error}")
    st.stop()

# Add imported materials from CSV upload
imported_materials = st.session_state.get("imported_materials", [])
if imported_materials:
    imported_df = pd.DataFrame(imported_materials)
    # Ensure required columns exist
    for col in ["material", "unit", "emission_factor", "unit_cost"]:
        if col not in imported_df.columns:
            imported_df[col] = ""
    imported_df = imported_df.rename(columns={"name": "material"})
    materials_df = pd.concat([materials_df, imported_df], ignore_index=True)
    materials_df = validate_materials(materials_df)


# --------------------------------------------------
# Research Material Factor Catalogue
# --------------------------------------------------
# Research Material Factor Catalogue
# --------------------------------------------------
RESEARCH_FACTORS_FILE = (
    Path(__file__).resolve().parent / "data" / "material_factors.csv"
)

research_factors_df = None

try:
    research_factors_df = load_material_factors(RESEARCH_FACTORS_FILE)

    st.subheader("🔬 Research Material Factor Catalogue")
    st.caption(
        "Browse the 78 construction-material characterization factors extracted "
        "from Chaudhary & Akhtar (2023), Supporting Information Table S3. "
        "These material factors are cradle-to-gate and are separate from the "
        "existing demo pricing dataset."
    )

    search_text = st.text_input(
        "Search research materials",
        placeholder="Example: cement, brick, steel, sand",
        key="research_material_search",
    )

    searchable = research_factors_df[
        ["material_id", "broad_category", "material"]
    ].astype("string")

    if search_text.strip():
        mask = searchable.apply(
            lambda column: column.str.contains(
                search_text.strip(), case=False, na=False
            )
        ).any(axis=1)
        filtered_factors = research_factors_df[mask]
    else:
        filtered_factors = research_factors_df

    if filtered_factors.empty:
        st.warning("No research material matched your search.")
    else:
        selected_label = st.selectbox(
            "Select a research material",
            options=[
                f"{row.material_id} — {row.material}"
                for row in filtered_factors.itertuples(index=False)
            ],
            key="research_material_select",
        )

        selected_id = selected_label.split(" — ", 1)[0]
        selected_factor = research_factors_df[
            research_factors_df["material_id"] == selected_id
        ].iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric("GWP Factor", f"{selected_factor['gwp_cf']:,.4f}")
        col2.metric("Energy Factor", f"{selected_factor['energy_cf']:,.4f}")
        col3.metric("Boundary", str(selected_factor["boundary"]))

        st.dataframe(
            selected_factor.to_frame("Value"),
            width="stretch",
        )

        if str(selected_factor["verification_status"]) == "Needs-review":
            st.warning(
                "This record is marked Needs-review. Do not treat its factors "
                "as fully verified without checking the original source."
            )

except FileNotFoundError:
    st.error("Research material factor file not found: data/material_factors.csv")
except (ValueError, pd.errors.ParserError) as error:
    st.error(f"Unable to load research material factors: {error}")
# --------------------------------------------------
# Research Material Calculator
# --------------------------------------------------

if research_factors_df is not None:

    st.divider()
    st.header("🧮 Research Material Calculator")

    st.caption(
        "Calculate GWP and energy using the 78 research material factors "
        "from Chaudhary & Akhtar (2023), Supporting Information Table S3. "
        "These results use the factor's stated cradle-to-gate boundary."
    )

    research_labels = [
        f"{row.material_id} — {row.material}"
        for row in research_factors_df.itertuples(index=False)
    ]

    selected_research_labels = st.multiselect(
        "Select research materials to calculate",
        options=research_labels,
        key="research_calculator_materials",
    )

    research_rows = []

    if selected_research_labels:

        selected_ids = [
            label.split(" — ", 1)[0]
            for label in selected_research_labels
        ]

        st.subheader("Enter Material Quantities")

        for material_id in selected_ids:

            factor = research_factors_df[
                research_factors_df["material_id"] == material_id
            ].iloc[0]

            material_name = str(factor["material"])
            gwp_unit = str(factor["gwp_unit"]).strip()
            energy_unit = str(factor["energy_unit"]).strip()

            quantity_unit = (
                gwp_unit.split("/", 1)[1].strip()
                if "/" in gwp_unit
                else gwp_unit
            )

            st.markdown(f"**{material_id} — {material_name}**")

            st.caption(
                f"GWP: {gwp_unit} | Energy: {energy_unit}"
            )

            quantity = st.number_input(
                f"Quantity ({quantity_unit})",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key=f"research_quantity_{material_id}",
            )

            research_rows.append({
                "material_id": material_id,
                "material": material_name,
                "quantity": quantity,
                "quantity_unit": quantity_unit,
                "gwp_cf": factor["gwp_cf"],
                "gwp_unit": gwp_unit,
                "energy_cf": factor["energy_cf"],
                "energy_unit": energy_unit,
                "boundary": factor["boundary"],
                "geography": factor["geography"],
                "verification_status": factor["verification_status"],
            })

        try:
            research_input_df = pd.DataFrame(research_rows)

            research_result_df = calculate_research_footprint(
                research_input_df
            )

            research_summary = summarize_research_footprint(
                research_result_df
            )

            st.subheader("Research Calculation Results")

            col1, col2 = st.columns(2)

            col1.metric(
                "Total GWP",
                f"{research_summary['total_carbon_kg_co2e']:,.2f} kg CO2e",
            )

            col2.metric(
                "Total Energy",
                f"{research_summary['total_energy_mj']:,.2f} MJ",
            )

            st.caption(
                f"Boundary: {research_summary['boundary']} | "
                f"Geography: {research_summary['geography']}"
            )

            st.dataframe(
                research_result_df[
                    [
                        "material_id",
                        "material",
                        "quantity",
                        "quantity_unit",
                        "gwp_cf",
                        "gwp_unit",
                        "carbon_kg_co2e",
                        "energy_cf",
                        "energy_unit",
                        "energy_mj",
                        "verification_status",
                    ]
                ],
                width="stretch",
            )

            needs_review = research_result_df[
                research_result_df["verification_status"] == "Needs-review"
            ]

            if not needs_review.empty:
                st.warning(
                    "One or more selected factors are marked Needs-review. "
                    "Check the original source before treating these results "
                    "as verified."
                )

            st.info(
                "This Research Calculator reports only the selected "
                "material factors within their stated boundary. "
                "It does not automatically add transport, onsite "
                "construction, operational or end-of-life impacts."
            )

        except (ValueError, KeyError) as error:
            st.error(f"Research calculation failed: {error}")

    else:
        st.info("Select one or more research materials to begin.")
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
    base_unit = str(item["unit"])

    with st.sidebar.expander(material_name, expanded=True):
        # Unit selection
        base_unit_display = get_unit_label(base_unit)
        available_units = get_units_by_category(
            get_base_unit(base_unit) or "mass"
        )
        unit_options = [base_unit] + [
            u for u in available_units if u != base_unit
        ][:5]

        current_unit = st.session_state.get(
            f"material_unit_{material_name}", base_unit
        )
        if current_unit not in unit_options:
            current_unit = base_unit

        selected_unit = st.selectbox(
            "Unit",
            options=unit_options,
            index=unit_options.index(current_unit),
            key=f"unit_select_{material_name}",
        )

        # Convert stored quantity if unit changed
        stored_qty = st.session_state.get(
            f"material_qty_{material_name}", 100.0
        )
        if selected_unit != current_unit and is_valid_unit(selected_unit) and is_valid_unit(current_unit):
            converted_qty = convert_unit(stored_qty, current_unit, selected_unit)
            if converted_qty is not None:
                stored_qty = converted_qty

        st.session_state[f"material_unit_{material_name}"] = selected_unit
        st.session_state[f"material_qty_{material_name}"] = stored_qty

        quantity = st.number_input(
            f"Quantity ({get_unit_label(selected_unit)})",
            min_value=0.0,
            value=float(stored_qty),
            step=10.0,
            key=f"quantity_{material_name}",
        )
        unit_cost = st.number_input(
            f"Cost per {get_unit_label(selected_unit)} (INR)",
            min_value=0.0,
            value=float(item["unit_cost"]),
            step=0.1,
            key=f"cost_{material_name}",
        )

    # Convert quantity to base unit for calculation
    calc_qty = quantity
    if selected_unit != base_unit and is_valid_unit(selected_unit) and is_valid_unit(base_unit):
        calc_qty = convert_unit(quantity, selected_unit, base_unit) or quantity

    rows.append(
        {
            "material": material_name,
            "quantity": calc_qty,
            "unit_cost": unit_cost,
            "emission_factor": float(item["emission_factor"]),
            "unit": base_unit,
            "display_unit": selected_unit,
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
# Authentication (Sidebar)
# --------------------------------------------------
st.sidebar.divider()
st.sidebar.subheader("🔐 Account")

if is_authenticated():
    user = get_current_user()
    st.sidebar.success(f"Signed in as: {user['email']}")
    if st.sidebar.button("Sign out", key="sidebar_signout", use_container_width=True):
        logout()
        st.rerun()
else:
    auth_tab = st.sidebar.radio(
        "Auth",
        options=["Sign in", "Register"],
        key="auth_tab",
        horizontal=True,
    )

    if auth_tab == "Register":
        reg_email = st.sidebar.text_input("Email", key="reg_email")
        reg_password = st.sidebar.text_input("Password", type="password", key="reg_password")
        reg_mobile = st.sidebar.text_input("Mobile (optional)", key="reg_mobile")
        if st.sidebar.button("Create account", key="btn_register", use_container_width=True):
            if reg_email and reg_password:
                result = register_user(reg_email, reg_password, reg_mobile)
                if result["success"]:
                    st.sidebar.success("Account created! Please sign in.")
                else:
                    st.sidebar.error(result["error"])
            else:
                st.sidebar.error("Please enter email and password.")
    else:
        login_email = st.sidebar.text_input("Email", key="login_email")
        login_password = st.sidebar.text_input("Password", type="password", key="login_password")
        login_mobile = st.sidebar.text_input("Mobile (for SMS login)", key="login_mobile")
        sms_code = st.sidebar.text_input("SMS Code (6 digits)", key="sms_code", max_chars=6)

        col_login, col_mobile = st.sidebar.columns(2)
        with col_login:
            if st.button("Sign in", key="btn_login", use_container_width=True):
                if login_email and login_password:
                    result = login_user(login_email, login_password)
                    if result["success"]:
                        st.sidebar.success("Signed in successfully!")
                        st.rerun()
                    else:
                        st.sidebar.error(result["error"])
                else:
                    st.sidebar.error("Please enter email and password.")
        with col_mobile:
            if st.button("SMS Login", key="btn_mobile_login", use_container_width=True):
                if login_mobile and sms_code:
                    result = login_with_mobile(login_mobile, sms_code)
                    if result["success"]:
                        st.sidebar.success("Signed in with mobile!")
                        st.rerun()
                    else:
                        st.sidebar.error(result["error"])
                else:
                    st.sidebar.error("Please enter mobile and SMS code.")


# --------------------------------------------------
# Project Save/Load (Authenticated users only)
# --------------------------------------------------
st.sidebar.divider()
st.sidebar.subheader("💾 Projects")

if is_authenticated():
    proj_col1, proj_col2 = st.sidebar.columns(2)
    with proj_col1:
        proj_name = st.text_input("Project name", key="proj_name_input", placeholder="e.g. My Building")
        if st.button("Save", key="btn_save_project", use_container_width=True):
            if proj_name:
                try:
                    save_project(proj_name)
                    st.sidebar.success(f"Saved '{proj_name}'")
                except Exception as e:
                    st.sidebar.error(str(e))
            else:
                st.sidebar.error("Enter project name.")
    with proj_col2:
        saved_projects = list_projects()
        if saved_projects:
            selected_proj = st.selectbox(
                "Load project",
                options=[""] + saved_projects,
                key="proj_load_select",
            )
            if selected_proj and st.button("Load", key="btn_load_project", use_container_width=True):
                if load_project(selected_proj):
                    st.sidebar.success(f"Loaded '{selected_proj}'")
                    st.rerun()
                else:
                    st.sidebar.error("Project not found.")
            if st.button("Delete", key="btn_delete_project", use_container_width=True):
                if selected_proj:
                    delete_project(selected_proj)
                    st.sidebar.success(f"Deleted '{selected_proj}'")
                    st.rerun()
                else:
                    st.sidebar.error("Select a project to delete.")
        else:
            st.sidebar.info("No saved projects.")
else:
    st.sidebar.info("Sign in to save/load projects.")


# --------------------------------------------------
# Theme Toggle (Dark Mode)
# --------------------------------------------------
st.sidebar.divider()
st.sidebar.subheader("🎨 Theme")

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

dark_mode = st.sidebar.toggle(
    "Dark Mode",
    value=st.session_state["dark_mode"],
    key="dark_mode_toggle",
)
st.session_state["dark_mode"] = dark_mode

# Apply dark mode CSS
if dark_mode:
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; }
        .stApp h1, .stApp h2, .stApp h3 { color: #ffffff !important; }
        .stApp p, .stApp label, .stApp span { color: #e0e0e0 !important; }
        .stMetric { background-color: #1e1e1e !important; border-color: #333 !important; }
        .stDataFrame { background-color: #1e1e1e !important; }
        .stSelectbox, .stTextInput, .stNumberInput { background-color: #1e1e1e !important; }
        .stButton > button { background-color: #087f5b !important; color: #ffffff !important; }
        .stSidebar { background-color: #0e1117 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# CSV Import
# --------------------------------------------------
st.sidebar.divider()
st.sidebar.subheader("📁 Import Materials")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV",
    type=["csv"],
    key="csv_uploader",
    help="Columns: name, unit, emission_factor, unit_cost, source, verification_status",
)

import_mode = st.sidebar.selectbox(
    "Import mode",
    options=["Merge with existing", "Replace all"],
    key="import_mode_select",
)

if uploaded_file is not None:
    try:
        import_df = pd.read_csv(uploaded_file)
        required_cols = ["name", "unit", "emission_factor", "unit_cost"]
        missing = [c for c in required_cols if c not in import_df.columns]

        if missing:
            st.sidebar.error(f"Missing columns: {', '.join(missing)}")
        else:
            st.sidebar.info(f"Found {len(import_df)} material(s) in CSV.")

            if st.sidebar.button("Confirm Import", key="btn_confirm_import", use_container_width=True):
                if import_mode == "Replace all":
                    st.session_state["imported_materials"] = import_df.to_dict("records")
                    st.sidebar.success("Materials imported (replace mode).")
                else:
                    existing = st.session_state.get("imported_materials", [])
                    existing_names = {m["name"] for m in existing}
                    new_materials = [
                        m for m in import_df.to_dict("records")
                        if m["name"] not in existing_names
                    ]
                    st.session_state["imported_materials"] = existing + new_materials
                    st.sidebar.success(f"Imported {len(new_materials)} new material(s).")
                st.rerun()
    except Exception as e:
        st.sidebar.error(f"Failed to read CSV: {str(e)}")


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
# Unit Converter Panel
# --------------------------------------------------
st.divider()
st.subheader("🧮 Unit Converter")
conv_col1, conv_col2, conv_col3 = st.columns([1, 1, 1])

with conv_col1:
    conv_value = st.number_input("Value", min_value=0.0, value=1.0, step=1.0, key="conv_value")

with conv_col2:
    conv_from = st.selectbox(
        "From",
        options=list(UNIT_TO_BASE.keys()),
        index=0,
        key="conv_from",
    )

with conv_col3:
    conv_to = st.selectbox(
        "To",
        options=list(UNIT_TO_BASE.keys()),
        index=0,
        key="conv_to",
    )

conv_result = None
conv_formula = ""
if conv_value > 0:
    conv_result = convert_unit(conv_value, conv_from, conv_to)
    if conv_result is not None:
        conv_formula = (
            f"{conv_value:,.4f} {get_unit_label(conv_from)} = "
            f"{conv_result:,.4f} {get_unit_label(conv_to)}"
        )
    else:
        conv_formula = "Incompatible units"

if conv_result is not None:
    st.success(conv_formula)
else:
    st.info("Enter a value to convert between units.")

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
st.plotly_chart(lca_fig, width="stretch")

st.dataframe(
    lca_breakdown_df.style.format({"Carbon (kg CO2e)": "{:,.2f}"}),
    width="stretch",
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
st.plotly_chart(fig, width="stretch")


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
    width="stretch",
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
    width="stretch",
    hide_index=True,
)



# --------------------------------------------------
# CSV Export
# --------------------------------------------------
st.subheader("📥 Export Your Analysis")
csv_output = df.to_csv(index=False)

# Save LCA inputs so the calculation can be reproduced later.
lca_inputs_df = pd.DataFrame([
    {"Input": "Transport mass (tonnes)", "Value": transport_tonnes},
    {"Input": "Transport distance (km)", "Value": transport_distance_km},
    {
        "Input": "Transport emission factor (kg CO2e/tonne-km)",
        "Value": transport_factor,
    },
    {"Input": "Annual electricity (kWh)", "Value": annual_energy_kwh},
    {
        "Input": "Building lifetime (years)",
        "Value": building_lifetime_years,
    },
    {
        "Input": "Electricity emission factor (kg CO2e/kWh)",
        "Value": electricity_factor,
    },
    {
        "Input": "End-of-life emissions (kg CO2e)",
        "Value": end_of_life_carbon_kg,
    },
]).to_csv(index=False)

lca_csv_summary = lca_breakdown_df.to_csv(index=False)
lca_total_csv = pd.DataFrame(
    [{
        "Life-Cycle Stage": "TOTAL LIFE-CYCLE CARBON",
        "Carbon (kg CO2e)": total_lifecycle_carbon,
    }]
).to_csv(index=False)

csv_data = (
    csv_output
    + "\n\nLCA Input Assumptions\n"
    + lca_inputs_df
    + "\nLife-Cycle Carbon Summary\n"
    + lca_csv_summary
    + "\n"
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

if st.button("Generate AI Recommendations", type="primary", width="stretch"):
    if not api_key_available:
        st.info(
            "AI recommendations require a Gemini API key. "
            "Configure GOOGLE_API_KEY or GEMINI_API_KEY in "
            "Streamlit Secrets or environment variables to enable."
        )
    else:
        try:
            with st.spinner("Analyzing material data with Gemini AI..."):
                recommendations = get_cached_ai_recommendations(
                    df,
                    total_carbon,
                    total_cost,
                    get_google_api_key(),
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
