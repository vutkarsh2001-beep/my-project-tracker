from database.db import get_connection


def get_buckets():

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM buckets
        ORDER BY display_order
        """
    ).fetchall()

    conn.close()

    return rows


def create_bucket(bucket_name):

    conn = get_connection()

    order_value = conn.execute(
        """
        SELECT COALESCE(MAX(display_order),0)+1
        FROM buckets
        """
    ).fetchone()[0]

    conn.execute(
        """
        INSERT INTO buckets(
            bucket_name,
            display_order
        )
        VALUES (?,?)
        """,
        (
            bucket_name,
            order_value
        )
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

    current = None

    for i, bucket in enumerate(buckets):

        if bucket["id"] == bucket_id:

            current = i
            break

    if current and current > 0:

        left_bucket = buckets[current - 1]

        conn.execute(
            """
            UPDATE buckets
            SET display_order=?
            WHERE id=?
            """,
            (
                left_bucket["display_order"],
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
                buckets[current]["display_order"],
                left_bucket["id"]
            )
        )

    conn.commit()
    conn.close()