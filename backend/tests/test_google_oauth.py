'''"""
Tests for Google OAuth integration.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


class TestGoogleOAuth:
    """Test Google OAuth flow."""
    
    @pytest.mark.asyncio
    async def test_google_login_redirect(self, client: AsyncClient):
        """Test Google OAuth initiation redirects to Google."""
        with patch('app.auth.oauth.oauth.google.authorize_redirect') as mock_auth:
            mock_auth.return_value = "https://accounts.google.com/o/oauth2/auth?..."
            
            response = await client.get(
                "/api/auth/google/login?role=candidate",
                follow_redirects=False
            )
            
            # Should redirect
            assert response.status_code in [200, 307, 302]
    
    @pytest.mark.asyncio
    async def test_google_callback_new_candidate(self, client: AsyncClient, db):
        """Test Google OAuth callback creating new candidate user."""
        mock_user_info = {
            'sub': 'google_user_123',
            'email': 'newuser@gmail.com',
            'email_verified': True,
            'name': 'New Google User',
            'picture': 'https://example.com/photo.jpg'
        }
        
        with patch('app.auth.oauth.oauth.google.authorize_access_token') as mock_token:
            mock_token.return_value = {'userinfo': mock_user_info}
            
            # Simulate callback with state
            from app.auth.oauth import GoogleOAuthHandler
            state = GoogleOAuthHandler.encode_state(role='candidate')
            
            response = await client.get(
                f"/api/auth/google/callback?code=test_code&state={state}"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["user"]["email"] == "newuser@gmail.com"
            assert "candidate" in data["user"]["roles"]
            
            # Verify user created in database
            user = await db.users.find_one({"email": "newuser@gmail.com"})
            assert user is not None
            assert user["oauth"]["google"]["sub"] == "google_user_123"
    
    @pytest.mark.asyncio
    async def test_google_callback_new_recruiter_with_invite(
        self,
        client: AsyncClient,
        db,
        valid_invite
    ):
        """Test Google OAuth creating new recruiter with valid invite."""
        mock_user_info = {
            'sub': 'google_recruiter_456',
            'email': 'newhire@test.com',  # Matches invite email
            'email_verified': True,
            'name': 'New Recruiter',
            'picture': None
        }
        
        with patch('app.auth.oauth.oauth.google.authorize_access_token') as mock_token:
            mock_token.return_value = {'userinfo': mock_user_info}
            
            # Create state with recruiter role and invite
            from app.auth.oauth import GoogleOAuthHandler
            state = GoogleOAuthHandler.encode_state(
                role='recruiter',
                invite_code='VALID_CODE_123'
            )
            
            response = await client.get(
                f"/api/auth/google/callback?code=test_code&state={state}"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "recruiter" in data["user"]["roles"]
            
            # Verify user is verified recruiter
            user = await db.users.find_one({"email": "newhire@test.com"})
            assert user["is_recruiter_verified"] is True
            assert "recruiter" in user["roles"]
            
            # Verify invite was consumed
            invite = await db.recruiter_invites.find_one({"invite_code": "VALID_CODE_123"})
            assert invite is None
    
    @pytest.mark.asyncio
    async def test_google_callback_recruiter_without_invite_defaults_to_candidate(
        self,
        client: AsyncClient,
        db
    ):
        """Test Google OAuth with recruiter role but no invite creates candidate."""
        mock_user_info = {
            'sub': 'google_user_789',
            'email': 'noinvite@test.com',
            'email_verified': True,
            'name': 'No Invite User',
            'picture': None
        }
        
        with patch('app.auth.oauth.oauth.google.authorize_access_token') as mock_token:
            mock_token.return_value = {'userinfo': mock_user_info}
            
            # Request recruiter role without valid invite
            from app.auth.oauth import GoogleOAuthHandler
            state = GoogleOAuthHandler.encode_state(role='recruiter')
            
            response = await client.get(
                f"/api/auth/google/callback?code=test_code&state={state}"
            )
            
            assert response.status_code == 200
            data = response.json()
            # Should default to candidate
            assert "candidate" in data["user"]["roles"]
            assert "recruiter" not in data["user"]["roles"]
    
    @pytest.mark.asyncio
    async def test_google_callback_existing_user(
        self,
        client: AsyncClient,
        sample_candidate,
        db
    ):
        """Test Google OAuth callback with existing user links account."""
        mock_user_info = {
            'sub': 'google_existing_123',
            'email': 'candidate@test.com',  # Existing user
            'email_verified': True,
            'name': 'Test Candidate',
            'picture': None
        }
        
        with patch('app.auth.oauth.oauth.google.authorize_access_token') as mock_token:
            mock_token.return_value = {'userinfo': mock_user_info}
            
            from app.auth.oauth import GoogleOAuthHandler
            state = GoogleOAuthHandler.encode_state()
            
            response = await client.get(
                f"/api/auth/google/callback?code=test_code&state={state}"
            )
            
            assert response.status_code == 200
            
            # Verify Google account linked
            user = await db.users.find_one({"email": "candidate@test.com"})
            assert user["oauth"]["google"]["sub"] == "google_existing_123"
    
    @pytest.mark.asyncio
    async def test_google_callback_unverified_email_rejected(
        self,
        client: AsyncClient
    ):
        """Test Google OAuth rejects unverified email."""
        mock_user_info = {
            'sub': 'google_unverified_999',
            'email': 'unverified@test.com',
            'email_verified': False,  # Not verified
            'name': 'Unverified User'
        }
        
        with patch('app.auth.oauth.oauth.google.authorize_access_token') as mock_token:
            mock_token.return_value = {'userinfo': mock_user_info}
            
            response = await client.get(
                "/api/auth/google/callback?code=test_code&state=e30="  # Empty state
            )
            
            assert response.status_code == 500
            assert "not verified" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_google_callback_existing_unverified_recruiter_blocked(
        self,
        client: AsyncClient,
        sample_recruiter_unverified,
        db
    ):
        """Test existing unverified recruiter cannot login via OAuth without invite."""
        mock_user_info = {
            'sub': 'google_recruiter_blocked',
            'email': 'recruiter@test.com',  # Existing unverified recruiter
            'email_verified': True,
            'name': 'Test Recruiter'
        }
        
        with patch('app.auth.oauth.oauth.google.authorize_access_token') as mock_token:
            mock_token.return_value = {'userinfo': mock_user_info}
            
            from app.auth.oauth import GoogleOAuthHandler
            state = GoogleOAuthHandler.encode_state()
            
            response = await client.get(
                f"/api/auth/google/callback?code=test_code&state={state}"
            )
            
            # Should be blocked due to unverified status
            assert response.status_code == 403
            assert "pending verification" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_state_encoding_decoding(self):
        """Test OAuth state parameter encoding and decoding."""
        from app.auth.oauth import GoogleOAuthHandler
        
        # Test with role only
        state1 = GoogleOAuthHandler.encode_state(role='recruiter')
        decoded1 = GoogleOAuthHandler.decode_state(state1)
        assert decoded1['role'] == 'recruiter'
        
        # Test with role and invite
        state2 = GoogleOAuthHandler.encode_state(
            role='recruiter',
            invite_code='TEST123'
        )
        decoded2 = GoogleOAuthHandler.decode_state(state2)
        assert decoded2['role'] == 'recruiter'
        assert decoded2['invite_code'] == 'TEST123'
        
        # Test empty state
        state3 = GoogleOAuthHandler.encode_state()
        decoded3 = GoogleOAuthHandler.decode_state(state3)
        assert decoded3 == {}'''