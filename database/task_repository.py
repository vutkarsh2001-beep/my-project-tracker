from database.db import get_connection
from datetime import date


def get_tasks():

    conn = get_connection()

    rows = conn.execute("""
    SELECT
        t.*,
        b.bucket_name
    FROM tasks t
    LEFT JOIN buckets b
        ON t.bucket_id = b.id
    """).fetchall()

    conn.close()

    return rows


def get_task_by_id(task_id):

    conn = get_connection()

    task = conn.execute(
        """
        SELECT *
        FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    ).fetchone()

    conn.close()

    return task


def create_task(
    category,
    project,
    bucket_id,
    task_name,
    description,
    priority,
    plan_start,
    plan_end
):

    conn = get_connection()

    conn.execute("""
    INSERT INTO tasks(
        category,
        project,
        bucket_id,
        task_name,
        description,
        priority,
        status,
        plan_start,
        plan_end
    )
    VALUES(?,?,?,?,?,?,?,?,?)
    """,
    (
        category,
        project,
        bucket_id,
        task_name,
        description,
        priority,
        "Not Started",
        plan_start,
        plan_end
    ))

    conn.commit()
    conn.close()


def update_task_status(
    task_id,
    new_status
):

    conn = get_connection()

    closure_date = None

    if new_status == "Completed":
        closure_date = str(date.today())

    conn.execute("""
    UPDATE tasks
    SET
        status=?,
        closure_date=?
    WHERE id=?
    """,
    (
        new_status,
        closure_date,
        task_id
    ))

    conn.commit()
    conn.close()

def update_task_details(
    task_id,
    description,
    priority,
    status
):

    conn = get_connection()

    closure_date = None

    if status == "Completed":
        closure_date = str(date.today())

    conn.execute(
        """
        UPDATE tasks
        SET
            description=?,
            priority=?,
            status=?,
            closure_date=?
        WHERE id=?
        """,
        (
            description,
            priority,
            status,
            closure_date,
            task_id
        )
    )

    conn.commit()
    conn.close()
