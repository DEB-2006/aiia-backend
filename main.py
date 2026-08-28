from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes.auth import router as auth_router
from routes.patient import router as patient_router
from routes.safety import router as safety_router
from routes.intervention import router as intervention_router
from routes.dashboard import router as dashboard_router
from routes.trial import router as trial_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AIIA Clinical Trials CTMS",
    version="1.0.0",
    description="GCP-compliant CTMS Backend for Ayurveda Research"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router binding
app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(safety_router)
app.include_router(intervention_router)
app.include_router(dashboard_router)
app.include_router(trial_router)

@app.get("/")
def home():
    return {"message": "AIIA CTMS Backend Server Active"}

@app.get("/health")
def health_check():
    return {"status": "online", "system": "AIIA-CTMS-Backend"}