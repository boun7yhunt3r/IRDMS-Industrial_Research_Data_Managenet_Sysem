from taipy.gui import Gui, notify

from pages.home.home_page import home_md
from pages.login_page import root
from utils.keycloak_manager import KeycloakManager

login_open = True
access_token = None
username = ''
password = ''

# Initialize KeycloakManager once
keycloak_manager = KeycloakManager()


def login(state):
    """Handle user login using KeycloakManager."""
    token = keycloak_manager.check_login_with_keycloak(state.username, state.password)

    if token:
        state.login_open = False
        state.access_token = token["access_token"]
        notify(state, "success", f"Logged in successfully!")
    else:
        notify(state, "error", "Invalid username or password!")


pages = {
    "/": root,
    "Home": home_md
}

if __name__ == "__main__":
    Gui(pages=pages).run()