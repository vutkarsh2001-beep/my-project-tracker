import streamlit as st

from database.db import initialize_database

initialize_database()

st.set_page_config(
    page_title="Microsoft Planner Clone",
    layout="wide"
)

st.title("📋 Microsoft Planner Enterprise Workspace")

tab_board, tab_grid, tab_gantt = st.tabs(
    [
        "📊 Board",
        "📝 Grid",
        "📅 Gantt"
    ]
)

with tab_board:
    st.info(
        "Board View coming in next module"
    )

with tab_grid:
    st.info(
        "Grid View coming in next module"
    )

with tab_gantt:
    st.info(
        "Gantt View coming in next module"
    )