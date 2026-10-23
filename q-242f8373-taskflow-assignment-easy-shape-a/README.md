# TaskFlow Assignment (Easy) — Shape a Task API Response

A TaskFlow API endpoint takes the raw task stored in the database and hands the frontend a clean, predictable response. You'll write the function that shapes that response. This is a **pure Python function** — no web server, no FastAPI to run: you just take a dict in and return a dict out, exactly like the logic that would live *inside* an endpoint.

## Worked example
```python
to_task_response({'id': 1, 'title': 'Fix login bug', 'status': 'done'})
# -> {'task_id': 1, 'title': 'Fix login bug', 'status': 'done', 'is_completed': True}
```
Here `id` was copied into `task_id`, `title` and `status` came straight from the task, and `is_completed` is `True` because the status is `'done'`. When a key is missing you fall back to a default instead of crashing — e.g. `to_task_response({'id': 4, 'title': 'No status here'})` returns `status` `'todo'` and `is_completed` `False`.

## What to build
Write `to_task_response(task)` that returns a dict with EXACTLY these four keys:

- `task_id` — the task's `id`, or `None` if the `id` key is absent.
- `title` — the task's `title`; use an empty string `""` when it's missing or `None`.
- `status` — the task's `status`; default to `"todo"` when it's missing or `None`.
- `is_completed` — `True` only when the (defaulted) status equals `"done"`, otherwise `False`.

Keep it pure: no printing, no I/O — just build and `return` the dict.

## Concepts you'll use
`dict.get(key, default)`, comparing strings (`== "done"`), building a dict.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `to_task_response(task)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `to_task_response({'id': 1, 'title': 'Fix login bug', 'status': 'done'})['task_id']`  →  `1`
- `to_task_response({'id': 1, 'title': 'Fix login bug', 'status': 'done'})['title']`  →  `Fix login bug`
- `to_task_response({'id': 1, 'title': 'Fix login bug', 'status': 'done'})['status']`  →  `done`

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
def to_task_response(task)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
