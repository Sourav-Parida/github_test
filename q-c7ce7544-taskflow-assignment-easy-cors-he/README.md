# TaskFlow Assignment (Easy) — CORS Header Builder

A TaskFlow API request arrives from a browser on some website (its `origin`). A CORS *middleware* — a small piece of code that runs on every request before your handler — decides which origins are allowed to talk to the API. You'll write the function that builds its response headers.

## Worked example
```python
build_cors_headers('https://app.taskflow.io',
                   ['https://app.taskflow.io', 'https://admin.taskflow.io'])
# -> {'Access-Control-Allow-Origin': 'https://app.taskflow.io',
#     'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
#     'Access-Control-Allow-Credentials': 'true'}
```
The origin is in the allow-list, so we echo it back and add the two extra headers that tell the browser the request is permitted.

## What to build
`build_cors_headers(origin, allowed_origins)`:
- If `origin` is empty (`''` or `None`) OR is not a member of `allowed_origins`, return exactly `{'Access-Control-Allow-Origin': 'null'}` — the browser reads `'null'` as "not allowed".
- Otherwise (origin is allowed), return the three-key dict below, where `<the origin>` is the `origin` you were given:
```
{
  'Access-Control-Allow-Origin': <the origin>,
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
  'Access-Control-Allow-Credentials': 'true',
}
```
- Pure function: no I/O, return a plain dict.

## Concepts you'll use
Dict literals, membership test (`in`), a simple `if/else`.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `build_cors_headers(origin, allowed_origins)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `build_cors_headers('https://app.taskflow.io', ['https://app.taskflow.io', 'https://admin.taskflow.io'])['Access-Control-Allow-Origin']`  →  `https://app.taskflow.io`
- `build_cors_headers('https://app.taskflow.io', ['https://app.taskflow.io', 'https://admin.taskflow.io'])['Access-Control-Allow-Methods']`  →  `GET, POST, PUT, DELETE`
- `build_cors_headers('https://app.taskflow.io', ['https://app.taskflow.io', 'https://admin.taskflow.io'])['Access-Control-Allow-Credentials']`  →  `true`

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
def build_cors_headers(origin, allowed_origins)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
