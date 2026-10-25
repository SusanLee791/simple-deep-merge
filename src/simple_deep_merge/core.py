"""Deep merge for nested mappings.

This module provides a single function, merge(base, overlay), which combines
base and overlay into a new mapping. A shallow copy of base is returned with
overlay's keys recursively merged in.

Merge rules (applied top-down through nested dicts):

  * None in overlay clears: if overlay sets a key to None, the key is present
    in the result with value None, regardless of base. This lets callers
    explicitly reset fields rather than leaving them implicitly inherited.
  * Dict + dict recurses: keys present in both are merged; keys present only in
    overlay are added; keys present only in base are kept untouched.
  * Dict + non-dict: overlay wins, and a non-dict base is replaced entirely by
    a dict overlay (and vice versa). There is no attempt to coerce or convert.
  * Lists: lists are treated as scalars, not merged. Overlay's list replaces
    base's list wholesale. (See README for rationale.)
  * All other types: overlay wins, including when overlay's type differs from
    base's type (e.g., int -> str). No type coercion is attempted.

Input dicts are never mutated; the result is a new dict.
"""

from __future__ import annotations

import copy
from typing import Any, Mapping, MutableMapping


def _is_mapping(obj: Any) -> bool:
    # isinstance(..., Mapping) would also accept e.g. chainmap and other
    # collections.Mapping subclasses, but not strings or bytes. Using the
    # abc keeps us open to third-party dict-likes without requiring an exact
    # dict match. We require a Mapping, not a MutableMapping, because we only
    # read from inputs and write to fresh dicts we control.
    return isinstance(obj, Mapping)


def merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> MutableMapping[str, Any]:
    """Deep-merge two mappings and return a new dict.

    Neither ``base`` nor ``overlay`` is mutated.

    Args:
        base: The starting mapping. Its values form the default.
        overlay: The overriding mapping. Its values win; for dict-vs-dict keys,
            values are merged recursively.

    Returns:
        A new dict containing the merged result.
    """
    if not _is_mapping(base):
        raise TypeError(
            "base must be a Mapping, got %r" % type(base).__name__
        )
    if not _is_mapping(overlay):
        raise TypeError(
            "overlay must be a Mapping, got %r" % type(overlay).__name__
        )

    # Fresh dict so we never touch the caller's base; callers can safely use
    # the same base across multiple merges.
    result: dict[str, Any] = dict(base)

    for key, overlay_value in overlay.items():
        # None in overlay is the explicit-clear signal: set the key to None
        # even if base had a non-None value. This is checked before the
        # dict-recursion branch so a None overlay always wins, never triggers
        # a TypeError on base[key], and is symmetric whether or not the key
        # existed in base.
        if overlay_value is None:
            result[key] = None
            continue

        if key in result:
            base_value = result[key]
            # Only dict-vs-dict recurses. Lists, tuples, sets, and scalars
            # are all treated as opaque values, so overlay simply replaces.
            if _is_mapping(base_value) and _is_mapping(overlay_value):
                result[key] = merge(base_value, overlay_value)
            else:
                result[key] = copy.deepcopy(overlay_value)
        else:
            result[key] = copy.deepcopy(overlay_value)

    return result
