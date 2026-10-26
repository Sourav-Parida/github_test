# TaskFlow Assignment (Medium) — Apply a batch of CRUD operations

This is a mini repository that replays a list of changes against a database. You'll seed a `Task` table using a SQLAlchemy model, then walk through a list of operations — create, update, rename, delete — applying each in turn. It's the full CRUD story through an ORM, plus the important habit of failing *softly* when an op points at a task that isn't there.

## Worked example
```python
apply_ops([{'title': 'A', 'status': 'todo'}],
          [{'op': 'update_status', 'id': 1, 'status': 'done'}])
# -> {'count': 1, 'tasks': [{'id': 1, 'title': 'A', 'status': 'done'}]}
```
The seed created task `id` 1, then the `update_status` op flipped its status to `'done'`. One task remains, so `count` is 1. If that op had targeted `id` 99 (which doesn't exist), it would simply be skipped — no error — and the task would stay `'todo'`.

## What to build
Write `apply_ops(seed, ops)`:

- Seed a fresh in-memory repo with the `seed` task dicts (missing status -> `'todo'`).
- Apply each op in `ops` **in order**:
  - `{'op':'create','title':..,'status':..}` inserts a task
  - `{'op':'update_status','id':..,'status':..}` changes status
  - `{'op':'rename','id':..,'title':..}` changes title
  - `{'op':'delete','id':..}` removes the task
- An op targeting an id that does not exist is a safe no-op (never raise).
- Return `{'count': <remaining count>, 'tasks': [ {'id','title','status'} sorted by id ]}`.

## Concepts you'll use
SQLAlchemy model + `Session`, dispatching on `op['op']` (`if/elif`), `session.get(Task, id)` returning `None` when missing, `add`/`delete`/`commit`, sorting results by `id`, model-to-dict.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `class Base(DeclarativeBase)`
- `class Task(Base)`
- `_engine()`
- `apply_ops(seed, ops)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `apply_ops([{'title': 'A', 'status': 'todo'}], [{'op': 'update_status', 'id': 1, 'status': 'done'}])['count']`  →  `1`
- `apply_ops([{'title': 'A', 'status': 'todo'}], [{'op': 'update_status', 'id': 1, 'status': 'done'}])['tasks']`  →  `[{"id": 1, "title": "A", "status": "done"}]`
- `apply_ops([{'title': 'A', 'status': 'todo'}], [{'op': 'update_status', 'id': 99, 'status': 'done'}])['count']`  →  `1`

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
def _engine()
def apply_ops(seed, ops)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
