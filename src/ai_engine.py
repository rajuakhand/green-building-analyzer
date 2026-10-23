
import os

import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

MODEL_NAME = "gemini-3.8-flash"

REQUIRED_COLUMNS = [
    "material",
    "quantity",
    "carbon_kg_co2e",
    "estimated_cost",
]


# --------------------------------------------------
# Response Formatting
# --------------------------------------------------

def _extract_response_text(content) -> str:
    """Convert Gemini response content into readable text."""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")

                if isinstance(text, str) and text.strip():
                    text_parts.append(text.strip())

        return "\n\n".join(text_parts).strip()

    return str(content).strip()


# --------------------------------------------------
# AI Recommendations
# --------------------------------------------------

def get_ai_recommendations(
    materials: pd.DataFrame,
    total_carbon_kg: float,
    total_cost: float,
) -> str:
    """
    Generate sustainable building recommendations using Gemini.

    Returns readable Markdown text or a user-friendly error message.
    """

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return (
            "⚠️ **AI configuration required**\n\n"
            "`GOOGLE_API_KEY` পাওয়া যায়নি। "
            "প্রজেক্টের `.env` ফাইল এবং API key configuration পরীক্ষা করো।"
        )

    try:
        # Validate the input data
        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in materials.columns
        ]

        if missing_columns:
            return (
                "⚠️ **Material data error**\n\n"
                "প্রয়োজনীয় column পাওয়া যায়নি: "
                + ", ".join(missing_columns)
            )

        if materials.empty:
            return "⚠️ বিশ্লেষণের জন্য কোনো material data পাওয়া যায়নি।"

        # Prepare a compact summary for the AI
        material_summary = materials[
            REQUIRED_COLUMNS
        ].to_string(index=False)

        # Initialize Gemini
        llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=api_key,
            temperature=0.2,
            max_retries=2,
        )

        # Build the recommendation prompt
        prompt = f"""
You are a professional sustainable construction advisor.

Analyze the following construction material footprint data.

MATERIAL DATA:
{material_summary}

TOTAL ESTIMATED CARBON: {total_carbon_kg:.2f} kg CO2e
TOTAL ESTIMATED COST: INR {total_cost:.2f}

Write a professional report in clear English using Markdown.

Include these sections:

## 1. Executive Summary
Briefly summarize the estimated carbon footprint and material cost.

## 2. Main Carbon Contributors
Identify the materials contributing most to the calculated emissions.
Use the provided data and calculate percentages carefully.

## 3. Carbon Reduction Strategies
Suggest three practical ways to reduce embodied carbon.
Mention relevant structural, engineering, durability, and local-code
requirements where appropriate.

## 4. Cost Optimization
Suggest practical procurement, material efficiency, and mix-design ideas.
Do not promise savings without verified cost data.

## 5. Data Quality and Limitations
Explain that emission factors and costs may be illustrative.
Warn about possible double-counting if concrete and its ingredients
are all counted separately.
Mention that transport, construction, and end-of-life impacts may
be excluded.

IMPORTANT RULES:
- Treat all calculated results as estimates, not certified assessments.
- Do not invent emission factors, prices, citations, or verified sources.
- Do not claim a specific carbon reduction percentage without a
  reliable basis and relevant project information.
- Distinguish general recommendations from results calculated
  directly from the supplied data.
- Respect the units and scope limitations of the input data.
- If information is insufficient, clearly state what must be verified.
- Do not claim the project complies with any building code unless verified.
- Keep the report concise, practical, and professional.
"""

        response = llm.invoke(prompt)

        # Normalize the response for Streamlit Markdown rendering
        recommendation_text = _extract_response_text(response.content)

        if not recommendation_text:
            return (
                "⚠️ **Empty AI response**\n\n"
                "Gemini কোনো readable recommendation দেয়নি। "
                "আবার চেষ্টা করো।"
            )

        return recommendation_text

    except Exception:
        # Avoid exposing credentials or raw internal error details
        return (
            "⚠️ **AI recommendations temporarily unavailable**\n\n"
            "Gemini API request সম্পন্ন করা যায়নি। "
            "ইন্টারনেট সংযোগ, API key, model availability এবং "
            "API quota পরীক্ষা করে কিছুক্ষণ পর আবার চেষ্টা করো।"
        )
