from taipy.gui import Gui, notify
from pages.home.home_page import home_md
from pages.login_page import root

login_open = True
username = ''
password = ''

def create_account(state):
    notify(state, "info", "Creating account...")
    # Put your own logic to create an account
    # Maybe, by opening another dialog
    state.username = "Taipy"
    state.password = "password"
    notify(state, "success", "Account created!")


def login(state):
    if state.username == "Taipy" and state.password == "password":
        state.login_open = False
        notify(state, "success", "Logged in!")
    else:
        notify(state, "error", "Wrong username or password!")


pages = {"/": root,
         "Home": home_md}

if __name__ == "__main__":
    Gui(pages=pages).run()