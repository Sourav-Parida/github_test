# TaskFlow Assignment (Medium) — Cache-first TaskService reads (repo + cache + clock)

# Cache-aware task reads

Same *dependency injection* idea, one step up: `TaskService` now also gets a `cache` dict handed in, and reads follow the cache-aside rule — check the cache before hitting the repo. You'll add a few small read methods on top.

## Worked example
```python
svc = TaskService(repo=lambda i: {1: {'id': 1, 'status': 'todo'}}.get(i),
                  cache={}, clock=lambda: '2026-01-01')
svc.get_task(1)['status']   # -> 'todo'
```
`get_task(1)` isn't in the cache yet, so it calls `repo(1)`, stores the result, and returns it. A second call would come straight from the cache. All three dependencies (`repo`, `cache`, `clock`) were injected.

## What to build
`class TaskService` composed from three **injected** dependencies:
- `repo` -- callable `repo(task_id) -> dict | None`
- `cache` -- a `dict` used as a read cache
- `clock` -- callable `() -> str` timestamp

Methods:
- `get_task(task_id)`: return the cached value if `task_id` is already in `cache`; otherwise call `repo(task_id)`, store non-`None` results in `cache`, and return the task (or `None` if not found). **The cache must be checked before the repo.**
- `status_of(task_id)`: the task's `status`, or `'unknown'` if the task is missing or has no status.
- `summary(ids)`: fetch each id via `get_task`, skip missing ones, and return a `dict` counting tasks per status (missing status counts as `'unknown'`).
- `stamp(task_id)`: return the task merged with `'checked_at': clock()`; return `None` if the task is missing.

Return plain dicts / values.

## Concepts you'll use
`__init__` storing injected deps, `in` check on a dict, `dict.get` with a default, dict merging (`{**task, 'checked_at': ...}`), counting in a loop.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `class TaskService`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `TaskService(repo=lambda i: {1:{'id':1,'status':'todo'}}.get(i), cache={}, clock=lambda: '2026-01-01').get_task(1)['id']`  →  `1`
- `TaskService(repo=lambda i: {1:{'id':1,'status':'todo'}}.get(i), cache={}, clock=lambda: '2026-01-01').get_task(1)['status']`  →  `todo`
- `TaskService(repo=lambda i: {'id':i,'status':'todo'}, cache={1:{'id':1,'status':'cached'}}, clock=lambda: 'x').get_task(1)['id']`  →  `1`

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
class TaskService:
    def get_task(self, task_id)
    def status_of(self, task_id)
    def summary(self, ids)
    def stamp(self, task_id)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
