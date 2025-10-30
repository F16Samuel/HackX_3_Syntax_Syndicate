
# Updated LLM Prompt (copy-paste)

> You are an expert Python backend engineer. Generate a **complete, production-ready FastAPI server** implementing **User Registration, Login (candidate & recruiter separately), Google OAuth login**, **Token Refresh, Logout**, and a sample protected endpoint. The stack must be **FastAPI + MongoDB** (async), and all configuration/secrets must come from a `.env` file (or pydantic/BaseSettings that reads `.env`). Produce runnable code, tests, and simple run instructions. Follow the exact requirements below.
>
> ### High-level requirements
>
> 1. Use **FastAPI** (async), **Motor** (async MongoDB client), **Pydantic** models for request/response and settings, **python-jose** (or equivalent) for JWT, and **authlib** (or google-auth / oauthlib) for Google OAuth server-side flow. Use **bcrypt** for password hashing. Use pydantic `BaseSettings` to load `.env`.
> 2. Provide token-based authentication using **access tokens (JWT)** and **refresh tokens**. Access tokens short-lived (15 minutes), refresh tokens longer (7 days). Refresh tokens must be **stored in MongoDB** and support rotation/revocation.
> 3. Implement secure practices:
>
>    * Salted password hashing (bcrypt) with configurable rounds.
>    * Validate JWTs: signature, `exp`, `sub`.
>    * Keep secrets in `.env`, **never** hard-code secrets in code.
>    * Provide sample `.env.example` file including Google OAuth variables.
>    * Show both header-based and cookie-based refresh token options; default to header JSON + DB storage. Include commented cookie code & instructions.
> 4. Use **async/await** consistently (FastAPI + Motor).
> 5. Provide neat file/project layout. Each file as a labeled code block.
> 6. Include **unit tests** (pytest + httpx AsyncClient) for register/login/refresh/logout/google-oauth/protected route.
> 7. Provide a `requirements.txt` and run instructions.
>
> ### Role & flow specifics (candidate vs recruiter)
>
> * User document must include `roles: list[str]` and `is_recruiter_verified: bool` (default `False`).
> * There must be two separate login endpoints:
>
>   * `POST /api/auth/login/candidate` — normal email/password login for candidate role. If user exists with role `candidate` or no explicit role, allow login and return tokens.
>   * `POST /api/auth/login/recruiter` — recruiter login flow:
>
>     * Accepts `{ "email", "password", "invite_code" (optional) }`.
>     * If a recruiter account exists and `is_recruiter_verified` is `True`, allow login like candidate.
>     * If recruiter account exists but `is_recruiter_verified` is `False`, reject login with 403 and message: "Recruiter pending verification".
>     * Support invite-based verification: if an `invite_code` is provided and matches a pre-created `recruiter_invites` collection record (with `email`, `invite_code`, `expires_at`), then on successful registration set `is_recruiter_verified=True`. (Implement invite lookup logic.)
>     * Also include a `POST /api/auth/recruiter/verify` endpoint that an admin can call to flip `is_recruiter_verified` for a user (protected — admin-only).
> * On registration, default role is `candidate`. Provide separate recruiter registration route `POST /api/auth/register/recruiter` that requires a valid `invite_code` OR admin creation. If invite present and valid, set `is_recruiter_verified=True` and add `recruiter` to `roles`.
>
> ### Google OAuth specifics
>
> * Implement server-side OAuth flow using **Authlib's OAuth client** (or clearly instruct model to use it). Provide endpoints:
>
>   * `GET /api/auth/google/login` — redirect to Google's OAuth consent screen with scopes `openid email profile`.
>   * `GET /api/auth/google/callback` — Google redirects here with code. Exchange code for id_token/access token, verify `id_token` (email, email_verified), then:
>
>     * If user with same email exists:
>
>       * If user has `recruiter` role and `is_recruiter_verified=False`, deny recruiter access (403) and instruct to verify.
>       * Otherwise, sign them in and issue access + refresh tokens (create refresh token entry if not exists).
>     * If user does not exist:
>
>       * Create a new user with `roles=["candidate"]` by default and `accounts.google = { "sub": ..., "email": ... }`. If you detect the OAuth flow indicates recruiter intent (e.g., `state` parameter contains `role=recruiter` AND there's a valid invite for that email), create as `recruiter` and set `is_recruiter_verified` accordingly.
>   * For front-end flows: support `state` parameter encoding (e.g., `role=recruiter`) so the frontend can request recruiter login via Google. Explain in comments how to securely encode `state`.
> * Store minimal Google account info in `users.oauth.google` subdocument (`sub`, `email`, `picture`, `last_login`).
>
> ### Required endpoints & behaviors (updated)
>
> 1. `POST /api/auth/register` — candidate registration (email/password).
> 2. `POST /api/auth/register/recruiter` — recruiter registration with `invite_code` option (see above).
> 3. `POST /api/auth/login/candidate` — candidate login (email/password).
> 4. `POST /api/auth/login/recruiter` — recruiter login (email/password + invite_code optional).
> 5. `GET /api/auth/google/login?role=candidate|recruiter` — redirect to Google consent (role optional via `state`).
> 6. `GET /api/auth/google/callback` — handle OAuth callback, create/link user, issue tokens, respect recruiter verification rules.
> 7. `POST /api/auth/refresh` — refresh access token (refresh token in JSON body or cookie).
> 8. `POST /api/auth/logout` — revoke refresh token(s) (accept refresh_token or use cookie).
> 9. `POST /api/auth/recruiter/verify` — admin-only to set `is_recruiter_verified` for a user.
> 10. `GET /api/protected/me` — protected user info endpoint (role-aware).
>
> ### Data models & collections (explicit)
>
> * `users` document (include oauth subdoc and recruiter flag):
>
>   ```json
>   {
>     "_id": ObjectId,
>     "email": "string",
>     "name": "string",
>     "password_hash": "string | null",
>     "roles": ["candidate" | "recruiter" | "admin"],
>     "is_recruiter_verified": false,
>     "oauth": {
>         "google": { "sub": "string", "email": "string", "picture": "string", "last_login": datetime }
>     },
>     "created_at": datetime
>   }
>   ```
> * `refresh_tokens` document:
>
>   ```json
>   {
>     "_id": ObjectId,
>     "user_id": ObjectId,
>     "token": "string",         // opaque string or jti if using JWT
>     "expires_at": datetime,
>     "created_at": datetime,
>     "revoked": bool,
>     "device_info": {...}
>   }
>   ```
> * `recruiter_invites` document:
>
>   ```json
>   {
>     "email": "string",
>     "invite_code": "string",
>     "created_at": datetime,
>     "expires_at": datetime,
>     "created_by": ObjectId
>   }
>   ```
>
> ### Settings & `.env` (include Google)
>
> Use pydantic `BaseSettings`. `.env.example` must include:
>
> ```
> MONGODB_URI=
> MONGODB_DB=programming_pathshala
> JWT_SECRET_KEY=
> JWT_ALGORITHM=HS256
> ACCESS_TOKEN_EXPIRE_MINUTES=15
> REFRESH_TOKEN_EXPIRE_DAYS=7
> BCRYPT_ROUNDS=12
> BACKEND_CORS_ORIGINS=[]
> GOOGLE_CLIENT_ID=
> GOOGLE_CLIENT_SECRET=
> GOOGLE_OAUTH_REDIRECT_URI=  # e.g. http://localhost:8000/api/auth/google/callback
> ```
>
> ### Security & verification details (explicit)
>
> * Recruiter-specific restrictions: recruiter accounts cannot sign in (via password or Google) unless `is_recruiter_verified==True` OR a valid invite code was used during registration OAuth mapping. Clearly document admin verification flow.
> * On Google login with `role=recruiter` state, confirm there's either (a) a valid invite for the email OR (b) admin verification pending — do NOT auto-grant recruiter privileges without invite or admin approval.
> * For refresh tokens: implement rotation (issue new refresh, mark old as revoked) and persist tokens. Make rotation optional but recommend enabling it; include code to rotate by default.
>
> ### File structure to generate (same as before, add oauth & invites)
>
> ```
> backend/
> ├─ app/
> │  ├─ main.py
> │  ├─ config.py
> │  ├─ db.py
> │  ├─ models.py
> │  ├─ auth/
> │  │   ├─ routes.py
> │  │   ├─ schemas.py
> │  │   ├─ service.py
> │  │   ├─ deps.py
> │  │   └─ oauth.py        # google oauth client + callback handler
> │  ├─ admin/
> │  │   └─ routes.py      # recruiter verification endpoint
> │  └─ routes.py
> ├─ tests/
> │  ├─ test_auth.py
> │  ├─ test_google_oauth.py
> ├─ .env.example
> ├─ requirements.txt
> └─ README.md
> ```
>
> ### Tests to include (updated)
>
> * Candidate register & login.
> * Recruiter register with invite & login success.
> * Recruiter login blocked when not verified.
> * Google OAuth flow (mock exchange) for candidate: create new user and login.
> * Google OAuth for recruiter with `state=role=recruiter` and valid invite: create/verify recruiter and login.
> * Refresh & logout & token revocation.
>
> ### Deliverables & style
>
> * Output must be runnable.
> * Provide well-documented code and comments explaining recruiter verification security choices and OAuth `state` encoding/decoding.
> * Use type hints and Python 3.11+ idioms.
> * README: setup, how to create invite codes, how to test Google OAuth locally (use ngrok or explain how), and how to set `state` param to request recruiter flow.
>
> ### Final note
>
> After code, include a short explanation (6–10 bullets) describing:
>
> * how recruiter vs candidate flows differ,
> * how Google OAuth maps to internal users,
> * how invites and admin verification work,
> * refresh token rotation & revocation behavior,
> * how to switch to cookie-based refresh tokens safely.
>
> Now generate the full project files as earlier: each file in its own labeled code block, followed by `requirements.txt` and `README.md`. Focus on security, correctness, and good test coverage for the expanded flows.
