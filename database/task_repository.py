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
