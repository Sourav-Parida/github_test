# TaskFlow Assignment (Medium) — Validation layer that raises, boundary that catches

## Error Signaling — raise then catch

Here you'll practice the two halves of clean error handling. One function **raises** an exception the moment it spots a bad field. A second function **catches** that exception and shapes a friendly response — so the caller always gets a dict, never a crash. This is exactly how a real endpoint separates "detect the problem" from "report the problem".

## Worked example
```python
submit_task({'title': 'Write spec', 'status': 'todo'})
# -> {'ok': True, 'task': {'title': 'Write spec', 'status': 'todo', 'priority': 'medium'}}
```
Everything was valid, so `submit_task` returns `ok: True` with the cleaned task (`priority` defaulted to `'medium'`). Give it a blank title — `submit_task({'title': '', 'status': 'todo'})` — and `validate_task` raises, which `submit_task` catches and turns into `{'ok': False, 'error': {'status': 422, 'code': 'validation_error', 'message': ..., 'field': 'title'}}`.

## What to build
- `validate_task(payload)` — **raise** `ValidationError(message, field=...)` on the **first** invalid field, checked in this order: non-dict payload; `title` required non-empty (after `.strip()`); `status` default `todo`, must be in `{todo,in_progress,done}`; `priority` default `medium`, must be in `{low,medium,high}`; `estimate_hours` if present must be a real number `>= 0` (a `bool` is NOT a valid number).
- `submit_task(payload)` — wrap `validate_task` in `try/except` and return a response dict.
  - **Success:** `{'ok': True, 'task': {'title','status','priority'}}`.
  - **Failure:** `{'ok': False, 'error': {'status':422,'code':'validation_error','message':...,'field':...}}`.

## Concepts you'll use
Custom exceptions with an extra attribute (`field=...`), `raise`, `try/except`, `str.strip()`, membership sets, `isinstance` (`bool` vs `int`).

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `class TaskFlowError(Exception)`
- `class ValidationError(TaskFlowError)`
- `validate_task(payload)`
- `submit_task(payload)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `submit_task({'title': 'Write spec', 'status': 'todo'})['ok']`  →  `True`
- `submit_task({'title': 'Write spec', 'status': 'todo'})['task']`  →  `{"title": "Write spec", "status": "todo", "priority": "medium"}`
- `submit_task({'title': '', 'status': 'todo'})['ok']`  →  `False`

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
def validate_task(payload)
def submit_task(payload)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
