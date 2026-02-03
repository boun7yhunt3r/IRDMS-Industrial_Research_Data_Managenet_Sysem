from taipy.gui import Markdown
from utils.keycloak_manager import KeycloakManager
from utils.shepard_connect import ShepardManager

user_menu_open = False
selected_item = None
def toggle_user_menu(state):
    """Toggle the user menu dialog."""
    state.user_menu_open = not state.user_menu_open

def close_user_menu(state):
    """Close the user menu dialog."""
    state.user_menu_open = False

def logout(state):
    """Handle user logout."""
    state.user_menu_open = False  # Close the menu first
    keycloak_manager = KeycloakManager()
    keycloak_manager.logout(state)

home_md = Markdown("app/pages/home/home_page.md")