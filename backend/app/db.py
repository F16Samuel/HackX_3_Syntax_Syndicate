"""
Async MongoDB connection using Motor.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Global database client and database instances
mongodb_client: AsyncIOMotorClient | None = None
mongodb: AsyncIOMotorDatabase | None = None


async def connect_to_mongo():
    """Establish connection to MongoDB."""
    global mongodb_client, mongodb
    try:
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
        mongodb = mongodb_client[settings.MONGODB_DB]
        
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.MONGODB_DB}")
        
        # Create indexes
        await create_indexes()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("Closed MongoDB connection")


async def create_indexes():
    """Create necessary database indexes."""
    if mongodb is None:
        return
    
    # Users collection indexes
    await mongodb.users.create_index("email", unique=True)
    await mongodb.users.create_index("oauth.google.sub", sparse=True)
    
    # Refresh tokens collection indexes
    await mongodb.refresh_tokens.create_index("token", unique=True)
    await mongodb.refresh_tokens.create_index("user_id")
    await mongodb.refresh_tokens.create_index("expires_at")
    
    # Recruiter invites collection indexes
    await mongodb.recruiter_invites.create_index("email")
    await mongodb.recruiter_invites.create_index("invite_code", unique=True)
    await mongodb.recruiter_invites.create_index("expires_at")
    
    logger.info("Database indexes created")


def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance."""
    if mongodb is None:
        raise RuntimeError("Database not initialized")
    return mongodb