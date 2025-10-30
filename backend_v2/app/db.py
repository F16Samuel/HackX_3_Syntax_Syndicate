# backend_v2/app/db.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

class DataBase:
    """Container for the MongoDB client."""
    client: AsyncIOMotorClient | None = None

db = DataBase()

async def connect_to_mongo():
    """Connects to the MongoDB database on application startup."""
    print("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(
        settings.MONGO_URI,
        # Set serverSelectionTimeoutMS to handle connection issues gracefully
        serverSelectionTimeoutMS=5000 
    )
    try:
        # Ping the server to confirm connection
        await db.client.admin.command('ping')
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        db.client = None


async def close_mongo_connection():
    """Closes the MongoDB connection on application shutdown."""
    if db.client:
        print("Closing MongoDB connection...")
        db.client.close()
        print("MongoDB connection closed.")

async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency to get the MongoDB database instance.
    Ensures connection is established.
    """
    if db.client is None:
        # This is a fallback, lifespan event should handle connection.
        await connect_to_mongo() 
        if db.client is None:
            raise Exception("Failed to establish database connection")
            
    return db.client[settings.MONGO_DB_NAME]