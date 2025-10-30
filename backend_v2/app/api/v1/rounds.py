# backend_v2/app/api/v1/rounds.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from app.db import get_database
from app.schemas.round import RoundCreate, RoundPublic
from app.models.round import RoundInDB
from app.core.auth_dependency import get_current_user  # <-- Import auth dependency
from app.models.user import UserInDB  # <-- Import user model

router = APIRouter(
    prefix="/user/rounds",  # <-- Changed prefix to /user/rounds
    tags=["Rounds"],
    dependencies=[Depends(get_current_user)]  # <-- Secure all endpoints in this router
)

# --- CRUD Logic (Refactored from teammate's crud.py) ---

async def _get_filtered_rounds(
    db: AsyncIOMotorDatabase,
    user: UserInDB,  # <-- Pass in the authenticated user
    type: str | None = None,
    status: str | None = None,
    sort: str | None = None
) -> List[RoundPublic]:
    """
    Internal function to fetch rounds from the DB, using Pydantic models.
    """
    query = {
        "user_id": user.id  # <-- Filter rounds by the authenticated user's ID
    }
    if type:
        query["type"] = type
    if status:
        query["status"] = status 

    cursor = db["rounds"].find(query)
    if sort == "date":
        # Pymongo uses 1 for ascending, -1 for descending.
        cursor = cursor.sort("startDateTime", 1) 

    rounds_docs = await cursor.to_list(100)
    
    # Pydantic will handle the _id -> id mapping and serialization
    return [RoundPublic(**doc) for doc in rounds_docs]

async def _add_round(
    db: AsyncIOMotorDatabase,
    round_data: RoundCreate,
    user: UserInDB  # <-- Pass in the authenticated user
) -> RoundPublic:
    """
    Internal function to create a new round document in the DB.
    """
    new_round = RoundInDB(
        **round_data.model_dump(),
        user_id=user.id  # <-- Set the user_id on creation
    )
    
    # Convert to dict for insertion, using alias=True to handle '_id'
    round_doc = new_round.model_dump(by_alias=True, exclude=["id"])
    
    result = await db["rounds"].insert_one(round_doc)
    
    inserted = await db["rounds"].find_one({"_id": result.inserted_id})
    if not inserted:
        raise HTTPException(
            status_code=500, 
            detail="Failed to create and retrieve the new round."
        )
        
    return RoundPublic(**inserted)

# --- API Endpoints (Refactored from teammate's routes.py) ---

@router.get("/", response_model=List[RoundPublic])
async def fetch_rounds_endpoint(
    type: str | None = Query(None, description="Filter by round type"),
    status: str | None = Query(None, description="Filter by round status"),
    sort: str | None = Query(None, description="Sort by 'date'"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user)  # <-- Get current user
):
    """
    Get a list of rounds for the authenticated user.
    """
    return await _get_filtered_rounds(db, current_user, type, status, sort)

@router.post("/", response_model=RoundPublic, status_code=status.HTTP_201_CREATED)
async def create_round_endpoint(
    round: RoundCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user)  # <-- Get current user
):
    """
    Create a new round for the authenticated user.
    """
    return await _add_round(db, round, current_user)

