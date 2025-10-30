"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient


class TestCandidateRegistration:
    """Test candidate registration flow."""
    
    @pytest.mark.asyncio
    async def test_register_candidate_success(self, client: AsyncClient):
        """Test successful candidate registration."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "newcandidate@test.com",
                "password": "SecurePass123",
                "name": "New Candidate"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, sample_candidate):
        """Test registration with duplicate email."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "candidate@test.com",
                "password": "SecurePass123",
                "name": "Duplicate User"
            }
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "weak@test.com",
                "password": "weak",
                "name": "Weak Password User"
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestRecruiterRegistration:
    """Test recruiter registration flow."""
    
    @pytest.mark.asyncio
    async def test_register_recruiter_with_valid_invite(
        self,
        client: AsyncClient,
        valid_invite
    ):
        """Test successful recruiter registration with invite code."""
        response = await client.post(
            "/api/auth/register/recruiter",
            json={
                "email": "newhire@test.com",
                "password": "SecurePass123",
                "name": "New Recruiter",
                "invite_code": "VALID_CODE_123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_register_recruiter_invalid_invite(self, client: AsyncClient):
        """Test recruiter registration with invalid invite code."""
        response = await client.post(
            "/api/auth/register/recruiter",
            json={
                "email": "invalid@test.com",
                "password": "SecurePass123",
                "name": "Invalid Invite",
                "invite_code": "INVALID_CODE"
            }
        )
        
        assert response.status_code == 400
        assert "Invalid or expired invite code" in response.json()["detail"]


class TestCandidateLogin:
    """Test candidate login flow."""
    
    @pytest.mark.asyncio
    async def test_login_candidate_success(self, client: AsyncClient, sample_candidate):
        """Test successful candidate login."""
        response = await client.post(
            "/api/auth/login/candidate",
            json={
                "email": "candidate@test.com",
                "password": "TestPass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_login_candidate_wrong_password(
        self,
        client: AsyncClient,
        sample_candidate
    ):
        """Test candidate login with wrong password."""
        response = await client.post(
            "/api/auth/login/candidate",
            json={
                "email": "candidate@test.com",
                "password": "WrongPassword123"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_candidate_nonexistent(self, client: AsyncClient):
        """Test candidate login with nonexistent email."""
        response = await client.post(
            "/api/auth/login/candidate",
            json={
                "email": "nonexistent@test.com",
                "password": "SomePass123"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]


class TestRecruiterLogin:
    """Test recruiter login flow."""
    
    @pytest.mark.asyncio
    async def test_login_verified_recruiter_success(
        self,
        client: AsyncClient,
        sample_recruiter_verified
    ):
        """Test successful login for verified recruiter."""
        response = await client.post(
            "/api/auth/login/recruiter",
            json={
                "email": "recruiter.verified@test.com",
                "password": "TestPass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_login_unverified_recruiter_blocked(
        self,
        client: AsyncClient,
        sample_recruiter_unverified
    ):
        """Test that unverified recruiter cannot login without invite."""
        response = await client.post(
            "/api/auth/login/recruiter",
            json={
                "email": "recruiter@test.com",
                "password": "TestPass123"
            }
        )
        
        assert response.status_code == 403
        assert "pending verification" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_unverified_recruiter_with_invite(
        self,
        client: AsyncClient,
        sample_recruiter_unverified,
        db
    ):
        """Test unverified recruiter can login with valid invite code."""
        # Create invite for the unverified recruiter
        from datetime import datetime, timedelta
        await db.recruiter_invites.insert_one({
            "email": "recruiter@test.com",
            "invite_code": "VERIFY_CODE_456",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=7)
        })
        
        response = await client.post(
            "/api/auth/login/recruiter",
            json={
                "email": "recruiter@test.com",
                "password": "TestPass123",
                "invite_code": "VERIFY_CODE_456"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        
        # Verify user is now verified
        user = await db.users.find_one({"email": "recruiter@test.com"})
        assert user["is_recruiter_verified"] is True


class TestTokenRefresh:
    """Test token refresh flow."""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, sample_candidate):
        """Test successful token refresh."""
        # Login to get tokens
        login_response = await client.post(
            "/api/auth/login/candidate",
            json={
                "email": "candidate@test.com",
                "password": "TestPass123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        # New refresh token should be different (rotation)
        assert data["refresh_token"] != refresh_token
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token_12345"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_refresh_token_reuse_blocked(self, client: AsyncClient, sample_candidate):
        """Test that refresh token cannot be reused after rotation."""
        # Login
        login_response = await client.post(
            "/api/auth/login/candidate",
            json={
                "email": "candidate@test.com",
                "password": "TestPass123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # First refresh (should work)
        response1 = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response1.status_code == 200
        
        # Try to reuse old token (should fail)
        response2 = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response2.status_code == 401


class TestLogout:
    """Test logout flow."""
    
    @pytest.mark.asyncio
    async def test_logout_specific_token(
        self,
        client: AsyncClient,
        sample_candidate,
        candidate_token
    ):
        """Test logout with specific refresh token."""
        # Login to get refresh token
        login_response = await client.post(
            "/api/auth/login/candidate",
            json={
                "email": "candidate@test.com",
                "password": "TestPass123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Logout
        response = await client.post(
            "/api/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {candidate_token}"}
        )
        
        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]
        
        # Try to use revoked token (should fail)
        refresh_response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_logout_all_devices(
        self,
        client: AsyncClient,
        sample_candidate,
        candidate_token
    ):
        """Test logout from all devices."""
        # Create multiple sessions
        for _ in range(3):
            await client.post(
                "/api/auth/login/candidate",
                json={
                    "email": "candidate@test.com",
                    "password": "TestPass123"
                }
            )
        
        # Logout without refresh_token (logout all)
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {candidate_token}"}
        )
        
        assert response.status_code == 200
        # Should have logged out from multiple devices
        assert "device(s)" in response.json()["message"]


class TestProtectedEndpoints:
    """Test protected endpoint access."""
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token."""
        response = await client.get("/api/protected/me")
        assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_valid_token(
        self,
        client: AsyncClient,
        candidate_token
    ):
        """Test accessing protected endpoint with valid token."""
        response = await client.get(
            "/api/protected/me",
            headers={"Authorization": f"Bearer {candidate_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "candidate@test.com"
        assert "candidate" in data["roles"]
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """Test accessing protected endpoint with invalid token."""
        response = await client.get(
            "/api/protected/me",
            headers={"Authorization": "Bearer invalid_token_xyz"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_recruiter_endpoint_requires_verification(
        self,
        client: AsyncClient,
        sample_recruiter_unverified,
        db
    ):
        """Test that recruiter endpoints require verification."""
        from app.auth.service import AuthService
        auth_service = AuthService(db)
        
        # Create token for unverified recruiter
        token = auth_service.create_access_token(
            str(sample_recruiter_unverified["_id"]),
            ["recruiter"]
        )
        
        response = await client.get(
            "/api/protected/recruiter/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "not verified" in response.json()["detail"]


class TestAdminEndpoints:
    """Test admin endpoints."""
    
    @pytest.mark.asyncio
    async def test_verify_recruiter_as_admin(
        self,
        client: AsyncClient,
        admin_token,
        sample_recruiter_unverified,
        db
    ):
        """Test admin can verify recruiter."""
        response = await client.post(
            "/api/auth/recruiter/verify",
            json={
                "email": "recruiter@test.com",
                "verified": True
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert "verified" in response.json()["message"]
        
        # Check database
        user = await db.users.find_one({"email": "recruiter@test.com"})
        assert user["is_recruiter_verified"] is True
    
    @pytest.mark.asyncio
    async def test_verify_recruiter_without_admin(
        self,
        client: AsyncClient,
        candidate_token,
        sample_recruiter_unverified
    ):
        """Test non-admin cannot verify recruiter."""
        response = await client.post(
            "/api/auth/recruiter/verify",
            json={
                "email": "recruiter@test.com",
                "verified": True
            },
            headers={"Authorization": f"Bearer {candidate_token}"}
        )
        
        assert response.status_code == 403
        assert "Admin privileges required" in response.json()["detail"]