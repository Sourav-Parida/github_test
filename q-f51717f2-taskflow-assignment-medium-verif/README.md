# TaskFlow Assignment (Medium) — Verify TaskFlow Tokens with Expiry and Roles

Real JWTs expire, and the API needs to know *why* a token was rejected. You'll extend TaskFlow's token layer to stamp an expiry and report a precise outcome — valid, expired, wrong signature, or plain garbage.

## Worked example
```python
verify_token(issue_token('u1', 'admin', 'sec'), 'sec')['sub']         # -> 'u1'
verify_token(issue_token('u1', 'admin', 'sec', 1000000000), 'sec')    # -> 'expired'
```
A fresh token verifies and returns its claims dict. The second token was issued with an expiry timestamp already in the past, so verification returns the string `'expired'` instead of the claims.

## What to build
Using pyjwt, HS256:
- `issue_token(user_id, role, secret, exp_ts=None)` -> signs `{"sub": user_id, "role": role}`, adding `"exp": exp_ts` (a Unix timestamp) only when `exp_ts` is given.
- `verify_token(token, secret)` -> returns the **claims dict** when valid; otherwise returns the string `"expired"`, `"invalid_signature"`, or `"invalid_token"`. Mind the pyjwt exception order (expiry is not a signature error).
- `extract_role(token, secret)` -> the role string, or `"invalid"` when the token cannot be trusted for any reason.

Return plain values only; never let a pyjwt exception escape.

## Concepts you'll use
`jwt.encode` with an `exp` claim, catching specific exceptions in order (`ExpiredSignatureError`, `InvalidSignatureError`, `InvalidTokenError`), conditional dict building.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `issue_token(user_id, role, secret, exp_ts=None)`
- `verify_token(token, secret)`
- `extract_role(token, secret)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `verify_token(issue_token('u1','admin','sec'),'sec')['sub']`  →  `u1`
- `verify_token(issue_token('u1','admin','sec'),'sec')['role']`  →  `admin`
- `verify_token(issue_token('u1','admin','sec',1000000000),'sec')`  →  `expired`

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
def issue_token(user_id, role, secret, exp_ts=None)
def verify_token(token, secret)
def extract_role(token, secret)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
