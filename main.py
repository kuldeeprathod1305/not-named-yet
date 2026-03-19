from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db import init_db, save_route, save_feedback, get_average_rating
from routing import get_route
from datetime import datetime
import random

app = FastAPI()

# -------- CORS --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home():
    return {"message": "Backend running 🚀"}


# -------- REQUEST MODELS --------

class PredictRequest(BaseModel):
    source: str
    destination: str
    time: str = ""
    source_coords: list[float] = []
    destination_coords: list[float] = []

class FeedbackRequest(BaseModel):
    route_id: int
    rating: int
    comment: str = ""


# -------- SMART PREDICTION + ROUTING --------

@app.post("/predict")
def predict(req: PredictRequest):

    # Use provided time or current hour
    if req.time:
        current_hour = int(req.time.split(":")[0])
    else:
        current_hour = datetime.now().hour

    avg_rating = get_average_rating()

    # Time-based traffic logic
    if 8 <= current_hour <= 11 or 17 <= current_hour <= 20:
        base_time = random.randint(30, 50)
        traffic = "high"
        traffic_score = 8.0
    elif 12 <= current_hour <= 16:
        base_time = random.randint(20, 30)
        traffic = "moderate"
        traffic_score = 5.0
    else:
        base_time = random.randint(10, 20)
        traffic = "low"
        traffic_score = 2.0

    # AI learning adjustment (your original logic)
    adjustment = (5 - avg_rating) * 2
    estimated_time = int(base_time + adjustment)
    confidence = round(random.uniform(0.75, 0.95), 2)

    # Real routing if map coords provided
    best_route, alt_route = [], []
    if req.source_coords and req.destination_coords:
        result = get_route(
            req.source_coords,
            req.destination_coords,
            traffic_score
        )
        best_route = result["best_route"]
        alt_route  = result["alt_route"]
        estimated_time = result["estimated_time"]

    route_id = save_route(
        req.source,
        req.destination,
        "smart_route",
        estimated_time
    )

    return {
        "route_id":      route_id,
        "source":        req.source,
        "destination":   req.destination,
        "traffic":       traffic,
        "traffic_score": traffic_score,
        "estimated_time": estimated_time,
        "confidence":    confidence,
        "avg_feedback":  round(avg_rating, 2),
        "best_route":    best_route,
        "alt_route":     alt_route
    }


# -------- FEEDBACK --------

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    save_feedback(req.route_id, req.rating, req.comment)
    return {
        "message":  "Feedback saved ✓",
        "route_id": req.route_id,
        "rating":   req.rating
    }


# -------- HEALTH CHECK --------

@app.get("/health")
def health():
    avg = get_average_rating()
    return {
        "status":     "ok",
        "avg_rating": round(avg, 2),
        "time":       datetime.now().strftime("%H:%M")
    }# Real routing if map coords provided
    best_route, alt_route = [], []
    if req.source_coords and req.destination_coords:
        try:
            result = get_route(
                req.source_coords,
                req.destination_coords,
                traffic_score
            )
            best_route = result["best_route"]
            alt_route  = result["alt_route"]
            estimated_time = result["estimated_time"]
        except Exception as e:
            return {"error": str(e)}