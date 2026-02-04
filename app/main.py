from taipy.gui import Gui, State, navigate, notify, Icon
from neo4j_viz import VisualizationGraph
import tempfile

from pages.home.home_page import home_md
from pages.login_page import root
from pages.user.user_page import user_md

from utils.keycloak_manager import KeycloakManager
from utils.shepard_connect import ShepardManager
from utils.logger import logger

login_open = True
access_token = None
username = ''
password = ''
logged_in_user = ''
tree_data = []
references = {}

# Initialize with a default empty graph instead of None
class NeoGraphWrapper:
    def __init__(self, nodes=None, relationships=None):
        self.viz = VisualizationGraph(nodes or [], relationships or [])

# Initialize with empty graph to prevent None errors
home_graph = NeoGraphWrapper([], [])

# Initialize managers
keycloak_manager = KeycloakManager()
# shepard_manager = ShepardManager() 

menu_items = [
    ("Home", Icon("images/home.gif", "Home")),
    ("User", Icon("images/settings.gif", "User")),
]

def login(state):
    keycloak_manager.login(state)
    if state.access_token:
        logger.info(f"******************************New Login******************************")
        logger.info(f"User successfully logged in : {state.logged_in_user}")
        shepard_manager = ShepardManager(access_token=state.access_token)
        state.tree_data, state.references = shepard_manager.build_tree_structure()
        nodes, relationships = shepard_manager.create_graph_from_data(state.tree_data, state.references)
        #logger.info(f"Nodes:", nodes, "Relationships:", relationships)
        # FIX: Create new graph instance and explicitly assign it
        state.home_graph = NeoGraphWrapper(nodes, relationships)
        # Force GUI update if needed
        notify(state, "success", "Graph loaded successfully")

def logout(state):
    keycloak_manager.logout(state)
    # Reset graph on logout
    state.home_graph = NeoGraphWrapper([], [])

# Called when a menu item is clicked
def menu_action(state: State, var_name: str, var_value: dict):
    selected_page = var_value["args"][0]         # "Home" / "Dashboard" / "Settings"
    session_on_navigate(state, selected_page)
    navigate(state, selected_page)               # Navigate to page

def session_on_navigate(state, page_name):
    """
    Navigation handler that intercepts page navigation.
    Checks session validity before allowing navigation to protected pages.
    """
    # Allow navigation to root/initial page without session check
    if page_name in ["/", "TaiPy_root_page"]:
        return page_name
    
    # For Home page - allow navigation but check session to show/hide login dialog
    if page_name == "Home":
        if state.access_token:  # Only rebuild if logged in
            shepard_manager = ShepardManager(access_token=state.access_token)
            state.tree_data, state.references = shepard_manager.build_tree_structure()
            
            # FIX: Rebuild the graph when navigating to Home
            nodes, relationships = shepard_manager.create_graph_from_data(state.tree_data, state.references)
            state.home_graph = NeoGraphWrapper(nodes, relationships)
        
        if not keycloak_manager.check_session_and_logout_if_expired(state):
            state.login_open = True
        return page_name
    
    # For all other pages, require valid session
    if not keycloak_manager.check_session_and_logout_if_expired(state):
        state.login_open = True
        return "/"
    
    return page_name

def render_neo_viz(wrapper: NeoGraphWrapper):
    # Get the HTML content from the visualization
    html_object = wrapper.viz.render(width="100%", height="600px")
    raw_html = html_object.data
    
    # Save to a temporary file and return the bytes (like the Folium example)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as temp_file:
        temp_file.write(raw_html)
        temp_file.flush()
        
        # Read back as bytes
        with open(temp_file.name, "rb") as f:
            return f.read()

pages = {
    "/": root,
    "Home": home_md,
    "User": user_md
}

if __name__ == "__main__":
    gui = Gui(pages=pages)
    gui.register_content_provider(NeoGraphWrapper, render_neo_viz)
    gui.run(title="IRDMS", port=5005, dark_mode=True, dev_mode=True)