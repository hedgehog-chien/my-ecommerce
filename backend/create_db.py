import asyncio
from database import engine, Base
import models

async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    print("Database Initialized")

if __name__ == "__main__":
    asyncio.run(init_db())
