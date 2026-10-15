import sqlite3

DB_NAME = "planner.db"


def get_connection():

    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buckets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        bucket_name TEXT NOT NULL,
        display_order INTEGER NOT NULL,

        UNIQUE(project_id,bucket_name),

        FOREIGN KEY(project_id)
        REFERENCES projects(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bucket_id INTEGER NOT NULL,
        task_name TEXT NOT NULL,
        description TEXT,
        priority TEXT,
        status TEXT,
        plan_start DATE,
        plan_end DATE,
        actual_end DATE,
        closure_date DATE,
        is_late INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        UNIQUE(bucket_id,task_name),

        FOREIGN KEY(bucket_id)
        REFERENCES buckets(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checklist_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        item_name TEXT,
        completed INTEGER DEFAULT 0,

        FOREIGN KEY(task_id)
        REFERENCES tasks(id)
    )
    """)

    count = cursor.execute(
        """
        SELECT COUNT(*)
        FROM projects
        """
    ).fetchone()[0]

    if count == 0:

        cursor.execute(
            """
            INSERT INTO projects(
                project_name,
                description
            )
            VALUES(
                'Default Project',
                'Initial Project'
            )
            """
        )

    default_project = cursor.execute(
        """
        SELECT id
        FROM projects
        WHERE project_name='Default Project'
        """
    ).fetchone()

    if default_project:

        project_id = default_project["id"]

        bucket_count = cursor.execute(
            """
            SELECT COUNT(*)
            FROM buckets
            """
        ).fetchone()[0]

        if bucket_count == 0:

            cursor.execute(
                """
                INSERT INTO buckets(
                    project_id,
                    bucket_name,
                    display_order
                )
                VALUES(
                    ?,
                    'Backlog',
                    1
                )
                """,
                (project_id,)
            )

    conn.commit()
    conn.close()
