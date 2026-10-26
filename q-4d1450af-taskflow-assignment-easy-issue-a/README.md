# TaskFlow Assignment (Easy) — Issue a TaskFlow Access Token

When someone logs into TaskFlow, the server hands them a *JWT* (JSON Web Token) — a compact, signed string that proves who they are on later requests. It's signed with a secret, so nobody can forge or tamper with it. You'll write the helpers that create and read one.

## Worked example
```python
tok = issue_token('u1', 'admin', 's3cr3t')
read_claims(tok, 's3cr3t')['sub']    # -> 'u1'
read_claims(tok, 's3cr3t')['role']   # -> 'admin'
```
`issue_token` signs the payload `{"sub": "u1", "role": "admin"}` with the secret into a token string; `read_claims` verifies the signature with the same secret and gives the payload back.

## What to build
Using the `pyjwt` library (`import jwt`, HS256):
- `issue_token(user_id, role, secret)` -> a JWT whose payload is exactly `{"sub": user_id, "role": role}`.
- `read_claims(token, secret)` -> the decoded claims dict.
- `token_is_valid(token, secret)` -> `True` if the token decodes under `secret`, else `False` (never raise).

All functions are pure Python and return plain values. Use `algorithm="HS256"` when encoding and `algorithms=["HS256"]` when decoding.

## Concepts you'll use
`jwt.encode` / `jwt.decode`, dict payloads, `try/except` to return `False` instead of raising.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `issue_token(user_id, role, secret)`
- `read_claims(token, secret)`
- `token_is_valid(token, secret)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `read_claims(issue_token('u1','admin','s3cr3t'),'s3cr3t')['sub']`  →  `u1`
- `read_claims(issue_token('u1','admin','s3cr3t'),'s3cr3t')['role']`  →  `admin`
- `read_claims(issue_token('u9','member','k'),'k')['sub']`  →  `u9`

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
def issue_token(user_id, role, secret)
def read_claims(token, secret)
def token_is_valid(token, secret)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
