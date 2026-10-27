# TaskFlow Assignment (Easy) — Cache-Key Builder for Task Queries

Before TaskFlow asks the database for a list of tasks, it checks a cache — a fast store keyed by a short string. This is the *cache-aside* pattern: look in the cache first, hit the database only on a miss. Here you'll build the key that names one such cached query.

## Worked example
```python
build_cache_key('tasks', status='done', project=5)   # -> 'tasks:project=5&status=done'
```
With no filters you'd get just `'tasks'`. With filters, each `key=value` pair is sorted **by key** (`project` before `status`) and joined with `&`, then placed after `entity:` — so the same filters always produce the same key, no matter the call order.

## What to build
`build_cache_key(entity, **filters)` (`**filters` means: any extra keyword arguments arrive as a dict named `filters`):
- No filters -> return the bare `entity` (e.g. `build_cache_key('tasks')` -> `'tasks'`).
- With filters -> return `entity` + `':'` + the `key=value` pairs joined by `'&'`, **sorted alphabetically by key** so key order in the call never matters.
- Render values with plain `str()`; falsy values like `0` and `False` MUST be kept.
- If `entity` is empty or not a string, return `None`.

## Concepts you'll use
`**kwargs`, `sorted(...)`, f-strings or `str()`, `str.join`, `isinstance`.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `build_cache_key(entity, **filters)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `build_cache_key('tasks')`  →  `tasks`
- `build_cache_key('tasks', status='done')`  →  `tasks:status=done`
- `build_cache_key('tasks', project=5, status='done')`  →  `tasks:project=5&status=done`

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
def build_cache_key(entity, **filters)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
