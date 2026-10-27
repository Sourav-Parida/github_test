# TaskFlow Assignment (Medium) — PBKDF2 Password Store for TaskFlow Users

TaskFlow must never store a password as plain text. Instead it stores a one-way *hash* — a scrambled fingerprint you can re-check but not reverse — mixed with a random `salt` so two people with the same password still get different hashes. You'll write the hashing, the storable record, and the verify step.

## Worked example
```python
rec = make_record('hunter2', b'0123456789abcdef')   # -> '100000$<salt_hex>$<hash_hex>'
verify_password('hunter2', rec)   # -> True
verify_password('wrong',   rec)   # -> False
```
`make_record` hashes the password with the salt and packs the iteration count, salt, and hash into one `$`-separated string. `verify_password` re-hashes the guess the same way and checks whether it matches.

## What to build
Three functions:
- `hash_password(password, salt, iterations=100000)` -> hex `str`: `hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations).hex()`. `salt` is `bytes`.
- `make_record(password, salt, iterations=100000)` -> `str`: the storable record `'iterations$salt_hex$hash_hex'` (use `salt.hex()`).
- `verify_password(password, record)` -> `bool`: parse the record, rebuild the salt with `bytes.fromhex`, recompute the hash using the ITERATION COUNT STORED IN THE RECORD, and return whether it matches. Any malformed record must return `False` (do not raise).

The same password+salt must always produce the same hash; a different salt or password must change it. Return plain values only.

## Concepts you'll use
`hashlib.pbkdf2_hmac`, `.hex()` / `bytes.fromhex`, `str.split('$')`, `try/except` to swallow bad input.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `hash_password(password, salt, iterations=100000)`
- `make_record(password, salt, iterations=100000)`
- `verify_password(password, record)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `verify_password('hunter2', make_record('hunter2', b'0123456789abcdef'))`  →  `True`
- `verify_password('wrong', make_record('hunter2', b'0123456789abcdef'))`  →  `False`
- `make_record('p', b'0123456789abcdef').split('$')[0]`  →  `100000`

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
def hash_password(password, salt, iterations=ITERATIONS)
def make_record(password, salt, iterations=ITERATIONS)
def verify_password(password, record)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
