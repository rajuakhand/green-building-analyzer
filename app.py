import os
import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from fpdf import FPDF

# Page configuration
st.set_page_config(
    page_title="Green Building Analyzer",
    page_icon="🏢",
    layout="wide"
)

# API Key Configuration (Safe for both Local & Streamlit Cloud)
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
# App Header
st.title("🌱 Green Building Analyzer")
st.markdown("**AI-Powered Smart Green Building and Material Footprint Analyzer**")
st.markdown("---")

# Sidebar for Navigation
st.sidebar.header("🧭 Navigation & Menu")
option = st.sidebar.selectbox(
    "Choose a Section",
    ["Dashboard & Overview", "Material Carbon Footprint (Plotly)", "AI Recommendations & PDF Report"]
)

# Sample Data for Materials
material_data = {
    'Material': ['Concrete', 'Steel', 'Glass', 'Wood', 'Aluminum'],
    'Carbon Emission (kg CO2e)': [300, 550, 200, -50, 800]
}
df_materials = pd.DataFrame(material_data)

# --- PDF Generation Function ---
def generate_pdf(df, ai_text):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Green Building Analyzer Report", ln=True, align="C")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(200, 8, txt="AI-Powered Smart Green Building & Carbon Footprint Assessment", ln=True, align="C")
    pdf.ln(10)
    
    # Section 1: Material Emissions Summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="1. Material Carbon Footprint Summary", ln=True)
    pdf.set_font("Arial", "", 10)
    
    for index, row in df.iterrows():
        pdf.cell(200, 8, txt=f"- {row['Material']}: {row['Carbon Emission (kg CO2e)']} kg CO2e", ln=True)
    
    pdf.ln(10)
    
    # Section 2: AI Recommendations
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="2. AI-Powered Recommendations & Insights", ln=True)
    pdf.set_font("Arial", "", 10)
    
    # Clean up text for FPDF (handles multi-line text)
    if not ai_text:
        ai_text = "No AI recommendations generated yet."
    
    pdf.multi_cell(0, 8, txt=ai_text)
    
    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin1')

# --- Section 1: Dashboard ---
if option == "Dashboard & Overview":
    st.header("Welcome to Green Building Dashboard")
    st.write("Eikhane apnar project-er summary ebong core metrics dekhte parben.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Analyzed Materials", value="5 Types")
    with col2:
        st.metric(label="Average Emission Score", value="300 kg CO2e")
    with col3:
        st.metric(label="Sustainability Status", value="Optimized 🌟")

# --- Section 2: Plotly Charts ---
elif option == "Material Carbon Footprint (Plotly)":
    st.subheader("📊 Material Carbon Footprint Comparison (Plotly Interactive)")
    st.write("Nicher interactive chart-ti theke alada building material-er carbon emission tulona dekhte parben.")
    
    fig = px.bar(
        df_materials, 
        x='Material', 
        y='Carbon Emission (kg CO2e)',
        title='Carbon Footprint by Building Material',
        color='Carbon Emission (kg CO2e)',
        color_continuous_scale='Greens',
        text='Carbon Emission (kg CO2e)'
    )
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# --- Section 3: AI Recommendations & PDF Report ---
elif option == "AI Recommendations & PDF Report":
    st.header("🤖 Gemini AI Insights & PDF Report Generator")
    st.write("Project details diye AI recommendations generate করুন এবং এক ক্লিকে অফিশিয়াল পিডিএফ রিপোর্ট ডাউনলোড করুন।")
    
    user_input = st.text_area("Enter project details or material specifications:", placeholder="E.g., Using 40% recycled concrete for commercial building...")
    
    # Session state to store AI response for PDF
    if "ai_response_text" not in st.session_state:
        st.session_state["ai_response_text"] = ""

    if st.button("Generate AI Recommendations"):
        if not api_key:
            st.error("Please configure your GEMINI_API_KEY in Streamlit Cloud Secrets.")
        elif not user_input:
            st.warning("Please enter some project details first.")
        else:
            try:
                with st.spinner("Analyzing with Google Gemini AI..."):
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(f"Provide professional green building and carbon footprint reduction recommendations for: {user_input}")
                    st.session_state["ai_response_text"] = response.text
                    st.success("AI Insights Generated Successfully!")
            except Exception as e:
                st.error(f"Error generating AI response: {e}")

    # Display AI text if available
    if st.session_state["ai_response_text"]:
        st.markdown("### AI Recommendations:")
        st.write(st.session_state["ai_response_text"])
        
        st.markdown("---")
        st.subheader("📥 Download Official PDF Report")
        st.write("আপনার জেনারেট করা ডাটা এবং এআই সাজেশনসহ প্রফেশনাল পিডিএফ রিপোর্ট ডাউনলোড করুন:")
        
        pdf_data = generate_pdf(df_materials, st.session_state["ai_response_text"])
        
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_data,
            file_name="Green_Building_Analyzer_Report.pdf",
            mime="application/pdf"
        )
