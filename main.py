from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import httpx
import os
from dotenv import load_dotenv
import json
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] for all origins (less secure)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HISTORY_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'history.json'))

# In-memory history: list of dicts with 'story' and 'rating'
def load_history():
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

history: List[Dict[str, str]] = load_history()

# Gemini API config (replace with your actual endpoint and key)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class StoryRequest(BaseModel):
    last_rating: Optional[str] = None

class StoryResponse(BaseModel):
    story: str

class HistoryResponse(BaseModel):
    history: List[Dict[str, str]]

def build_gemini_prompt(
    history: Optional[List[Dict[str, str]]] = None,
    last_rating: Optional[str] = None
) -> str:
    if not history or len(history) == 0:
        return (
            "Write a short story in Russian, 2-3 paragraphs long, suitable for a learner at the intermediate level. "
            "Aim for a story that is interesting and engaging. "
            "Do not include any English translation or explanation."
        )
    history_section = "Here are the last stories and their ratings:\n"
    for i, entry in enumerate(history[-5:], 1):
        history_section += f"\nStory {i}:\n{entry['story']}\nRating: {entry['rating']}\n"
    if last_rating == "Too Easy":
        feedback = "The last story was too easy. Please generate a new story that is more challenging."
    elif last_rating == "Too Hard":
        feedback = "The last story was too hard. Please generate a new story that is easier."
    elif last_rating == "Just Right":
        feedback = (
            "The last story was just right. You do not need to generate a new story unless requested."
        )
    else:
        feedback = "Please generate a new story, adjusting the difficulty as appropriate."
    progression = (
        "When generating a new story, always try to stay on the harder side of 'just right' for the user."
    )
    prompt = (
        f"{history_section}\n\n"
        f"{feedback}\n"
        "Write a new short story in Russian, 5-6 paragraphs long. "
        "Do not include any English translation or explanation. The example texts have 'Story' or 'История' in the beginning, you must NOT include it.\n"
        f"{progression}"
    )
    return prompt

async def call_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(GEMINI_API_URL, headers=headers, params=params, json=data)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Gemini API error")
        result = response.json()
        # Extract the story from the Gemini response
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise HTTPException(status_code=500, detail="Malformed Gemini API response")

@app.post("/generate_story", response_model=StoryResponse)
async def generate_story(req: StoryRequest):
    prompt = build_gemini_prompt(history, req.last_rating)
    story = await call_gemini(prompt)
    # Only add to history if not "Just Right"
    if req.last_rating != "Just Right":
        history.append({"story": story, "rating": req.last_rating or "N/A"})
        # Keep only the last 5
        if len(history) > 5:
            history.pop(0)
        save_history(history)
    return {"story": story}

@app.get("/history", response_model=HistoryResponse)
def get_history():
    return {"history": history} 