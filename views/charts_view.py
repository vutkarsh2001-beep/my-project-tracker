import streamlit as st
import pandas as pd
import plotly.express as px

from database.task_repository import (
    get_tasks
)


def render_charts():

    st.subheader(
        "📈 Planner Analytics"
    )

    tasks = get_tasks()

    if not tasks:

        st.info(
            "No task data available."
        )

        return

    df = pd.DataFrame(
        [dict(t) for t in tasks]
    )

    col1, col2 = st.columns(2)

    with col1:

        status_chart = (
            df["status"]
            .value_counts()
            .reset_index()
        )

        status_chart.columns = [
            "Status",
            "Count"
        ]

        fig = px.pie(
            status_chart,
            names="Status",
            values="Count",
            title="Task Status Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        priority_chart = (
            df["priority"]
            .value_counts()
            .reset_index()
        )

        priority_chart.columns = [
            "Priority",
            "Count"
        ]

        fig2 = px.bar(
            priority_chart,
            x="Priority",
            y="Count",
            title="Priority Breakdown"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )