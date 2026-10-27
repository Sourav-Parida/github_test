# TaskFlow Assignment (Easy) — Sanitise TaskFlow Tag Names

Users type messy tag names on their TaskFlow tasks. Before you store or show a tag you *sanitise* it — strip out anything that isn't a safe, plain character — so no surprising input sneaks through. You'll write that cleaner.

## Worked example
```python
sanitize_tag(' Bug-Fix ')   # -> 'Bug-Fix'
```
The surrounding spaces are trimmed, and every remaining character (`B`, `u`, `g`, `-`, `F`, `i`, `x`) is an ASCII letter or a hyphen, so all are kept — with their original upper/lower case.

## What to build
`sanitize_tag(raw)`:
1. If `raw` is not a `str`, return `'untitled'`.
2. Strip surrounding whitespace.
3. Keep ONLY ASCII letters, ASCII digits, hyphen `-` and underscore `_`. Drop everything else (spaces, punctuation, accented/non-ASCII letters, emoji).
4. If nothing remains, return `'untitled'`.

Case is preserved (do not upper/lower-case the kept characters). Return a plain string.

## Concepts you'll use
`isinstance`, `str.strip`, filtering characters into a new string (loop or comprehension), an allowed set or `str.isascii`/`str.isalnum`.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `sanitize_tag(raw)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `sanitize_tag(' Bug-Fix ')`  →  `Bug-Fix`
- `sanitize_tag('hot!!!')`  →  `hot`
- `sanitize_tag('   ')`  →  `untitled`

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
def sanitize_tag(raw)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
