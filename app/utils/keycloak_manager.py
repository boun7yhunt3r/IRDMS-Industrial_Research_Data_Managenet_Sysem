from keycloak import KeycloakOpenID
from dotenv import load_dotenv
import os

load_dotenv()


class KeycloakManager:
    """Manages Keycloak authentication."""
    
    def __init__(self):
        self.keycloak_url = os.getenv("KEYCLOAK_URL")
        self.realm = os.getenv("KEYCLOAK_REALM")
        self.client_id = os.getenv("KEYCLOAK_CLIENT_ID")
        self.client_secret = None  # Public client
        
        self.keycloak_client = KeycloakOpenID(
            server_url=f"{self.keycloak_url}/",
            client_id=self.client_id,
            realm_name=self.realm,
            client_secret_key=self.client_secret,
        )
    
    def check_login_with_keycloak(self, username, password):
        """
        Authenticate user with Keycloak.
        
        Args:
            username (str): User's username
            password (str): User's password
            
        Returns:
            dict or None: Token dictionary if successful, None otherwise
        """
        try:
            token = self.keycloak_client.token(username, password)
            return token
        except Exception:
            return None