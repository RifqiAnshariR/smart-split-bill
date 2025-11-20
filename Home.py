import streamlit as st
from config.config import Config
from utils.styling import load_css


st.set_page_config(
    page_title=f"{Config.APP_PAGE_TITLE} - Home", 
    page_icon=Config.APP_PAGE_ICON, 
    layout=Config.APP_LAYOUT, 
    menu_items=Config.APP_MENU_ITEMS
)


load_css()


st.title(Config.APP_PAGE_TITLE)

st.subheader("Hello...")
st.write("This site helps you split the bill evenly or by items.")

st.html("<div class='footer'>©2025 Rifqi Anshari Rasyid.</div>")
