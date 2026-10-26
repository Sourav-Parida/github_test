# TaskFlow Assignment (Medium) — Count open tasks per TaskFlow project with a LEFT JOIN aggregate

TaskFlow's dashboard wants a count of "open" (not-done) tasks for every project — including projects that have zero tasks so far. This is a two-table job: projects and tasks, joined together. You'll practice a `LEFT JOIN`, which keeps every project on the left even when it has no matching tasks on the right, so nothing silently disappears from the report.

## Worked example
```python
projects = [{'id':1,'name':'Website Revamp'}, {'id':2,'name':'Mobile App'}, {'id':3,'name':'Data Migration'}]
tasks = [{'id':1,'project_id':1,'status':'todo'}, {'id':2,'project_id':1,'status':'done'},
         {'id':3,'project_id':1,'status':'in_progress'}, {'id':4,'project_id':2,'status':'done'}]
open_tasks_per_project(projects, tasks)
# -> [{'project_id': 1, 'name': 'Website Revamp', 'open_count': 2},
#     {'project_id': 2, 'name': 'Mobile App', 'open_count': 0},
#     {'project_id': 3, 'name': 'Data Migration', 'open_count': 0}]
```
Project 1 has two not-`done` tasks, so `open_count` is 2. Project 2's only task is `done` (count 0) and project 3 has no tasks at all — but thanks to the `LEFT JOIN` both still appear with `open_count` 0.

## What to build
Write `open_tasks_per_project(projects, tasks)`. `projects` is a list of dicts with `id`, `name`; `tasks` a list with `id`, `project_id`, `status`.

- Build an in-memory SQLite DB with a `projects` and a `tasks` table and insert both (parameterised).
- Return one dict per project: keys `project_id`, `name`, `open_count` = the number of that project's tasks whose `status` is **not** `'done'`.
- Use a **LEFT JOIN** so a project with no tasks (or only done tasks) still appears with `open_count` 0.
- Bind the `'done'` literal as a **parameter**, not string interpolation.
- Order rows by `project_id` ascending. Tasks whose `project_id` matches no project are ignored.

## Concepts you'll use
`sqlite3`, two `CREATE TABLE`s, `LEFT JOIN ... ON`, conditional counting (`SUM(CASE WHEN status != ? THEN 1 ELSE 0 END)` or `COUNT`), `GROUP BY`, `ORDER BY`, `?` parameters.


<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `open_tasks_per_project(projects, tasks)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `len(open_tasks_per_project([{'id':1,'name':'Website Revamp'},{'id':2,'name':'Mobile App'},{'id':3,'name':'Data Migration'}], [{'id':1,'project_id':1,'status':'todo'},{'id':2,'project_id':1,'status':'done'},{'id':3,'project_id':1,'status':'in_progress'},{'id':4,'project_id':2,'status':'done'}]))`  →  `3`
- `open_tasks_per_project([{'id':1,'name':'Website Revamp'},{'id':2,'name':'Mobile App'},{'id':3,'name':'Data Migration'}], [{'id':1,'project_id':1,'status':'todo'},{'id':2,'project_id':1,'status':'done'},{'id':3,'project_id':1,'status':'in_progress'},{'id':4,'project_id':2,'status':'done'}])[0]['project_id']`  →  `1`
- `open_tasks_per_project([{'id':1,'name':'Website Revamp'},{'id':2,'name':'Mobile App'},{'id':3,'name':'Data Migration'}], [{'id':1,'project_id':1,'status':'todo'},{'id':2,'project_id':1,'status':'done'},{'id':3,'project_id':1,'status':'in_progress'},{'id':4,'project_id':2,'status':'done'}])[0]['name']`  →  `Website Revamp`

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
def open_tasks_per_project(projects, tasks)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
