import os
import json
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
# Use the model ID that appeared in your check_models.py list.
# Common working ones: 'gemini-2.0-flash-exp', 'gemini-1.5-flash', 'gemini-1.5-flash-8b'
MODEL_ID = 'gemini-2.5-flash-lite' 

def get_ai_decision(user_message, menu_context, history_summary=""):
    """
    Sends the user message + menu context to Google Gemini
    and returns a structured JSON decision.
    """
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_KEY"))
        
        # System Prompt: The "Brain" instructions
        system_prompt = f"""
        You are the AI Manager of a restaurant called 'AutoHost'.
        
        CONTEXT:
        The current menu is:
        {menu_context}
        
        INSTRUCTIONS:
        1. Analyze the USER MESSAGE.
        2. Identify the Intent: 'menu', 'order', or 'chat'.
        3. If 'order': Extract items matching the menu. Calculate totals if possible.
        4. If 'menu': Be polite, say "Here is our menu below:". Do NOT list items yourself, the system will attach them.
        5. Output strictly VALID JSON. No markdown formatting.
        
        RESPONSE FORMAT (JSON ONLY):
        {{
            "intent": "menu" | "order" | "chat",
            "response_text": "Your polite reply to the customer.",
            "order_items": [
                {{"item_name": "Burger", "qty": 2, "price": 100}}
            ]
        }}
        """

        # Call the AI
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"System: {system_prompt}\nUser: {user_message}"
        )

        # Clean the response (Remove ```json and ``` if AI adds them)
        raw_text = response.text.strip()
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()

        # Parse JSON
        ai_data = json.loads(clean_text)
        return ai_data

    except Exception as e:
        print(f"AI Connection Error: {e}")
        # Fallback if AI crashes
        return {
            "intent": "chat",
            "response_text": "I am currently updating my systems. Please try again in a moment.",
            "order_items": []
        }