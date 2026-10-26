# TaskFlow Assignment (Easy) — Filter TaskFlow tasks by status with a parameterised query

TaskFlow needs to pull just the tasks in a given status column ("show me everything that's `todo`"). You'll do it the database way: load the tasks into a real SQLite table, then run a SQL query to fetch the matches. This is your first taste of talking to a database from Python — and of doing it *safely* with parameter binding instead of gluing values into the SQL string.

## Worked example
```python
tasks = [{'id':1,'title':'Fix login bug','status':'todo'},
         {'id':2,'title':'Write API docs','status':'done'},
         {'id':3,'title':'Add unit tests','status':'todo'}]
tasks_by_status(tasks, 'todo')
# -> [{'id': 1, 'title': 'Fix login bug', 'status': 'todo'},
#     {'id': 3, 'title': 'Add unit tests', 'status': 'todo'}]
```
The two `'todo'` rows come back as dicts, ordered by `id`. The `'done'` one is filtered out by the SQL `WHERE status = ?` clause.

## What to build
Write `tasks_by_status(tasks, status)` where `tasks` is a list of dicts with keys `id`, `title`, `status`:

- Create an **in-memory** SQLite database (`sqlite3.connect(':memory:')`), create a `tasks` table, and insert every row.
- Run a **parameterised** `SELECT ... WHERE status = ?` — pass the value as a parameter, never with string formatting (this is how you avoid SQL injection).
- Return the matching rows as a **list of dicts** with keys `id`, `title`, `status`, ordered by `id` ascending.
- An empty input list, or a status with no matches, must return `[]`.

## Concepts you'll use
`sqlite3` (`connect`, `cursor`, `execute`, `executemany`, `fetchall`), `CREATE TABLE` / `INSERT` / `SELECT`, `?` parameter binding, building dicts from query rows.


<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `tasks_by_status(tasks, status)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `len(tasks_by_status([{'id':1,'title':'Fix login bug','status':'todo'},{'id':2,'title':'Write API docs','status':'done'},{'id':3,'title':'Add unit tests','status':'todo'},{'id':4,'title':'Deploy staging','status':'in_progress'},{'id':5,'title':'Review PR','status':'done'}], 'todo'))`  →  `2`
- `tasks_by_status([{'id':1,'title':'Fix login bug','status':'todo'},{'id':2,'title':'Write API docs','status':'done'},{'id':3,'title':'Add unit tests','status':'todo'},{'id':4,'title':'Deploy staging','status':'in_progress'},{'id':5,'title':'Review PR','status':'done'}], 'todo')[0]['id']`  →  `1`
- `tasks_by_status([{'id':1,'title':'Fix login bug','status':'todo'},{'id':2,'title':'Write API docs','status':'done'},{'id':3,'title':'Add unit tests','status':'todo'},{'id':4,'title':'Deploy staging','status':'in_progress'},{'id':5,'title':'Review PR','status':'done'}], 'todo')[0]['title']`  →  `Fix login bug`

Return the exact value shown (a list stays a list; round numbers only if the task says so). **`return` the value — do not `print` it.**

<!--LL-ATTEMPT-->
---

## How to attempt this

1. Open the assignment from your course page. Write your answer **in the code editor on the
   right** — there is no file to create and nothing to name.
2. Click **Run Tests** to grade it. The visible tests run first so you can see where you stand.
3. Read any failure carefully: it shows the **input**, what was **expected**, and what your code
   **actually returned**. That three-way comparison is usually enough to find the bug.
4. Re-run as often as you like. Each value is scored separately, so a partly-correct answer still
   earns marks — submit something rather than nothing.
5. When you are satisfied, **Submit**.

### The exact shape to define

```python
def tasks_by_status(tasks, status)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
