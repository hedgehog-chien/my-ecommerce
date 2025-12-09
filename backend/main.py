from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, get_db
from routers import products, purchases, sales, inventory
import import_service

app = FastAPI(title="Ecommerce Inventory System")

# CORS Setup (Allow frontend)
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:5174", # Vite alternative
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
