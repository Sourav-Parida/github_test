# TaskFlow Assignment (Easy) — Insert tasks and read them back

Time to meet an ORM. Instead of writing raw SQL, you describe your table as a Python **class** (a SQLAlchemy model) and let the library handle the SQL for you. Here you'll define a `Task` model, insert some rows through it, and read them back — the foundation of every repository you'll build next.

## Worked example
```python
insert_tasks([{'title': 'Design schema', 'status': 'todo'},
              {'title': 'Write repo', 'status': 'done'}])
# -> [{'id': 1, 'title': 'Design schema', 'status': 'todo'},
#     {'id': 2, 'title': 'Write repo', 'status': 'done'}]
```
Each input row became a `Task` row in the database; the `id` was auto-assigned (1, 2, …) by the primary key. Notice the output is **plain dicts**, not `Task` objects — you convert each model instance back into a simple dict before returning.

## What to build
Write `insert_tasks(rows)`:

- Build a fresh in-memory SQLite DB (`create_engine('sqlite://')`) with a declarative `Task` model: `id` (Integer primary key, auto-increment), `title` (String), `status` (String).
- Insert every row. If a row omits `status`, store `'todo'`.
- Return a list of plain dicts `{'id','title','status'}` ordered by `id`.

Return plain dicts, not `Task` objects.

## Concepts you'll use
SQLAlchemy 2.0 `DeclarativeBase`, a mapped model class, `create_engine`, `Base.metadata.create_all`, a `Session` (`add`, `commit`, `query`/`select`), `dict.get` for the `status` default, model-to-dict conversion.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `class Base(DeclarativeBase)`
- `class Task(Base)`
- `_engine()`
- `insert_tasks(rows)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `len(insert_tasks([{'title': 'Design schema', 'status': 'todo'}, {'title': 'Write repo', 'status': 'done'}]))`  →  `2`
- `insert_tasks([{'title': 'Design schema', 'status': 'todo'}, {'title': 'Write repo', 'status': 'done'}])[0]['id']`  →  `1`
- `insert_tasks([{'title': 'Design schema', 'status': 'todo'}, {'title': 'Write repo', 'status': 'done'}])[0]['title']`  →  `Design schema`

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
def _engine()
def insert_tasks(rows)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
