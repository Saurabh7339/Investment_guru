from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import create_db_and_tables, get_db

from app.services.rag_service import RAGService
from app.services.recommendation_service import RecommendationService
from typing import List
import os

from app.models.client import Client, ClientCreate, ClientRead, InvestmentRecommendation
from app.services.client_service import create_client, delete_client, get_client, get_clients, update_client

app = FastAPI(title="AI Investment Advisor")

import logging
from logging.config import dictConfig
from fastapi.logger import logger as fastapi_logger

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": "app.log",
            "mode": "a",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["default", "file"],
            "level": "INFO",
        },
    },
}

def setup_logging():
    dictConfig(LOG_CONFIG)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    fastapi_logger.handlers = logging.getLogger("app").handlers

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
rag_service = RAGService()
recommendation_service = RecommendationService(rag_service)

# Load documents on startup
@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    setup_logging()
    data_dir = "data"
    if os.path.exists(data_dir):
        file_paths = [
            os.path.join(data_dir, f) 
            for f in os.listdir(data_dir) 
            if f.endswith(('.pdf', '.csv', '.txt'))
        ]
        rag_service.process_and_store_documents(file_paths)

# Client endpoints
@app.post("/clients/",response_model=ClientRead)
def create_new_client(client: ClientCreate, db: Session = Depends(get_db)):
    return create_client(db, client)

@app.get("/clients/", response_model=List[Client])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_clients(db, skip=skip, limit=limit)

@app.get("/clients/{client_id}")
def read_client(client_id: int, db: Session = Depends(get_db)):
    db_client = get_client(db, client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@app.put("/clients/{client_id}", response_model=Client)
def update_existing_client(client_id: int, client_update: dict, db: Session = Depends(get_db)):
    return update_client(db, client_id, client_update)

@app.delete("/clients/{client_id}")
def delete_existing_client(client_id: int, db: Session = Depends(get_db)):
    return delete_client(db, client_id)

# Recommendation endpoint
@app.get("/clients/{client_id}/recommendations", response_model=InvestmentRecommendation)
def get_investment_recommendations(client_id: int, db: Session = Depends(get_db)):
    client = get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client_data = {
        "name": client.name,
        "age": client.age,
        "risk_tolerance": client.risk_tolerance,
        "investment_goals": client.investment_goals,
        "investment_history": client.investment_history,
        "portfolio": client.portfolio,
        "investment_horizon": client.investment_horizon,
        "investor_type": client.investor_type,
        "total_assets": client.total_assets,
        "preferred_investment_types": client.preferred_investment_types,
        "constraints": client.constraints
    }
    
    return recommendation_service.generate_recommendation(client_id, client_data)

# Document upload endpoint
@app.post("/upload-documents/")
async def upload_documents(file_paths: List[str]):
    rag_service.process_and_store_documents(file_paths)
    return {"message": "Documents processed and stored successfully"}