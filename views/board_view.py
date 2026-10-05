import streamlit as st

from views.task_details import (
    render_task_details
)

from database.bucket_repository import (
    get_buckets,
    create_bucket
)

from database.task_repository import (
    get_tasks,
    create_task
)


def render_board():

    st.subheader("Planner Board")

    col1, col2 = st.columns([3, 1])

    with col1:
        bucket_name = st.text_input(
            "Create Bucket"
        )

    with col2:

        st.write("")

        if st.button("Add Bucket"):

            if bucket_name.strip():

                create_bucket(
                    bucket_name
                )

                st.rerun()

    buckets = get_buckets()

    if not buckets:

        st.info(
            "Create your first bucket."
        )

        return

    tasks = get_tasks()

    board_columns = st.columns(
        len(buckets)
    )

    for col, bucket in zip(
        board_columns,
        buckets
    ):

        with col:

            st.markdown(
                f"### {bucket['bucket_name']}"
            )

            bucket_tasks = [
                t for t in tasks
                if t["bucket_id"] == bucket["id"]
            ]

            for task in bucket_tasks:

                clicked = st.button(
                    task["task_name"],
                    key=f"task_{task['id']}"
                )

                if clicked:

                    st.session_state[
                        "selected_task"
                    ] = task["id"]

            with st.expander(
                "➕ Add Task"
            ):

                task_name = st.text_input(
                    "Task Name",
                    key=f"name_{bucket['id']}"
                )

                project = st.text_input(
                    "Project",
                    key=f"project_{bucket['id']}"
                )

                category = st.text_input(
                    "Category",
                    key=f"category_{bucket['id']}"
                )

                priority = st.selectbox(
                    "Priority",
                    ["P1", "P2", "P3"],
                    key=f"priority_{bucket['id']}"
                )

                plan_start = st.date_input(
                    "Start Date",
                    key=f"start_{bucket['id']}"
                )

                plan_end = st.date_input(
                    "End Date",
                    key=f"end_{bucket['id']}"
                )

                if st.button(
                    "Create Task",
                    key=f"create_{bucket['id']}"
                ):

                    create_task(
                        category,
                        project,
                        bucket["id"],
                        task_name,
                        "",
                        priority,
                        plan_start,
                        plan_end
                    )

                    st.rerun()
