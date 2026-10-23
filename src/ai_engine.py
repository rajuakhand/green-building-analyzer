
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def get_ai_recommendations(materials, total_carbon_kg, total_cost):
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return "GOOGLE_API_KEY পাওয়া যায়নি। .env ফাইল পরীক্ষা করো।"

    try:
        llm = ChatGoogleGenerativeAI(    
        model="gemini-3.8-flash",

            google_api_key=api_key,
            temperature=0.3,
        )

        material_summary = materials[
            ["material", "quantity", "carbon_kg_co2e", "estimated_cost"]
        ].to_string(index=False)

        prompt = f"""
You are a sustainable green-building advisor.

Analyze this building material footprint.

Materials:
{material_summary}

Total estimated carbon: {total_carbon_kg:.2f} kg CO2e
Total estimated cost: {total_cost:.2f}

Give:
1. The materials contributing most to estimated carbon.
2. Three practical ways to reduce embodied carbon.
3. Potential cost-saving ideas.
4. Important limitations of these estimates.

Use clear, concise language. Do not invent emission factors.
Clearly label recommendations as estimates.
"""

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"AI recommendation আনতে সমস্যা হয়েছে: {e}"
