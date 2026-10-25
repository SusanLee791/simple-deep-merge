# simple-deep-merge

Merge nested mappings with explicit rules for lists and nulls. A single function, `merge(base, overlay)`, recursively combines two dicts into a new one; neither input is mutated.

```python
from simple_deep_merge import merge

base = {"db": {"host": "localhost", "port": 5432}}
overlay = {"db": {"port": 6543, "user": "admin"}, "log": None}

result = merge(base, overlay)
# result == {"db": {"host": "localhost", "port": 6543, "user": "admin"}, "log": None}
```

## Why this exists

Deep-merging configuration or layered defaults is a common need, but the default behaviour of most merge implementations is inconsistent about lists and `None`. This library picks one rule for each and sticks to it.

The rules, applied recursively through nested dicts:

- **`None` in overlay clears.** If overlay sets a key to `None`, the result has that key set to `None`, regardless of what base had. This lets a caller explicitly reset a field rather than leaving it implicitly inherited from base.
- **Dict + dict recurses.** Keys in both are merged; overlay-only keys are added; base-only keys are kept.
- **Dict + non-dict: overlay wins.** If base has a scalar and overlay has a dict (or vice versa), overlay replaces base entirely. No coercion is attempted.
- **Lists are scalars.** Overlay's list replaces base's list wholesale. By-index or by-id list merging is intentionally not supported — every list-merge policy is wrong for some caller, so this library refuses to pick one.
- **All other types: overlay wins**, including type changes (e.g., `int` -> `str`).

Only mappings (`dict` and other `collections.abc.Mapping` subclasses) are treated as mergeable containers. Tuples and sets are treated as opaque values.

## Awkward edge

Because lists are replaced rather than merged, a caller who wants to append to a list in base must read base, extend it, and pass the full list in overlay. Likewise, setting a key to `None` in overlay is a destructive clear, not a no-op — if you want to leave a key untouched, omit it from overlay.

## Running the tests

```sh
PYTHONPATH=src python -m unittest discover -s tests
```
