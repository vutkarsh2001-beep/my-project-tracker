from database.db import get_connection


def get_projects():

    conn = get_connection()

    projects = conn.execute(
        """
        SELECT *
        FROM projects
        ORDER BY project_name
        """
    ).fetchall()

    conn.close()

    return projects


def create_project(
    project_name,
    description=""
):

    conn = get_connection()

    existing = conn.execute(
        """
        SELECT COUNT(*)
        FROM projects
        WHERE project_name=?
        """,
        (project_name,)
    ).fetchone()[0]

    if existing > 0:

        conn.close()

        return False

    conn.execute(
        """
        INSERT INTO projects(
            project_name,
            description
        )
        VALUES (?,?)
        """,
        (
            project_name,
            description
        )
    )

    conn.commit()
    conn.close()

    return True


def rename_project(
    project_id,
    new_name
):

    conn = get_connection()

    existing = conn.execute(
        """
        SELECT COUNT(*)
        FROM projects
        WHERE project_name=?
        AND id<>?
        """,
        (
            new_name,
            project_id
        )
    ).fetchone()[0]

    if existing > 0:

        conn.close()

        return False

    conn.execute(
        """
        UPDATE projects
        SET project_name=?
        WHERE id=?
        """,
        (
            new_name,
            project_id
        )
    )

    conn.commit()
    conn.close()

    return True


def delete_project(project_id):

    conn = get_connection()

    conn.execute(
        """
        DELETE FROM projects
        WHERE id=?
        """,
        (project_id,)
    )

    conn.commit()
    conn.close()
