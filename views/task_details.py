import streamlit as st

from database.task_repository import (
    get_task_by_id,
    update_task_details
)

from database.checklist_repository import (
    get_checklist,
    create_checklist_item
)


def render_task_details(task_id):

    task = get_task_by_id(task_id)

    if not task:
        return

    st.markdown("---")

    st.subheader("Task Details")

    st.text_input(
        "Task Name",
        value=task["task_name"],
        disabled=True
    )

    description = st.text_area(
        "Description",
        value=task["description"] or ""
    )

    priorities = ["P1", "P2", "P3"]

    current_priority = (
        task["priority"]
        if task["priority"] in priorities
        else "P2"
    )

    priority = st.selectbox(
        "Priority",
        priorities,
        index=priorities.index(current_priority)
    )

    statuses = [
        "Not Started",
        "In Progress",
        "Completed"
    ]

    current_status = (
        task["status"]
        if task["status"] in statuses
        else "Not Started"
    )

    status = st.selectbox(
        "Status",
        statuses,
        index=statuses.index(current_status)
    )

    st.text_input(
        "Closure Date",
        value=task["closure_date"] or "",
        disabled=True
    )

    if st.button(
        "Save Changes",
        key=f"save_{task_id}"
    ):

        update_task_details(
            task_id,
            description,
            priority,
            status
        )

        st.success(
            "Task updated."
        )

        st.rerun()

    st.markdown("### Checklist")

    checklist_items = get_checklist(task_id)

    for item in checklist_items:

        st.checkbox(
            item["item_name"],
            value=bool(item["completed"]),
            disabled=True,
            key=f"item_{item['id']}"
        )

    new_item = st.text_input(
        "New Checklist Item",
        key=f"new_check_{task_id}"
    )

    if st.button(
        "Add Checklist Item",
        key=f"add_check_{task_id}"
    ):

        if new_item.strip():

            create_checklist_item(
                task_id,
                new_item
            )

            st.rerun()