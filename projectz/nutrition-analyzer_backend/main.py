from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image, UnidentifiedImageError
import io
import json
import uvicorn
import logging
from pydantic import BaseModel
from typing import List
import os

# Initialize FastAPI
app = FastAPI()

# Updated CORS configuration: no trailing slash in allowed origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST", "GET", "DELETE"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more details
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
GEMINI_API_KEY = "AIzaSyDt-V0HuKEjVSDrOWpnD7F7DhM9-R6iLZs"  # REPLACE WITH YOUR ACTUAL KEY
MODEL_NAME = 'gemini-1.5-flash'

try:
    logger.info("Initializing Gemini model...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
    logger.info("Gemini model initialized successfully")
except Exception as e:
    logger.error(f"Gemini initialization failed: {str(e)}")
    raise RuntimeError("Gemini API setup failed")

PROMPT_TEMPLATE = """Analyze this food image and return nutrition data as JSON:
{{
    "food_items": [{{
        "name": "food name",
        "portion_g": number,
        "calories": number,
        "protein_g": number,
        "carbs_g": number,
        "fats_g": number
    }}],
    "total_calories": number
}}"""

@app.post("/analyze-food")
async def analyze_food(image: UploadFile = File(...)):
    try:
        logger.debug(f"Received file: {image.filename}")
        
        if not image.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            raise HTTPException(400, detail="Only JPG/PNG images allowed")

        try:
            image_data = await image.read()
            img = Image.open(io.BytesIO(image_data))
            logger.debug("Image successfully opened")
        except UnidentifiedImageError:
            raise HTTPException(400, detail="Invalid image file")
        except Exception as e:
            raise HTTPException(400, detail=f"Image processing error: {str(e)}")

        try:
            logger.debug("Sending request to Gemini...")
            response = model.generate_content([PROMPT_TEMPLATE, img])
            logger.debug(f"Received response: {response.text[:100]}...")
            
            try:
                clean_response = response.text.replace("```json", "").replace("```", "").strip()
                if clean_response.startswith("{") and clean_response.endswith("}"):
                    return json.loads(clean_response)
                else:
                    logger.error(f"Unexpected response format: {clean_response}")
                    raise HTTPException(502, detail="AI returned unexpected format")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response: {response.text}")
                raise HTTPException(502, detail="AI returned invalid JSON format")

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise HTTPException(503, detail="Food analysis service unavailable")

    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Analysis failed")

CHAT_PROMPT_TEMPLATE =  """
    **System Role:** You are "ChefPal", a friendly and knowledgeable AI assistant specializing in culinary arts, recipes, and food-related discussions. Your primary function is to assist users with their cooking needs and engage in pleasant conversation.

    **Core Directives:**
    1.  **Dual Protocol Operation:** Operate under "General Conversation" and "Recipe/Food Inquiry" protocols based on user intent.
    2.  **Contextual Awareness:** Utilize `chat_history` for conversation flow and recalling *explicitly stated* user preferences (dietary restrictions, allergies, strong likes/dislikes mentioned previously). Prioritize the **current `query`**.
    3.  **Minimal Preference Probing:** When a recipe is requested, avoid excessive questioning about preferences. Ask clarifying questions *only* if essential information (like a known severe allergy needing confirmation or a completely unspecified dietary need for a vague request) is missing. Limit such questions to **one, or at most two, highly relevant points**. Default to standard recipes if the request is specific and no critical constraints are immediately apparent.
    4.  **Strict Output Format:** ALL responses MUST strictly adhere to the JSON format: `{{"response": "YOUR_GENERATED_CONTENT_HERE"}}`. No extra text outside this structure.

    **Protocol Definitions:**

    **Protocol 1: General Conversation**
    *   **Trigger:** Conversational queries, general non-food info, casual chat.
    *   **Behavior:**
        *   Engage in friendly, natural conversation. Maintain a helpful tone.
        *   Respond relevantly.
        *   *Passively* note conversation points (preferences, equipment) from query and `chat_history` for potential *future* reference, but do not actively probe for them in this mode.
        *   Do not provide recipes unless explicitly asked.
        *   Transition smoothly towards Protocol 2 if the user asks about food/recipes.

    **Protocol 2: Recipe/Food Inquiry**
    *   **Trigger:** Explicit requests for recipes, cooking steps, ingredient info, techniques, food types, nutrition.
    *   **Behavior:**
        *   **If a Specific Recipe is Requested (e.g., "lasagna recipe", "chocolate cookie recipe"):**
            *   **Prioritize providing a standard, popular version of the recipe directly.**
            *   **Use Context Selectively:** If `chat_history` contains *clear and relevant* preferences (e.g., user stated "I'm vegetarian" recently), tailor the standard recipe if easily possible (e.g., offer a vegetarian lasagna) and briefly mention the adaptation ("Here's a vegetarian version, as requested..."). Do not re-ask about preferences already stated unless confirmation is critical (e.g., for a severe allergy related to the specific ingredients).
            *   **Minimal Questioning:** Do *not* ask about general preferences (cuisine style, spice level, etc.) unless the request *itself* is vague and requires it. If a clarification is absolutely necessary (e.g., confirming a severe allergy's relevance to *this* recipe), ask **only one, highly targeted question**.
            *   **Recipe Detail:** Provide a clear, detailed recipe including: Title, Brief Description, Prep/Cook/Total Time, Servings, Ingredients (precise quantities/units), Equipment (optional), Numbered Instructions (clear, action verbs), Tips/Variations (optional).
        *   **If a Vague Recipe Request is Made (e.g., "dinner idea", "healthy snack"):**
            *   It is more acceptable here to ask **one or two** guiding questions to narrow down the possibilities. Examples: "Sure! To help me suggest something, do you have any dietary restrictions or preferences (like vegetarian, gluten-free)?", or "Are you looking for something quick, or do you have more time?"
            *   Alternatively, offer a popular default option and mention that you can refine it if they provide more details. Example: "A popular quick dinner is [Recipe Name]. Let me know if you'd like the recipe, or if you have something else in mind (like dietary needs or cuisine type)!"
        *   **If Food Information is Requested (Non-Recipe):**
            *   Provide accurate, detailed, relevant information addressing the query directly. Structure it logically.
        *   **Ambiguity Handling (Query vs. Info):** If a query is unclear (e.g., "tell me about sourdough"), provide brief info and ask if they want a recipe ("...It's known for its tangy flavor. Were you hoping for a recipe to make it yourself?").

    **Input Variables:**
    *   `query`: The user's most recent input/question.
    *   `chat_history`: A transcript or summary of the preceding conversation turns.

    **Mandatory Output:**
    *   Your final output **MUST** be a single JSON object: `{{"response": "..."}}`

    ---

    User: {query}

    Chat_history: {chat_history}

    ---
    """
class RecipeChatBotRequest(BaseModel):
    query: str
    chat_history: str | None = None

@app.post("/chat-bot")
async def reciepe_bot(request: RecipeChatBotRequest):
    query = request.query
    chat_history = request.chat_history or ""
    logger.debug(f"Received query: {query!r}, chat_history: {chat_history!r}")

    prompt = CHAT_PROMPT_TEMPLATE.format(query=query, chat_history=chat_history)

    try:
        logger.debug("Sending request to Gemini...")
        response = model.generate_content([prompt])
        logger.debug(f"Received raw response: {response.text[:100]}...")

        clean = response.text.replace("```json", "").replace("```", "").strip()
        if clean.startswith("{") and clean.endswith("}"):
            return json.loads(clean)
        else:
            logger.error(f"Unexpected response format: {clean}")
            raise HTTPException(status_code=502, detail="AI returned unexpected format")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gemini API or parsing error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Food analysis service unavailable")

# ======== Chat History Management ========

CHAT_HISTORY_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'chat_history')
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

class Message(BaseModel):
    user: str
    bot: str

class Session(BaseModel):
    id: str
    name: str
    messages: List[Message]

@app.get("/api/sessions", response_model=List[Session])
def get_sessions():
    sessions = []
    for filename in os.listdir(CHAT_HISTORY_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(CHAT_HISTORY_DIR, filename), "r", encoding="utf-8") as f:
                sessions.append(json.load(f))
    return sessions

@app.post("/api/sessions")
def save_session(session: Session):
    path = os.path.join(CHAT_HISTORY_DIR, f"{session.id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session.dict(), f, indent=2)
    return {"status": "Saved"}

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    path = os.path.join(CHAT_HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(path):
        os.remove(path)
        return {"status": "Deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")