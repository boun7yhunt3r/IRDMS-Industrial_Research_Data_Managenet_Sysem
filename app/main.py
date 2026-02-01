from taipy.gui import Gui, navigate, notify
from pages.home.home_page import home_md
from pages.login_page import root
from pages.user.user_page import user_md
from utils.keycloak_manager import KeycloakManager

login_open = True
access_token = None
username = ''
password = ''

# Initialize KeycloakManager once
keycloak_manager = KeycloakManager()


def login(state):
    keycloak_manager.login(state)

def logout(state):
    keycloak_manager.logout(state)

def on_navigate(state, page_name):
    """
    Navigation handler that intercepts page navigation.
    Checks session validity before allowing navigation to protected pages.
    """
    # Allow navigation to root/initial page without session check
    if page_name in ["/", "TaiPy_root_page"]:
        return page_name
    
    # For Home page - allow navigation but check session to show/hide login dialog
    if page_name == "Home":
        if not keycloak_manager.check_session_and_logout_if_expired(state):
            state.login_open = True
        return page_name
    
    # For all other pages, require valid session
    if not keycloak_manager.check_session_and_logout_if_expired(state):
        state.login_open = True
        return "/"
    
    return page_name

pages = {
    "/": root,
    "Home": home_md,
    "User": user_md
}

if __name__ == "__main__":
    gui = Gui(pages=pages)
    gui.run(title="IRDMS", port=5005, dark_mode=True, dev_mode=True)