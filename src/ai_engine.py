

import os

import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

MODEL_NAME = "gemini-3.5-flash-lite"

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
            max_retries=0,
            timeout=30,
        )

        # Build the recommendation prompt
        prompt = f"""
You are a practical sustainable-building advisor. Use the supplied data only.

Materials:
{material_summary}

Total estimated carbon: {total_carbon_kg:.2f} kg CO2e
Total estimated material cost: INR {total_cost:.2f}

Write a concise Markdown report with:
1. Executive summary.
2. Main carbon contributors, using the supplied figures.
3. Three practical carbon-reduction recommendations.
4. Cost-saving opportunities without promising unverified savings.
5. Data limitations, including illustrative emission factors and possible
   double-counting if concrete and its ingredients are counted separately.

Treat all results as estimates. Do not invent factors, prices, sources,
or carbon-reduction percentages. Keep the response under 400 words.
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

    except Exception as e:
        print(f"Gemini API error: {type(e).__name__}: {e}", flush=True)
        # Avoid exposing credentials or raw internal error details
        return (
            "⚠️ **AI recommendations temporarily unavailable**\n\n"
            "Gemini API request সম্পন্ন করা যায়নি। "
            "ইন্টারনেট সংযোগ, API key, model availability এবং "
            "API quota পরীক্ষা করে কিছুক্ষণ পর আবার চেষ্টা করো।"
        )
