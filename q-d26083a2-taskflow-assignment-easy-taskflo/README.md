# TaskFlow Assignment (Easy) — TaskFlow TaskStore: Create & Read

# Create & Read for the in-memory TaskStore

TaskFlow keeps its tasks in a plain dict (`store`) that maps a `task_id` to a task dict — an in-memory stand-in for a database. You'll write the "C" and "R" of CRUD: **create** a task and **read** one back. These are **pure Python functions** — no server, no real DB — each returns a `(data, status_code)` pair, the same shape an API endpoint would send.

## Worked example
```python
store = {}
create_task(store, 't1', 'Fix login')
# -> ({'id': 't1', 'title': 'Fix login', 'status': 'todo'}, 201)
```
The id `'t1'` wasn't in the store, so a new task is built (starting in the `'todo'` column), saved, and returned with `201` (Created). Reading it back with `get_task(store, 't1')` then gives `({'id': 't1', 'title': 'Fix login', 'status': 'todo'}, 200)`.

## What to build
- `create_task(store, task_id, title)` — if `task_id` is already in `store`, return `({'error': 'exists'}, 409)`. Otherwise build `task = {'id': task_id, 'title': title, 'status': 'todo'}`, save it in `store`, and return `(task, 201)`.
- `get_task(store, task_id)` — return `(task, 200)` when the id exists, otherwise `(None, 404)`.

Every new task starts life in the `'todo'` column.

## Concepts you'll use
Dictionaries (`in`, assigning `store[key] = ...`), returning a tuple `(value, code)`.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `create_task(store, task_id, title)`
- `get_task(store, task_id)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `len(create_task({}, 't1', 'Fix login'))`  →  `2`
- `create_task({}, 't1', 'Fix login')[0]['id']`  →  `t1`
- `create_task({}, 't1', 'Fix login')[0]['title']`  →  `Fix login`

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
def create_task(store, task_id, title)
def get_task(store, task_id)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
