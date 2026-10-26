import sqlite3

def tasks_by_status(tasks, status):
    conn = sqlite3.connect(':memory:')
    conn.execute(
        'CREATE TABLE tasks (id INTEGER, title TEXT, status TEXT)'
    )

    # Insert every task using a parameterised INSERT
    conn.executemany(
        'INSERT INTO tasks (id, title, status) VALUES (?, ?, ?)',
        [(task['id'], task['title'], task['status']) for task in tasks]
    )

    # Fetch matching tasks using a parameterised SELECT
    cursor = conn.execute(
        'SELECT id, title, status FROM tasks WHERE status = ? ORDER BY id ASC',
        (status,)
    )

    # Convert rows into a list of dictionaries
    result = [
        {'id': row[0], 'title': row[1], 'status': row[2]}
        for row in cursor.fetchall()
    ]

    conn.close()
    return result