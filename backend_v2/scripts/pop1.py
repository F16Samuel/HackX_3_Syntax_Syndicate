# backend_v2/scripts/populate_rounds.py
import os
import sys
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
from datetime import datetime, timedelta

# --- Configuration ---

# This script is in backend_v2/scripts/, so the .env is one level up
DOTENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(DOTENV_PATH)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# The user ID you provided
TARGET_USER_ID_STR = "69037396cae400f88628a4c8"
try:
    TARGET_USER_ID_OBJ = ObjectId(TARGET_USER_ID_STR)
except Exception:
    print(f"Error: Invalid TARGET_USER_ID_STR: {TARGET_USER_ID_STR}")
    print("Please check the user ID and try again.")
    sys.exit(1)

# --- Mock Data ---
# This data matches the 'RoundBase' schema you provided.

now = datetime.now()
tomorrow = now + timedelta(days=1)
next_week = now + timedelta(days=7)

base_rounds_data = [
    {
        "title": "Technical Assessment - Round 1",
        "subtitle": "Backend Engineering Challenge",
        "thumbnailUrl": "https://placehold.co/600x400/5e42a6/white?text=Backend",
        "role": "Software Engineer",
        "whoCanPlay": "Shortlisted Candidates",
        "dateTBA": False,
        "startDateTime": tomorrow.isoformat(),
        "endDateTime": (tomorrow + timedelta(hours=2)).isoformat(),
        "displayStartDate": tomorrow.strftime("%d %b %Y"),
        "displayStartTime": tomorrow.strftime("%I:%M %p"),
        "displayEndDate": (tomorrow + timedelta(hours=2)).strftime("%d %b %Y"),
        "displayEndTime": (tomorrow + timedelta(hours=2)).strftime("%I:%M %p"),
    },
    {
        "title": "Systems Design - Round 2",
        "subtitle": "High-Level Architecture",
        "thumbnailUrl": "https://placehold.co/600x400/42a65e/white?text=Sys+Design",
        "role": "Senior Software Engineer",
        "whoCanPlay": "Round 1 Pass",
        "dateTBA": True,
        "startDateTime": next_week.isoformat(),
        "endDateTime": (next_week + timedelta(hours=1)).isoformat(),
        "displayStartDate": "TBA",
        "displayStartTime": "TBA",
        "displayEndDate": "TBA",
        "displayEndTime": "TBA",
    },
    {
        "title": "Behavioral Interview",
        "subtitle": "Culture Fit",
        "thumbnailUrl": "https://placehold.co/600x400/a64242/white?text=Culture",
        "role": "All Roles",
        "whoCanPlay": "Finalists",
        "dateTBA": False,
        "startDateTime": (now + timedelta(days=10)).isoformat(),
        "endDateTime": (now + timedelta(days=10, hours=1)).isoformat(),
        "displayStartDate": (now + timedelta(days=10)).strftime("%d %b %Y"),
        "displayStartTime": (now + timedelta(days=10)).strftime("%I:%M %p"),
        "displayEndDate": (now + timedelta(days=10, hours=1)).strftime("%d %b %Y"),
        "displayEndTime": (now + timedelta(days=10, hours=1)).strftime("%I:%M %p"),
    }
]

def populate_rounds():
    """
    Connects to the database, cleans old rounds for the target user,
    and inserts the new mock rounds.
    """
    if not MONGO_URI or not MONGO_DB_NAME:
        print("Error: MONGO_URI or MONGO_DB_NAME not found in .env file.")
        print(f"Please check your .env file at: {DOTENV_PATH}")
        return

    client = None
    try:
        print(f"Connecting to MongoDB at {MONGO_URI.split('@')[-1]}...")
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        rounds_collection = db["rounds"]
        
        print(f"\nTargeting user: {TARGET_USER_ID_STR}")

        # 1. Delete existing rounds for this user to avoid duplicates
        print("Deleting old rounds for this user...")
        delete_result = rounds_collection.delete_many(
            {"user_id": TARGET_USER_ID_OBJ}
        )
        print(f"Deleted {delete_result.deleted_count} existing round(s).")

        # 2. Add the user_id to all our mock rounds
        rounds_to_insert = []
        for round_doc in base_rounds_data:
            round_doc["user_id"] = TARGET_USER_ID_OBJ
            rounds_to_insert.append(round_doc)

        # 3. Insert the new rounds
        print(f"Inserting {len(rounds_to_insert)} new rounds...")
        insert_result = rounds_collection.insert_many(rounds_to_insert)
        print(f"Successfully inserted {len(insert_result.inserted_ids)} new round(s).")

        print("\n✅ Population complete!")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    
    finally:
        if client:
            client.close()
            print("MongoDB connection closed.")

if __name__ == "__main__":
    populate_rounds()
