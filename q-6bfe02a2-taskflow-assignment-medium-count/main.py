import sqlite3

def open_tasks_per_project(projects, tasks):
    conn = sqlite3.connect(':memory:')

    conn.execute('CREATE TABLE projects (id INTEGER, name TEXT)')
    conn.execute('CREATE TABLE tasks (id INTEGER, project_id INTEGER, status TEXT)')

    # Insert projects using parameterised INSERT
    conn.executemany(
        'INSERT INTO projects (id, name) VALUES (?, ?)',
        [(p['id'], p['name']) for p in projects]
    )

    # Insert tasks using parameterised INSERT
    conn.executemany(
        'INSERT INTO tasks (id, project_id, status) VALUES (?, ?, ?)',
        [(t['id'], t['project_id'], t['status']) for t in tasks]
    )

    # LEFT JOIN and count tasks whose status is not 'done'
    cursor = conn.execute("""
        SELECT
            p.id AS project_id,
            p.name AS name,
            COUNT(
                CASE WHEN t.status != ? THEN t.id END
            ) AS open_count
        FROM projects p
        LEFT JOIN tasks t ON p.id = t.project_id
        GROUP BY p.id, p.name
        ORDER BY p.id ASC
    """, ('done',))

    # Convert rows into a list of dictionaries
    result = [
        {
            'project_id': row[0],
            'name': row[1],
            'open_count': row[2]
        }
        for row in cursor.fetchall()
    ]

    conn.close()
    return result