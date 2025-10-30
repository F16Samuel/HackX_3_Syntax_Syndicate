"""
Google OAuth integration using Authlib.
Handles OAuth flow, token exchange, and user verification.
"""
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from typing import Optional, Dict, Any
import base64
import json
import logging

from ..config import settings

logger = logging.getLogger(__name__)

# Initialize OAuth with Authlib
config = Config(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
})

oauth = OAuth(config)

# Register Google OAuth provider
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


class GoogleOAuthHandler:
    """Handler for Google OAuth operations."""
    
    @staticmethod
    def encode_state(role: Optional[str] = None, invite_code: Optional[str] = None) -> str:
        """
        Encode state parameter for OAuth flow.
        
        State parameter is used to:
        1. Prevent CSRF attacks (primary purpose)
        2. Pass additional context (role, invite_code) through OAuth flow
        
        Security: State should be verified on callback to prevent tampering.
        In production, consider signing the state with HMAC.
        """
        state_data = {}
        if role:
            state_data["role"] = role
        if invite_code:
            state_data["invite_code"] = invite_code
        
        # Base64 encode for URL safety
        state_json = json.dumps(state_data)
        state_b64 = base64.urlsafe_b64encode(state_json.encode()).decode()
        return state_b64
    
    @staticmethod
    def decode_state(state: str) -> Dict[str, Any]:
        """
        Decode state parameter from OAuth callback.
        
        Returns dictionary with role and invite_code if present.
        """
        try:
            state_json = base64.urlsafe_b64decode(state.encode()).decode()
            return json.loads(state_json)
        except Exception as e:
            logger.warning(f"Failed to decode state: {e}")
            return {}
    
    @staticmethod
    async def get_authorization_url(
        request,
        role: Optional[str] = None,
        invite_code: Optional[str] = None
    ) -> str:
        """
        Generate Google OAuth authorization URL.
        
        Args:
            request: Starlette request object
            role: Optional role to encode in state (candidate/recruiter)
            invite_code: Optional invite code for recruiter registration
        
        Returns:
            Authorization URL to redirect user to
        """
        # Encode state parameter
        state = GoogleOAuthHandler.encode_state(role, invite_code)
        
        # Generate authorization URL
        redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
        return await oauth.google.authorize_redirect(
            request,
            redirect_uri,
            state=state
        )
    
    @staticmethod
    async def handle_callback(request) -> Dict[str, Any]:
        """
        Handle OAuth callback from Google.
        
        Returns:
            Dictionary with user info and state data:
            {
                "sub": Google user ID,
                "email": user email,
                "name": user name,
                "picture": profile picture URL,
                "email_verified": bool,
                "state": decoded state dict
            }
        
        Raises:
            Exception: If token exchange fails or email not verified
        """
        # Exchange authorization code for tokens
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from ID token
        user_info = token.get('userinfo')
        if not user_info:
            raise ValueError("Failed to get user info from Google")
        
        # Verify email
        if not user_info.get('email_verified'):
            raise ValueError("Google email not verified")
        
        # Decode state parameter
        state_param = request.query_params.get('state', '')
        state_data = GoogleOAuthHandler.decode_state(state_param)
        
        return {
            "sub": user_info['sub'],
            "email": user_info['email'],
            "name": user_info.get('name', ''),
            "picture": user_info.get('picture'),
            "email_verified": user_info['email_verified'],
            "state": state_data
        }


# Export OAuth instance and handler
google_oauth_handler = GoogleOAuthHandler()