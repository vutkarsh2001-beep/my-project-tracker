def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buckets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bucket_name TEXT NOT NULL,
        display_order INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        project TEXT,
        bucket_id INTEGER,
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

    count = cursor.execute("""
    SELECT COUNT(*)
    FROM buckets
    """).fetchone()[0]

    if count == 0:

        cursor.execute("""
        INSERT INTO buckets(
            bucket_name,
            display_order
        )
        VALUES
        ('Backlog',1)
        """)

    conn.commit()
    conn.close()
