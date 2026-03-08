# main.py
# FastAPI ML Inference Service
# This is the Python microservice that:
#   1. Receives a clinical note from Spring Boot
#   2. Preprocesses it
#   3. Classifies it into a medical specialty
#   4. Detects negation of medical entities
#   5. Returns the result as JSON

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from preprocessing import preprocess
from negation import detect_negation

# ── Load saved model and vectorizer on startup ────────────────────────────────
# These are loaded ONCE when the service starts — not on every request
# Loading on every request would be extremely slow
print("Loading model and vectorizer...")
classifier = joblib.load("model/classifier.pkl")
vectorizer  = joblib.load("model/vectorizer.pkl")
print("Model loaded successfully!")

# ── Initialize FastAPI app ────────────────────────────────────────────────────
app = FastAPI(
    title="Medical Triage ML Service",
    description="Classifies clinical notes into medical specialties",
    version="1.0.0"
)

# ── Request and Response Models ───────────────────────────────────────────────
# Pydantic models define the structure of incoming and outgoing JSON
# FastAPI uses these to automatically validate requests
# If a request doesn't match the model — FastAPI returns 422 error automatically

class PredictRequest(BaseModel):
    note: str                    # the raw clinical note text

class SpecialtyProbability(BaseModel):
    specialty: str
    probability: float

class EntityResult(BaseModel):
    entity: str
    category: str
    status: str                  # "Present" or "Negated"

class PredictResponse(BaseModel):
    specialty: str               # top predicted specialty
    confidence: float            # confidence score 0-1
    all_probabilities: list[SpecialtyProbability]
    entities: list[EntityResult]

class PredictResponse(BaseModel):
    specialty: str
    confidence: float
    clean_text: str              
    all_probabilities: list[SpecialtyProbability]
    entities: list[EntityResult]


# ── Health Check Endpoint ─────────────────────────────────────────────────────
# This is a standard endpoint every service should have
# Docker, deployment platforms, and Spring Boot use this to check
# if the service is running and healthy
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ml-service"}


# ── Prediction Endpoint ───────────────────────────────────────────────────────
@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """
    Receives a clinical note, preprocesses it,
    classifies it, detects negation and returns full analysis.
    """

    # Validate input is not empty
    if not request.note or not request.note.strip():
        raise HTTPException(
            status_code=400,
            detail="Clinical note cannot be empty"
        )

    try:
        # Step 1: Preprocess the raw note
        # Same pipeline used during training — MUST be identical
        # If preprocessing differs from training, predictions will be wrong
        clean_text = preprocess(request.note)

        # Step 2: Transform using TF-IDF vectorizer
        # vectorizer.transform() converts text to the same
        # numerical matrix format the model was trained on
        # Note: transform() not fit_transform() — we never relearn vocabulary
        text_vector = vectorizer.transform([clean_text])

        # Step 3: Predict specialty
        predicted_specialty = classifier.predict(text_vector)[0]

        # Step 4: Get confidence scores for all specialties
        # predict_proba() returns probability for each class
        # e.g. [0.89, 0.06, 0.03, 0.02] for 4 specialties
        probabilities = classifier.predict_proba(text_vector)[0]
        classes       = classifier.classes_

        # Build list of all specialty probabilities
        all_probs = [
            SpecialtyProbability(
                specialty=cls,
                probability=round(float(prob), 4)
            )
            for cls, prob in zip(classes, probabilities)
        ]

        # Sort by probability descending
        all_probs.sort(key=lambda x: x.probability, reverse=True)

        # Get confidence of top prediction
        confidence = max(probabilities)

        # Step 5: Detect negation on cleaned text
        raw_entities = detect_negation(clean_text)

        # Build entity results
        entities = [
            EntityResult(
                entity=e['entity'],
                category=e['category'],
                status=e['status']
            )
            for e in raw_entities
        ]
    
        return PredictResponse(
            specialty=predicted_specialty,
            confidence=round(float(confidence), 4),
            clean_text=clean_text,      
            all_probabilities=all_probs,
            entities=entities
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

