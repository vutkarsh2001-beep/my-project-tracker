from database.db import get_connection


def get_buckets(project_id):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM buckets
        WHERE project_id=?
        ORDER BY display_order
        """,
        (project_id,)
    ).fetchall()

    conn.close()

    return rows


def create_bucket(
    project_id,
    bucket_name
):

    conn = get_connection()

    existing = conn.execute(
        """
        SELECT COUNT(*)
        FROM buckets
        WHERE project_id=?
        AND bucket_name=?
        """,
        (
            project_id,
            bucket_name
        )
    ).fetchone()[0]

    if existing > 0:

        conn.close()

        return False

    order_value = conn.execute(
        """
        SELECT COALESCE(MAX(display_order),0)+1
        FROM buckets
        WHERE project_id=?
        """,
        (project_id,)
    ).fetchone()[0]

    conn.execute(
        """
        INSERT INTO buckets(
            project_id,
            bucket_name,
            display_order
        )
        VALUES(?,?,?)
        """,
        (
            project_id,
            bucket_name,
            order_value
        )
    )

    conn.commit()
    conn.close()

    return True


def rename_bucket(
    project_id,
    bucket_id,
    new_name
):

    conn = get_connection()

    existing = conn.execute(
        """
        SELECT COUNT(*)
        FROM buckets
        WHERE project_id=?
        AND bucket_name=?
        AND id<>?
        """,
        (
            project_id,
            new_name,
            bucket_id
        )
    ).fetchone()[0]

    if existing > 0:

        conn.close()

        return False

    conn.execute(
        """
        UPDATE buckets
        SET bucket_name=?
        WHERE id=?
        """,
        (
            new_name,
            bucket_id
        )
    )

    conn.commit()
    conn.close()

    return True


def delete_bucket(bucket_id):

    conn = get_connection()

    conn.execute(
        """
        DELETE FROM buckets
        WHERE id=?
        """,
        (bucket_id,)
    )

    conn.commit()
    conn.close()


def move_bucket_left(bucket_id):

    conn = get_connection()

    buckets = conn.execute(
        """
        SELECT *
        FROM buckets
        ORDER BY display_order
        """
    ).fetchall()

    for i, bucket in enumerate(buckets):

        if bucket["id"] == bucket_id:

            if i == 0:
                conn.close()
                return

            left_bucket = buckets[i - 1]

            current_order = bucket["display_order"]

            left_order = left_bucket["display_order"]

            conn.execute(
                """
                UPDATE buckets
                SET display_order=?
                WHERE id=?
                """,
                (
                    left_order,
                    bucket_id
                )
            )

            conn.execute(
                """
                UPDATE buckets
                SET display_order=?
                WHERE id=?
                """,
                (
                    current_order,
                    left_bucket["id"]
                )
            )

            break

    conn.commit()
    conn.close()


def move_bucket_right(bucket_id):

    conn = get_connection()

    buckets = conn.execute(
        """
        SELECT *
        FROM buckets
        ORDER BY display_order
        """
    ).fetchall()

    for i, bucket in enumerate(buckets):

        if bucket["id"] == bucket_id:

            if i == len(buckets) - 1:
                conn.close()
                return

            right_bucket = buckets[i + 1]

            current_order = bucket["display_order"]

            right_order = right_bucket["display_order"]

            conn.execute(
                """
                UPDATE buckets
                SET display_order=?
                WHERE id=?
                """,
                (
                    right_order,
                    bucket_id
                )
            )

            conn.execute(
                """
                UPDATE buckets
                SET display_order=?
                WHERE id=?
                """,
                (
                    current_order,
                    right_bucket["id"]
                )
            )

            break

    conn.commit()
    conn.close()
