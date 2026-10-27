# TaskFlow Assignment (Easy) — Overdue task counter (inject repo + clock)

# Overdue counter

This session is about *dependency injection* (DI): instead of a class building its own helpers, you hand them in from outside — which makes it trivial to test with fake data. Here `TaskService` receives its data source and its clock, then counts overdue tasks.

## Worked example
```python
svc = TaskService(repo=lambda: [{'id': 1, 'due': '2026-01-05', 'status': 'todo'},
                                {'id': 2, 'due': '2026-01-20', 'status': 'todo'}],
                  clock=lambda: '2026-01-10')
svc.overdue_count()   # -> 1
```
Today is `'2026-01-10'`. Task 1 is due `'2026-01-05'` (before today) and not done, so it's overdue; task 2 is due later, so it isn't. Count = 1. Notice both `repo` and `clock` were *injected* as callables.

## What to build
`class TaskService` composed from two **injected** dependencies:
- `repo` -- a callable returning `list[dict]` of task records
- `clock` -- a callable returning today's date as an ISO string `'YYYY-MM-DD'`

`overdue_count()` returns the number of tasks that:
1. HAVE a `due` date (not `None`, key may be missing), AND
2. are NOT `'done'`, AND
3. have `due` **strictly** before `clock()`.

Because dates are ISO strings, plain `<` string comparison is correct. The service must never create its own clock or repo -- both arrive through `__init__`. Return a plain integer.

## Concepts you'll use
`__init__` storing injected callables, calling `repo()` and `clock()`, `dict.get`, string `<` comparison, counting in a loop.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `class TaskService`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `TaskService(repo=lambda: [{'id':1,'due':'2026-01-05','status':'todo'},{'id':2,'due':'2026-01-20','status':'todo'}], clock=lambda: '2026-01-10').overdue_count()`  →  `1`
- `TaskService(repo=lambda: [], clock=lambda: '2026-01-10').overdue_count()`  →  `0`
- `TaskService(repo=lambda: [{'id':1,'due':'2026-01-01','status':'todo'},{'id':2,'due':'2026-01-02','status':'todo'}], clock=lambda: '2026-06-01').overdue_count()`  →  `2`

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
    def overdue_count(self)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
