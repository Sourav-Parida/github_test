# TaskFlow Assignment (Medium) — TaskFlow TaskStore: Full CRUD with a Status Filter

# Complete the in-memory TaskStore CRUD API

TaskFlow stores tasks in a dict (`task_id -> {'id', 'title', 'status'}`), an in-memory stand-in for a database. `create_task` is already written; you'll fill in the rest of CRUD — read, update, delete, and list. These are **pure Python functions** (no server, no real DB): each returns a `(data, status_code)` pair like an API endpoint would.

## Worked example
```python
store = {}
create_task(store, 't1', 'Ship v2', 'in_progress')
update_task(store, 't1', {'status': 'done'})
# -> ({'id': 't1', 'title': 'Ship v2', 'status': 'done'}, 200)
```
`update_task` found task `'t1'`, applied the new `status`, and returned the updated task with `200`. If the id didn't exist it would return `(None, 404)` instead — and note `'id'` can never be changed, even if it appears in `fields`.

## What to build
- `get_task(store, task_id)` -> `(task, 200)` if it exists, else `(None, 404)`.
- `update_task(store, task_id, fields)` -> missing task -> `(None, 404)`. Apply the keys in `fields` to the stored task, but **never** allow `'id'` to be changed. Return `(updated_task, 200)`.
- `delete_task(store, task_id)` -> `(True, 200)` on success, or `(None, 404)` if missing.
- `list_tasks(store, status=None)` -> `(list_of_task_dicts, 200)`. When `status` is given, include only tasks whose `status` matches; an empty store or no matches yields `([], 200)`.

## Concepts you'll use
Dict lookup and `in`, `dict.update` (skipping the `'id'` key), `del store[key]`, `list(store.values())`, filtering with a list comprehension.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `create_task(store, task_id, title, status='todo')`
- `get_task(store, task_id)`
- `update_task(store, task_id, fields)`
- `delete_task(store, task_id)`
- `list_tasks(store, status=None)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `len(create_task({}, 't1', 'Ship v2', 'in_progress'))`  →  `2`
- `create_task({}, 't1', 'Ship v2', 'in_progress')[0]['id']`  →  `t1`
- `create_task({}, 't1', 'Ship v2', 'in_progress')[0]['title']`  →  `Ship v2`

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
def create_task(store, task_id, title, status='todo')
def get_task(store, task_id)
def update_task(store, task_id, fields)
def delete_task(store, task_id)
def list_tasks(store, status=None)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
