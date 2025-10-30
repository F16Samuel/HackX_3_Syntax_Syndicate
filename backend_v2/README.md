# backend_v2: FastAPI, MongoDB, and JWT

This is the production-ready backend for our assessment platform, built with FastAPI, Motor (async MongoDB), and a self-hosted JWT authentication system.

## Project Structure

\\\
backend_v2/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py         # /register, /login, /me
│   │       ├── candidate.py    # /session, /llm-prompt, /ws/chat
│   │       └── recruiter.py    # /test-template, /results
│   ├── core/
│   │   ├── auth_dependency.py  # get_current_user, RoleChecker
│   │   └── security.py       # Password hashing, JWT creation/decoding
│   ├── db.py                 # MongoDB connection logic (lifespan)
│   ├── models/               # MongoDB data models (UserInDB, Session, etc.)
│   ├── schemas/              # Pydantic schemas for API I/O
│   ├── services/             # Business logic (scoring, LLM gatekeeper, websockets)
│   ├── utils/                # Helper functions (sanitizers)
│   ├── config.py             # Pydantic-settings configuration
│   └── main.py               # FastAPI app initialization, CORS, routers
├── tests/
│   ├── conftest.py           # Pytest fixtures (test client, db setup)
│   ├── test_auth.py          # Tests for auth endpoints
│   └── test_session_flow.py  # Tests for candidate session workflow
├── .env.example              # Environment variable template
├── Dockerfile                # Multi-stage production Dockerfile
├── docker-compose.yml        # For local development with a Mongo container
├── README.md                 # This file
└── requirements.txt          # Python dependencies
\\\

## Setup & Running

### 1. Local Development (with Docker) - Recommended

This is the easiest way to get started.

1.  **Copy Environment File:**
    \\\powershell
    Copy-Item .env.example .env
    \\\
2.  **Edit \.env\:**
    Uncomment the \MONGO_URI\ for local Docker development:
    \\\
    MONGO_URI="mongodb://mongo:27017/"
    MONGO_DB_NAME="backend_v2_dev"
    \\\
    Also, set a \SECRET_KEY\.
3.  **Run Docker Compose:**
    \\\powershell
    docker-compose up --build
    \\\
    The API will be live at \http://localhost:8000/docs\.

### 2. Deployment (Render + MongoDB Atlas)

1.  **MongoDB Atlas:**
    * Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
    * Whitelist all IP addresses (0.0.0.0/0) for network access.
    * Create a database user and get the connection string (select "Drivers").
    * This is your \MONGO_URI\.

2.  **Render:**
    * Create a new **Web Service** on Render and connect your GitHub repository.
    * **Build Command:** \pip install -r requirements.txt\
    * **Start Command:** \uvicorn app.main:app --host 0.0.0.0 --port \
    * **Environment Variables:**
        * \MONGO_URI\: The connection string from MongoDB Atlas.
        * \MONGO_DB_NAME\: The name of your database (e.g., "backend_v2_prod").
        * \SECRET_KEY\: A strong, randomly generated secret.
        * \ALGORITHM\: \HS256\
        * \ACCESS_TOKEN_EXPIRE_MINUTES\: \60\
        * \FRONTEND_URL\: The URL of your deployed React frontend (e.g., \https://your-frontend.onrender.com\).
        * \PYTHON_VERSION\: \3.11\ (or your chosen version).

## Authentication Flow

This backend uses a self-hosted JWT system. There is no \/create-admin\ script. Users must register via the API.

* **Candidates:** \POST /api/v1/auth/candidate/register\ and \POST /api/v1/auth/candidate/login\
* **Recruiters:** \POST /api/v1/auth/recruiter/register\ and \POST /api/v1/auth/recruiter/login\

Login endpoints return a Bearer token that must be included in the \Authorization\ header for protected routes.
