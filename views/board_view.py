import streamlit as st

from views.task_details import (
    render_task_details
)

from database.project_repository import (
    get_projects,
    create_project
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

    projects = get_projects()

    if not projects:

        st.info(
            "No projects found."
        )

        return

    project_names = [
        p["project_name"]
        for p in projects
    ]

    selected_project_name = st.selectbox(
        "Project",
        project_names
    )

    selected_project = next(
        p
        for p in projects
        if p["project_name"]
        == selected_project_name
    )

    project_id = selected_project["id"]

    st.markdown("### Create Project")

    new_project = st.text_input(
        "Project Name"
    )

    if st.button("Add Project"):

        if new_project.strip():

            success = create_project(
                new_project
            )

            if success:

                st.success(
                    "Project created."
                )

                st.rerun()

            else:

                st.error(
                    "Project name already exists."
                )

    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col1:

        bucket_name = st.text_input(
            "Create Bucket"
        )

    with col2:

        st.write("")

        if st.button("Add Bucket"):

            if bucket_name.strip():

                success = create_bucket(
                    project_id,
                    bucket_name
                )

                if success:

                    st.rerun()

                else:

                    st.error(
                        "Two buckets can't share same name in a Project."
                    )

    buckets = get_buckets(
        project_id
    )

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
                t
                for t in tasks
                if t["bucket_id"]
                == bucket["id"]
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
                        selected_project_name,
                        bucket["id"],
                        task_name,
                        "",
                        priority,
                        plan_start,
                        plan_end
                    )

                    st.rerun()

    if "selected_task" in st.session_state:

        render_task_details(
            st.session_state[
                "selected_task"
            ]
        )
