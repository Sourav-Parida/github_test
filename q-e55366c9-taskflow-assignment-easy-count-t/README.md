# TaskFlow Assignment (Easy) — Count Tasks by Status

## Count Tasks by Status

A TaskFlow board wants a quick tally: how many tasks sit in each status column. You'll write the counter — a tiny, pure function that's easy to unit-*test*, which is exactly this session's theme.

## Worked example
```python
count_by_status([{'status': 'todo'}, {'status': 'done'}])   # -> {'todo': 1, 'done': 1}
count_by_status([{'status': 'todo'}, {'status': 'todo'}])   # -> {'todo': 2}
```
Walk the list and add 1 to a running count for each task's status. Statuses appear in the result in the order they were first seen.

## What to build
`count_by_status(tasks)`:
- `tasks` is a list of dicts, each with a `'status'` key (e.g. `'todo'`, `'in_progress'`, `'done'`, or any other string).
- Return a dict mapping each status seen to how many tasks have it.
- Preserve **first-seen insertion order** of statuses.
- An empty list returns `{}`.
- Extra keys on a task (like `'id'`) are ignored.

The function must be pure: no printing, no input, just return the dict.

## Concepts you'll use
Looping over a list, `dict.get(status, 0) + 1` (or `collections.Counter`), reading a dict key.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `count_by_status(tasks)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `count_by_status([{'status': 'todo'}, {'status': 'done'}])['todo']`  →  `1`
- `count_by_status([{'status': 'todo'}, {'status': 'done'}])['done']`  →  `1`
- `count_by_status([{'status': 'todo'}, {'status': 'todo'}])`  →  `{"todo": 2}`

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
def count_by_status(tasks)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
