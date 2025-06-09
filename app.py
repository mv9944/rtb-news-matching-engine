import asyncio
import os
import random
import time
import uuid
import json
from collections import deque
from contextlib import asynccontextmanager

import google.generativeai as genai
from dotenv import load_dotenv
from faker import Faker
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import socketio

load_dotenv()
fake = Faker()

MASTER_TOPICS = [
    "artificial-intelligence", "quantum-computing", "basketball", "nba-playoffs",
    "stock-market", "investment-strategies", "geopolitics", "election-results",
    "mental-health", "nutrition-science", "space-exploration", "mars-rover",
    "cryptocurrency-trends", "electric-vehicles", "battery-technology"
]

# In-memory storage
recent_articles = deque(maxlen=20)
recent_users = deque(maxlen=20)
recent_matches = deque(maxlen=20)
user_interests_db = {}

# --- NEW: State variable to track if generators are running ---
STREAMS_RUNNING = False

# --- Gemini LLM Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
GEMINI_PROMPT = """
Your task is to act as an expert tag extractor.
From the following news article title and summary, extract 5-7 relevant, concise, lowercase, single-word or hyphenated semantic tags.
Your response MUST be a valid JSON list of strings and nothing else. Do not add any explanatory text, markdown, or apologies.

Example Input:
Title: QuantumCorp unveils new 512-qubit processor
Summary: The tech giant QuantumCorp has announced a breakthrough in quantum computing.

Example Output:
["quantum-computing", "processors", "tech", "hardware", "innovation"]

Now, process the following article:
Title: {title}
Summary: {summary}
"""

# --- FastAPI & Socket.IO Setup (MODIFIED) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager now starts the app in an idle state."""
    print("Application started. Waiting for a client to connect and start the streams...")
    yield
    print("Application shutting down...")

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app_asgi = socketio.ASGIApp(sio, app)


# --- LLM Integration (Unchanged from your version) ---
async def get_gemini_tags(title: str, summary: str) -> list[str]:
    """
    Calls the Gemini API to extract semantic tags from article text.
    Includes robust error handling, a fallback mechanism, and detailed logging.
    """
    print(f"\n--- [LLM CALL] Attempting Gemini call for title: '{title}'")

    if not GOOGLE_API_KEY:
        print("--- [LLM SKIP] WARNING: GOOGLE_API_KEY not set. Using fallback.")
        return await fallback_tag_extraction(title)

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash", # Respecting your model choice
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        final_prompt = GEMINI_PROMPT.format(title=title, summary=summary)
        prompt_parts = [final_prompt]

        print(f"--- [LLM INPUT] Sending this to Gemini:\n---\n{final_prompt}\n---")
        
        response = await model.generate_content_async(prompt_parts)
        
        raw_response_text = response.text
        print(f"--- [LLM RAW RESPONSE] Gemini returned:\n---\n{raw_response_text}\n---")

        cleaned_text = raw_response_text.strip().replace("```json", "").replace("```", "").strip()
        
        tags = json.loads(cleaned_text)
        
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
             raise ValueError("LLM response was not a valid list of strings.")

        print(f"--- [LLM SUCCESS] Parsed tags: {tags}")
        
        return [tag.lower().replace(" ", "-") for tag in tags]
    except Exception as e:
        print(f"--- [LLM ERROR] API call or parsing failed: {e}. Using fallback.")
        return await fallback_tag_extraction(title)

async def fallback_tag_extraction(title: str) -> list[str]:
    """A simple, local fallback for tag extraction if the LLM fails."""
    return [word.lower() for word in title.split() if len(word) > 4]


# --- Data Stream Generators (Unchanged) ---
async def article_stream_generator():
    """Generates articles based on a topic from the MASTER_TOPICS list."""
    while True:
        topic = random.choice(MASTER_TOPICS)
        title = f"Breaking News on {topic.replace('-', ' ')}: {fake.sentence(nb_words=5)}"
        summary = fake.paragraph(nb_sentences=2)
        
        article = {
            "id": str(uuid.uuid4()),
            "title": title,
            "summary": summary,
            "llm_tags": await get_gemini_tags(title, summary),
            "timestamp": time.time(),
        }
        
        recent_articles.append(article)
        await sio.emit('new_article', article)
        await match_article_to_users(article)
        
        await asyncio.sleep(1 / 100)

async def user_stream_generator():
    """Simulates user activity using the MASTER_TOPICS list."""
    while True:
        user_id = f"user_{random.randint(1, 1000)}"
        user_interests = set(random.sample(MASTER_TOPICS, k=random.randint(2, 4)))
        
        user = {
            "user_id": user_id,
            "persona": "dynamic_user",
            "interests": list(user_interests),
            "timestamp": time.time(),
        }
        
        user_interests_db[user_id] = user_interests
        recent_users.append(user)
        await sio.emit('new_user', user)
        
        await asyncio.sleep(1 / 15)


# --- Matching Engine (Unchanged) ---
async def match_article_to_users(article: dict):
    """Calculates match scores between a new article and all known users."""
    article_tags = set(article.get("llm_tags", []))
    if not article_tags:
        return

    for user_id, user_tags in user_interests_db.items():
        if not user_tags:
            continue

        matched_tags = article_tags.intersection(user_tags)
        
        if matched_tags:
            score = len(matched_tags) / len(article_tags.union(user_tags))
            
            if score > 0.2:
                match = {
                    "user_id": user_id,
                    "article_id": article["id"],
                    "article_title": article["title"],
                    "score": round(score, 2),
                    "matched_tags": list(matched_tags),
                    "matched_at": time.time(),
                }
                recent_matches.append(match)
                await sio.emit('new_match', match)


# --- API Endpoints & WebSocket Events (MODIFIED) ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main dashboard HTML file."""
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@sio.event
async def connect(sid, environ):
    """Handles a new client connecting via WebSocket."""
    print(f"Client connected: {sid}")
    # Inform the new client if the streams are already running
    if STREAMS_RUNNING:
        await sio.emit('streams_started', to=sid)
    await sio.emit('initial_state', {
        "articles": list(recent_articles),
        "users": list(recent_users),
        "matches": list(recent_matches)
    }, to=sid)

@sio.event
def disconnect(sid):
    """Handles a client disconnecting."""
    print(f"Client disconnected: {sid}")

# --- NEW: Event handler for the start button ---
@sio.event
async def start_streams(sid):
    """Starts the data generators if they are not already running. Triggered by a client."""
    global STREAMS_RUNNING
    if not STREAMS_RUNNING:
        print(f"--- Received start signal from client {sid}. Starting data streams... ---")
        STREAMS_RUNNING = True
        # Start the tasks to run concurrently in the background
        asyncio.create_task(article_stream_generator())
        asyncio.create_task(user_stream_generator())
        # Notify all connected clients that the streams have started
        await sio.emit('streams_started')
    else:
        print(f"--- Received start signal from {sid}, but streams are already running. ---")