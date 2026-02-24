import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Gmail'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Outlook'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import gmail, outlook

app = FastAPI(
    title="AI Inbox Manager",
    description="Multi-platform inbox with AI-powered categorization",
    version="1.0.0"
)

# CORS - Allow frontend to connect (when we build it later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(gmail.router, prefix="/gmail", tags=["Gmail"])
app.include_router(outlook.router, prefix="/outlook", tags=["Outlook"])

@app.get("/")
def root():
    return {
        "message": "AI Inbox Manager API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}