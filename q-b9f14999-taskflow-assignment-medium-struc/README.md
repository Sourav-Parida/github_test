# TaskFlow Assignment (Medium) — Structured Log Record Builder

Every request that passes through the TaskFlow gateway *middleware* (code that runs on each request before the handler) gets logged. You'll write the function that turns one incoming `request` into a tidy log record.

## Worked example
```python
build_log_record({'method': 'get', 'path': '/api/tasks', 'status': 200,
                  'origin': 'https://app.taskflow.io'},
                 1, ['https://app.taskflow.io'])
# -> {'request_id': 'req-00001', 'method': 'GET', 'path': '/api/tasks',
#     'status': 200, 'level': 'info', 'cors_allowed': True}
```
`seq` 1 becomes `'req-00001'` (zero-padded to 5 digits), the method is upper-cased, status 200 is below 400 so the level is `'info'`, and the origin is in the allow-list so `cors_allowed` is `True`.

## What to build
`build_log_record(request, seq, allowed_origins)`:
- `request` is a dict that MAY contain `method`, `path`, `status`, `origin`. Read them with `.get` defaults: method -> `'GET'`, path -> `'/'`, status -> `200`, origin -> `None`.
- Return a dict with EXACTLY these keys, in this order:
  - `request_id`: `'req-%05d' % seq` (e.g. seq 42 -> `'req-00042'`).
  - `method`: the request method, upper-cased.
  - `path`: the request path.
  - `status`: the numeric status.
  - `level`: `'error'` if status >= 500, else `'warn'` if status >= 400, else `'info'`.
  - `cors_allowed`: `True` if origin is in `allowed_origins`, else `False`.
- Pure function: no I/O, return a plain dict.

## Concepts you'll use
`dict.get` with defaults, `%`-formatting, `str.upper`, `if/elif/else`, membership test (`in`).

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `build_log_record(request, seq, allowed_origins)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `build_log_record({'method':'get','path':'/api/tasks','status':200,'origin':'https://app.taskflow.io'}, 1, ['https://app.taskflow.io'])['request_id']`  →  `req-00001`
- `build_log_record({'method':'get','path':'/api/tasks','status':200,'origin':'https://app.taskflow.io'}, 1, ['https://app.taskflow.io'])['method']`  →  `GET`
- `build_log_record({'method':'get','path':'/api/tasks','status':200,'origin':'https://app.taskflow.io'}, 1, ['https://app.taskflow.io'])['path']`  →  `/api/tasks`

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
def build_log_record(request, seq, allowed_origins)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
