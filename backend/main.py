from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import products, purchases, sales, inventory

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

app.include_router(products.router)
app.include_router(purchases.router)
app.include_router(sales.router)
app.include_router(inventory.router)

@app.get("/")
def read_root():
    return {"message": "System Operational"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
