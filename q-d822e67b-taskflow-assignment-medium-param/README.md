# TaskFlow Assignment (Medium) — Parametrised Result Summary

## Parametrised Result Summary

This is a mini *test runner*: given a batch of parametrised cases (each with an expected and an actual value), report how many passed, how many failed, and which ones failed — the same summary a testing framework prints.

## Worked example
```python
summarize_results([{'name': 't1', 'expected': 1, 'actual': 1}])
# -> {'total': 1, 'passed': 1, 'failed': 0, 'failures': []}
```
The one case has `expected == actual`, so it passes: `total` 1, `passed` 1, `failed` 0, and no names in `failures`. A mismatching case would add its `name` to `failures` and count as failed.

## What to build
`summarize_results(cases)`, where `cases` is a list of dicts shaped like `{'name': str, 'expected': <any>, 'actual': <any>}`. Return a dict:

```
{'total': <int>, 'passed': <int>, 'failed': <int>, 'failures': [<names of failed cases in appearance order>]}
```

- A case **passes** when `expected == actual` (works for ints, strings, lists, dicts, None, booleans).
- `failed = total - passed`.
- `failures` lists the `name` of each failing case, in the order they appear in `cases`.
- Empty input returns `{'total': 0, 'passed': 0, 'failed': 0, 'failures': []}`.

Pure function: return the dict, no printing.

## Concepts you'll use
Looping with a pass/fail check (`==`), building a list of names, `len(...)`, assembling a result dict.

<!--LL-CONTRACT-->
### How to solve this
Write your Python **directly in the code editor** on the right, then click **Run Tests**. There is a single editor — you do **not** create or name any file; just define the function(s) below.

**Define:**
- `summarize_results(cases)`

**What the grader runs** (each value is scored **separately**, so a partly-correct answer still earns marks):
- `summarize_results([{'name': 't1', 'expected': 1, 'actual': 1}])['total']`  →  `1`
- `summarize_results([{'name': 't1', 'expected': 1, 'actual': 1}])['passed']`  →  `1`
- `summarize_results([{'name': 't1', 'expected': 1, 'actual': 1}])['failed']`  →  `0`

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
def summarize_results(cases)
```

> **Runtime:** your code is graded on **Python 3.11**, the same version as the Python in your editor. Modern syntax is fine — `match` statements and `int | None` unions in annotations both work.
>
> **`return` your answer — never `print` it.** A printed value is not a returned value, and the
> grader only reads what you return.

---
Edit **main.py** in this folder. **Run Test** (in the platform) grades it.
