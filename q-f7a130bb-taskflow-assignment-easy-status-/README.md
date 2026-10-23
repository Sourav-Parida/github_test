# TaskFlow Assignment (Easy) — Status code for a task lookup

When someone asks a TaskFlow API for a task by id, the server replies `200 OK` if it exists or `404 Not Found` if it doesn't. You'll write the tiny function that picks the right status code. It's a **pure Python function** — no web framework, no I/O — it just looks in a list and returns a number.

## Worked example
```python
task_status_code(5, [1, 2, 5, 9])
# -> 200
```
`5` is in the list of existing ids, so the answer is `200`. If the id isn't there — e.g. `task_status_code(3, [1, 2, 5, 9])` — you return `404` instead.

## What to build
Write `task_status_code(task_id, task_ids)` where `task_id` is the id being requested and `task_ids` is the list of ids that currently exist. Return the integer `200` if `task_id` is in `task_ids`, otherwise `404`.

## Concepts you'll use
The `in` membership test, returning an integer.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `task_status_code(task_id, task_ids)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `task_status_code(5, [1, 2, 5, 9])`  →  `200`
- `task_status_code(3, [1, 2, 5, 9])`  →  `404`
- `task_status_code(1, [1])`  →  `200`

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
def task_status_code(task_id, task_ids)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
