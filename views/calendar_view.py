import streamlit as st
import pandas as pd

from database.task_repository import (
    get_tasks,
    create_task
)


def render_calendar():

    st.subheader("📆 Calendar View")

    tasks = get_tasks()

    if tasks:

        df = pd.DataFrame(
            [dict(t) for t in tasks]
        )

        if "plan_end" in df.columns:

            st.calendar = True

            st.dataframe(
                df[
                    [
                        "task_name",
                        "project",
                        "status",
                        "plan_start",
                        "plan_end"
                    ]
                ],
                use_container_width=True
            )

    col1, col2 = st.columns(
        [3,1]
    )

    with col2:

        st.markdown(
            "### Unscheduled Tasks"
        )

        task_name = st.text_input(
            "Task Name"
        )

        plan_date = st.date_input(
            "Due Date"
        )

        if st.button(
            "Add Task"
        ):

            create_task(
                category="General",
                project="Calendar",
                bucket_id=1,
                task_name=task_name,
                description="",
                priority="P2",
                plan_start=plan_date,
                plan_end=plan_date
            )

            st.rerun()