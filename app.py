import os
import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="Green Building Analyzer",
    page_icon="🏢",
    layout="wide"
)

# API Key Configuration (Streamlit Secrets ba environment variable theke load korbe)
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
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
    ["Dashboard & Overview", "Material Carbon Footprint (Plotly)", "AI Recommendations"]
)

# --- Plotly Interactive Chart Function ---
def show_material_emissions_chart():
    st.subheader("📊 Material Carbon Footprint Comparison (Plotly Interactive)")
    st.write("Nicher interactive chart-ti theke alada building material-er carbon emission tulona dekhte parben. Apni chart-er opor hover ba zoom korte parben.")
    
    # Material emission data
    data = {
        'Material': ['Concrete', 'Steel', 'Glass', 'Wood', 'Aluminum'],
        'Carbon Emission (kg CO2e)': [300, 550, 200, -50, 800]
    }
    df = pd.DataFrame(data)
    
    # Plotly Bar Chart toiri kora
    fig = px.bar(
        df, 
        x='Material', 
        y='Carbon Emission (kg CO2e)',
        title='Carbon Footprint by Building Material',
        color='Carbon Emission (kg CO2e)',
        color_continuous_scale='Greens',
        text='Carbon Emission (kg CO2e)'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    # Streamlit-e Plotly chart render kora
    st.plotly_chart(fig, use_container_width=True)

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
    show_material_emissions_chart()

# --- Section 3: AI Recommendations ---
elif option == "AI Recommendations":
    st.header("🤖 Gemini AI-Powered Green Building Insights")
    st.write("Apnar building ba material details niche likhe AI recommendation generate korun:")
    
    user_input = st.text_area("Enter project details or material specifications:", placeholder="E.g., Using 40% recycled concrete for commercial building...")
    
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
                    st.success("AI Insights Generated Successfully:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Error generating AI response: {e}")