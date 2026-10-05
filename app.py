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
        "📅 Gantt",
	"📆 Calendar",
	"📈 Charts"
    ]
)

from views.board_view import (
    render_board
)

from views.calendar_view import (
    render_calendar
)

from views.charts_view import (
    render_charts
)
with tab_board:
    render_board()

with tab_grid:
    st.info(
        "Grid View coming in next module"
    )

with tab_gantt:
    st.info(
        "Gantt View coming in next module"
    )
with tab_calendar:
    render_calendar()
 
with tab_charts:
    render_charts()
