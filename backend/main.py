from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine

app = FastAPI(title="Ecommerce Inventory System")

# CORS Setup (Allow frontend)
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "System Operational"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
