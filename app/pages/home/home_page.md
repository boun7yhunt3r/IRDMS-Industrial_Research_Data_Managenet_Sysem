<|layout|columns=1 10 1|gap=20px|
<|
|>
<|
|>
<|{logged_in_user}|button|on_action=toggle_user_menu|class_name=user-button|hover_text=Logged in as: {logged_in_user}|>
|>

<|menu|label=Menu|lov={menu_items}|on_action=menu_action|>

<|{user_menu_open}|dialog|on_action=close_user_menu|
**Logged in as:** 
<|{logged_in_user}|text|>
<br/>
<|Logout|button|on_action=logout|class_name=error fullwidth|>
|>

<|layout|columns=3 7|gap=20px|
<|{selected_item}|tree|lov={tree_data}|>
<|
|>
|>