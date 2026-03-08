## Medical Triage Classification System

An end-to-end NLP pipeline that automatically classifies clinical notes into medical specialties — reducing manual routing work done by Health Information Management (HIM) staff.

## Overview

Clinical notes are unstructured text written by doctors after patient encounters. Manually routing these notes to the correct medical department is time-consuming and error-prone. This system automates that process using NLP and machine learning.

Input: Raw clinical note text  
Output: Predicted medical specialty + confidence score

## Architecture

Browser
   ↓
Frontend (Nginx :80)
   ↓
Spring Boot API Gateway (:8081)
   ↓                    ↓
FastAPI ML Service   PostgreSQL
(:8000)              (:5432)

All services are containerized with Docker Compose.

## Tech Stack

1. ML & NLP - Python, scikit-learn, spaCy
2. ML API - FastAPI, Uvicorn, Pydantic 
3. API Gateway - Java 17, Spring Boot, Spring Data JPA 
4. Database - PostgreSQL 
5. DevOps - Docker, Docker Compose 

## NLP Pipeline

Phase 1 — Clinical Text Preprocessing
- Noise removal (headers, ALL-CAPS section labels, dictation footers)
- Medical abbreviation expansion (abbreviations: `htn → hypertension`, `sob → shortness of breath`)
- Laterality protection (preserves left/right during lemmatization)
- Negation-aware stopword removal (preserves: no, not, without, denies, denied, negative)
- spaCy lemmatization

Phase 2 — Medical Entity Extraction
- POS-based extraction of nouns and adjectives
- Specialty-specific vocabulary analysis

Phase 3 — Negation Detection
- spaCy dependency parsing
- Detects negated vs present clinical findings
- Target entities: symptoms, diseases, anatomy, procedures

Phase 4 — Specialty Classification
- TF-IDF vectorization (5000 features, unigrams + bigrams)
- Logistic Regression with class balancing
- Accuracy: 67.81% on MTSamples dataset


## How to Run

### Prerequisites
- Docker Desktop installed and running

### Steps

1. To start:
```bash
git clone https://github.com/yourusername/medical-triage.git
cd medical-triage
docker compose up --build
```
2. Open `http://localhost` in your browser.

3. To Stop:
```bash
docker compose down
```

## API Endpoints
 
 `POST`  `/api/analyze` - Classify a clinical note 
 `GET`  `/api/notes` - Get all classified notes 
 `GET`  `/api/notes/specialty/{specialty}` - Filter notes by specialty 
 `GET`  `/api/notes/status/{status}` - Filter notes by status 
 `GET`  `/api/stats` - Specialty distribution 
 `PATCH`  `/api/notes/{id}/status` - Update review status 
 `GET`  `/api/health` - System health check 

### Example Request
```json
POST /api/analyze
{
  "note": "Patient presents with chest pain and shortness of breath. History of hypertension and coronary artery disease. Denies fever and cough."
}
```

### Example Response
```json
{
  "id": 1,
  "specialty": "Cardiovascular / Pulmonary",
  "confidence": 0.89,
  "cleanText": "patient present chest pain shortness breath history hypertension coronary artery disease no fever no cough",
  "allProbabilities": [
    { "specialty": "Cardiovascular / Pulmonary", "probability": 0.89 },
    { "specialty": "Surgery", "probability": 0.06 },
    { "specialty": "Orthopedic", "probability": 0.03 },
    { "specialty": "Consult - History and Phy.", "probability": 0.02 }
  ],
  "status": "Pending Review"
}
```

## Model Retraining

The model is trained on the [MTSamples dataset](https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions).

To retrain:
1. Open `NLPMT.ipynb` in Google Colab
2. Upload `mtsamples.csv`
3. Run all cells
4. Download `classifier.pkl` and `vectorizer.pkl`
5. Place both files in `ml-service/model/`
6. Rebuild: `docker compose up --build`


## Dataset

- **Source:** MTSamples — real medical transcription samples
- **Total records:** 4,999
- **Filtered to 4 specialties:** 2,330 records
- **Train/Test split:** 80/20 stratified
