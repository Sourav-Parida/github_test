# TaskFlow Assignment (Medium) — GET /tasks list handler with status filter and limit

This is the logic behind `GET /tasks?status=todo&limit=2` — the endpoint that lists tasks and lets the caller filter and cap how many come back. You'll build it as a **pure Python function**: the query params arrive as a dict, and you return a response dict. No server to run.

## Worked example
```python
handle_list_tasks({'status': 'todo'}, [
    {'id': 1, 'title': 'a', 'status': 'todo'},
    {'id': 2, 'title': 'b', 'status': 'done'},
    {'id': 3, 'title': 'c', 'status': 'todo'}])
# -> {'status_code': 200, 'body': [{'id': 1, 'title': 'a', 'status': 'todo'},
#                                  {'id': 3, 'title': 'c', 'status': 'todo'}]}
```
The `status` filter kept only the `'todo'` tasks, in their original order, and wrapped them with a `200` status code. Remember query values are **strings**, so a `'limit'` like `'2'` must be parsed to an int first.

## What to build
Write `handle_list_tasks(query, tasks)`. `query` is a dict of string params with optional keys `'status'` and `'limit'`; `tasks` is a list of dicts like `{'id': 1, 'title': 'Setup', 'status': 'todo'}`. Apply in order:

1. If `'status'` is present, keep only tasks whose `'status'` equals that value.
2. If `'limit'` is present, it must parse to a **positive** integer. If it doesn't (non-numeric, `0`, or negative), return `{'status_code': 422, 'body': {'error': 'invalid limit'}}`.
3. If `'limit'` is a valid positive int, keep only the first `limit` matching tasks.
4. Otherwise return `{'status_code': 200, 'body': <resulting list of task dicts>}`.

Preserve the original order of `tasks` in the body.

## Concepts you'll use
`dict.get` / `in`, list comprehension to filter, `int(...)` with a `try/except ValueError`, list slicing (`[:limit]`).

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `handle_list_tasks(query, tasks)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `handle_list_tasks({}, [{'id': 1, 'title': 'a', 'status': 'todo'}, {'id': 2, 'title': 'b', 'status': 'done'}, {'id': 3, 'title': 'c', 'status': 'todo'}])['status_code']`  →  `200`
- `handle_list_tasks({}, [{'id': 1, 'title': 'a', 'status': 'todo'}, {'id': 2, 'title': 'b', 'status': 'done'}, {'id': 3, 'title': 'c', 'status': 'todo'}])['body']`  →  `[{"id": 1, "title": "a", "status": "todo"}, {"id": 2, "title": "b", "status": "done"}, {"id": 3, "title": "c", "status": "todo"}]`
- `handle_list_tasks({'status': 'todo'}, [{'id': 1, 'title': 'a', 'status': 'todo'}, {'id': 2, 'title': 'b', 'status': 'done'}, {'id': 3, 'title': 'c', 'status': 'todo'}])['status_code']`  →  `200`

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
def handle_list_tasks(query, tasks)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
