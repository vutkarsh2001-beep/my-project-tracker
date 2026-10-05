from database.db import get_connection


def get_checklist(task_id):

    conn = get_connection()

    rows = conn.execute("""
    SELECT *
    FROM checklist_items
    WHERE task_id=?
    """,
    (task_id,)
    ).fetchall()

    conn.close()

    return rows


def create_checklist_item(
    task_id,
    item_name
):

    conn = get_connection()

    conn.execute("""
    INSERT INTO checklist_items(
        task_id,
        item_name
    )
    VALUES(?,?)
    """,
    (
        task_id,
        item_name
    ))

    conn.commit()
    conn.close()