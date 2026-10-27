# TaskFlow Assignment (Medium) — SimpleCache: a TTL Cache-Aside Layer

Time to build the cache itself. `SimpleCache` stores values with an expiry time so stale data disappears on its own — the heart of the *cache-aside* pattern (check the cache; on a miss, load and store).

## Worked example
```python
SimpleCache().set('t:1', 'done', 0, 10).get('t:1', 5)   # -> 'done'
```
We store `'done'` at time `0` with a time-to-live (`ttl`) of `10`, so it expires at time `10`. Reading at time `5` is still inside that window, so we get `'done'` back. (`set` returns `self`, which is why we can chain `.get` right after it.)

## What to build
`class SimpleCache`, backed by an internal dict:
- `set(key, value, now, ttl)` -> store value with expiry `now+ttl`; return `self` (chainable).
- `get(key, now)` -> return the value if present AND not expired, else `None`. An entry is expired when `now >= created+ttl`. Drop expired entries you encounter.
- `get_or_set(key, loader, now, ttl)` -> cache-aside: if a live value exists return it (do NOT call `loader`); otherwise call `loader()` (zero-arg), store it with `now+ttl`, and return it.
- `invalidate(key)` -> remove the key if present (safe if absent); return `self`.

Expiry is inclusive: at `now == created+ttl` the entry is already gone.

## Concepts you'll use
`class`/`__init__`, storing state in a dict, returning `self` for chaining, calling a passed-in `loader()`.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `class SimpleCache`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `SimpleCache().set('t:1','done',0,10).get('t:1',5)`  →  `done`
- `SimpleCache().get('t:1',5)`  →  `None`
- `SimpleCache().get_or_set('t:1', lambda: 'loaded', 0, 10)`  →  `loaded`

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
class SimpleCache:
    def set(self, key, value, now, ttl)
    def get(self, key, now)
    def get_or_set(self, key, loader, now, ttl)
    def invalidate(self, key)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
