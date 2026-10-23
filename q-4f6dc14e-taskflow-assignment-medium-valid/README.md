# TaskFlow Assignment (Medium) — Validate a Task-Creation Payload

Before TaskFlow saves a new task, an API endpoint checks the incoming data and reports back which fields are wrong. You'll write that checker. It's a **pure Python function** — no server needed: a dict goes in, a result dict comes out, just like the validation logic that would sit at the top of a real `POST /tasks` endpoint.

## Worked example
```python
validate_task_payload({'status': 'archived', 'priority': 'urgent'})
# -> {'valid': False, 'errors': ['invalid_priority', 'invalid_status', 'title_required']}
```
Three things are wrong here: there's no `title` (`title_required`), the status `'archived'` isn't allowed (`invalid_status`), and priority `'urgent'` isn't allowed (`invalid_priority`). Each broken rule adds its exact code to a list, and you return that list **sorted alphabetically**. A clean payload like `validate_task_payload({'title': 'Set up CI', 'status': 'todo', 'priority': 'high'})` returns `{'valid': True, 'errors': []}`.

## What to build
Write `validate_task_payload(payload)` returning `{"valid": bool, "errors": [sorted codes]}`. Check each rule and append the EXACT code shown when it fails:

| Condition | Error code |
|---|---|
| `title` missing / not a str / blank after `.strip()` | `title_required` |
| `status` not in `{todo, in_progress, review, done}` | `invalid_status` |
| `priority` key present but value not in `{low, medium, high}` | `invalid_priority` |
| `estimate_hours` key present but not a real number `>= 0` (a `bool` is NOT a number) | `invalid_estimate` |

Then sort `errors` alphabetically. `valid` is `True` only when `errors` is empty. Note "key present but…" means you only check `priority`/`estimate_hours` if that key is actually in the payload.

## Concepts you'll use
`dict.get` / `in payload`, membership sets (`in {…}`), `str.strip()`, `isinstance` (and remembering `bool` is a subclass of `int`), `sorted()`.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `validate_task_payload(payload)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `validate_task_payload({'title': 'Set up CI', 'status': 'todo', 'priority': 'high'})['valid']`  →  `True`
- `validate_task_payload({'title': 'Set up CI', 'status': 'todo', 'priority': 'high'})['errors']`  →  `[]`
- `validate_task_payload({'status': 'todo'})['valid']`  →  `False`

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
def validate_task_payload(payload)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
