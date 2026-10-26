# TaskFlow Assignment (Easy) — Typed error bodies for TaskFlow

## Error Signaling — the mapper

Deep inside TaskFlow, service code *raises* a specific exception when something goes wrong — "not found", "not allowed", and so on. At the edge of the API, we catch that exception and turn it into a tidy error body the client can read. You'll define the family of exceptions and write the little function that maps one to that body. Every exception carries its own `status` (HTTP code) and `code` (short machine-readable name).

## Worked example
```python
error_response(NotFoundError('Task 5 not found'))
# -> {'status': 404, 'code': 'not_found', 'message': 'Task 5 not found'}
```
`NotFoundError` was defined with `status=404` and `code='not_found'`, and its message text (`str(exc)`) becomes the `message`. So the mapper just reads those three things off whatever exception it's handed.

## What to build
Define a base exception `TaskFlowError(Exception)` with `status=500` and `code='internal_error'`, and four subclasses that override those two attributes:

| exception | status | code |
|---|---|---|
| `ValidationError` | 422 | `validation_error` |
| `NotFoundError` | 404 | `not_found` |
| `PermissionDeniedError` | 403 | `permission_denied` |
| `ConflictError` | 409 | `conflict` |

Then write `error_response(exc)` returning `{'status': exc.status, 'code': exc.code, 'message': str(exc)}`. Keys must appear in the order `status, code, message`.

## Concepts you'll use
Custom exception classes, inheritance, class-level attributes, `str(exc)` to get an exception's message.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `class TaskFlowError(Exception)`
- `class ValidationError(TaskFlowError)`
- `class NotFoundError(TaskFlowError)`
- `class PermissionDeniedError(TaskFlowError)`
- `class ConflictError(TaskFlowError)`
- `error_response(exc)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `error_response(NotFoundError('Task 5 not found'))['status']`  →  `404`
- `error_response(NotFoundError('Task 5 not found'))['code']`  →  `not_found`
- `error_response(NotFoundError('Task 5 not found'))['message']`  →  `Task 5 not found`

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
def error_response(exc)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
