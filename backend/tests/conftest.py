"""
Pytest configuration and fixtures.
"""
import pytest
import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

from app.main import app
from app.config import settings
from app.db import mongodb, mongodb_client
import os

# Use test database
TEST_DB_NAME = "programming_pathshala_test"


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Setup test database before tests."""
    # Override database name for tests
    settings.MONGODB_DB = TEST_DB_NAME
    
    # Import after settings override
    from app.db import connect_to_mongo, close_mongo_connection
    
    await connect_to_mongo()
    yield
    
    # Cleanup: drop test database
    if mongodb_client:
        await mongodb_client.drop_database(TEST_DB_NAME)
    await close_mongo_connection()


@pytest_asyncio.fixture
async def client():
    """Create test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db():
    """Get test database instance."""
    return mongodb


@pytest_asyncio.fixture(autouse=True)
async def clean_db(db):
    """Clean database before each test."""
    await db.users.delete_many({})
    await db.refresh_tokens.delete_many({})
    await db.recruiter_invites.delete_many({})
    yield


@pytest_asyncio.fixture
async def sample_candidate(db):
    """Create a sample candidate user."""
    from app.auth.service import AuthService
    auth_service = AuthService(db)
    
    user = await auth_service.create_user(
        email="candidate@test.com",
        name="Test Candidate",
        password="TestPass123",
        roles=["candidate"]
    )
    return user


@pytest_asyncio.fixture
async def sample_recruiter_unverified(db):
    """Create an unverified recruiter user."""
    from app.auth.service import AuthService
    auth_service = AuthService(db)
    
    user = await auth_service.create_user(
        email="recruiter@test.com",
        name="Test Recruiter",
        password="TestPass123",
        roles=["recruiter"],
        is_recruiter_verified=False
    )
    return user


@pytest_asyncio.fixture
async def sample_recruiter_verified(db):
    """Create a verified recruiter user."""
    from app.auth.service import AuthService
    auth_service = AuthService(db)
    
    user = await auth_service.create_user(
        email="recruiter.verified@test.com",
        name="Verified Recruiter",
        password="TestPass123",
        roles=["recruiter"],
        is_recruiter_verified=True
    )
    return user


@pytest_asyncio.fixture
async def sample_admin(db):
    """Create an admin user."""
    from app.auth.service import AuthService
    auth_service = AuthService(db)
    
    user = await auth_service.create_user(
        email="admin@test.com",
        name="Test Admin",
        password="AdminPass123",
        roles=["admin"]
    )
    return user


@pytest_asyncio.fixture
async def valid_invite(db):
    """Create a valid recruiter invite."""
    invite = {
        "email": "newhire@test.com",
        "invite_code": "VALID_CODE_123",
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=7),
        "created_by": None
    }
    result = await db.recruiter_invites.insert_one(invite)
    invite["_id"] = result.inserted_id
    return invite


@pytest_asyncio.fixture
async def candidate_token(client, sample_candidate):
    """Get access token for candidate user."""
    response = await client.post(
        "/api/auth/login/candidate",
        json={
            "email": "candidate@test.com",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def recruiter_token(client, sample_recruiter_verified):
    """Get access token for verified recruiter user."""
    response = await client.post(
        "/api/auth/login/recruiter",
        json={
            "email": "recruiter.verified@test.com",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def admin_token(client, sample_admin):
    """Get access token for admin user."""
    from app.auth.service import AuthService
    auth_service = AuthService(mongodb)
    token = auth_service.create_access_token(str(sample_admin["_id"]), ["admin"])
    return token
