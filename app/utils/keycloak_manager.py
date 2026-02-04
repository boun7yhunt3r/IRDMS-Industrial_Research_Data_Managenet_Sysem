from keycloak import KeycloakOpenID
from neo4j_viz import VisualizationGraph
from taipy.gui import Gui, notify
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize with a default empty graph instead of None
class NeoGraphWrapper:
    def __init__(self, nodes=None, relationships=None):
        self.viz = VisualizationGraph(nodes or [], relationships or [])

# Initialize with empty graph to prevent None errors

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
    
    def check_login_with_keycloak(self, username, password, state):
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
            userinfo = self.keycloak_client.userinfo(token['access_token'])
            state.logged_in_user = userinfo.get('name')
            return token
        except Exception:
            return None

    def is_token_valid(self, access_token):
        if not access_token:
            return False
        
        try:
            # Use userinfo instead of introspect for public clients
            userinfo = self.keycloak_client.userinfo(access_token)
            return True
        except Exception as e:
            return False
        
    def check_session_and_logout_if_expired(self, state):
        """
        Check if user session is still valid. If expired, log them out.
        Call this method on user interactions to verify session validity.
        
        Args:
            state: Taipy state object
            
        Returns:
            bool: True if session is valid, False if expired and logged out
        """
        # If user is not logged in, nothing to check
        if state.login_open or not state.access_token:
            return False
        
        # Check if token is still valid
        if not self.is_token_valid(state.access_token):
            # Token expired, log user out
            state.login_open = True
            state.access_token = None
            state.username = ""
            state.password = ""
            notify(state, "warning", "Your session has expired. Please log in again.")
            return False
        
        return True
        
    def login(self, state):
        """Handle user login using Keycloak."""
        token = self.check_login_with_keycloak(state.username, state.password,state)

        if token:
            state.login_open = False
            state.access_token = token["access_token"]
            notify(state, "success", "Logged in successfully!")
        else:
            notify(state, "error", "Invalid username or password!")

    def logout(self, state):
        """Reset session and return user to login page."""
        state.login_open = True
        state.access_token = None
        state.username = ""
        state.password = ""
        state.logged_in_user = ""
        state.tree_data = []
        state.references = {}
        state.home_graph = NeoGraphWrapper([], [])
        notify(state, "success", "You have been logged out!")