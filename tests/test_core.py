"""Tests for simple_deep_merge.core.merge.

Each test exercises a specific merge rule documented in the module docstring.
Tests are deterministic and operate only on plain Python data structures.
"""

import unittest

from simple_deep_merge.core import merge


class TestMergeBasic(unittest.TestCase):

    def test_overlay_replaces_scalar(self):
        self.assertEqual(
            merge({"a": 1}, {"a": 2}),
            {"a": 2},
        )

    def test_overlay_adds_new_key(self):
        self.assertEqual(
            merge({"a": 1}, {"b": 2}),
            {"a": 1, "b": 2},
        )

    def test_base_key_without_overlay_kept(self):
        self.assertEqual(
            merge({"a": 1, "b": 2}, {"a": 3}),
            {"a": 3, "b": 2},
        )

    def test_empty_overlay_returns_base_values(self):
        self.assertEqual(
            merge({"a": 1}, {}),
            {"a": 1},
        )

    def test_empty_base_uses_overlay(self):
        self.assertEqual(
            merge({}, {"a": 1}),
            {"a": 1},
        )

    def test_both_empty(self):
        self.assertEqual(merge({}, {}), {})


class TestMergeDeep(unittest.TestCase):

    def test_nested_dict_merge(self):
        self.assertEqual(
            merge({"a": {"x": 1, "y": 2}}, {"a": {"y": 3, "z": 4}}),
            {"a": {"x": 1, "y": 3, "z": 4}},
        )

    def test_deeply_nested_merge(self):
        self.assertEqual(
            merge(
                {"a": {"b": {"c": 1}}},
                {"a": {"b": {"d": 2}}},
            ),
            {"a": {"b": {"c": 1, "d": 2}}},
        )

    def test_overlay_dict_replaces_base_scalar(self):
        self.assertEqual(
            merge({"a": 1}, {"a": {"x": 2}}),
            {"a": {"x": 2}},
        )

    def test_overlay_scalar_replaces_base_dict(self):
        self.assertEqual(
            merge({"a": {"x": 2}}, {"a": 1}),
            {"a": 1},
        )


class TestMergeNone(unittest.TestCase):

    def test_none_in_overlay_sets_none(self):
        self.assertEqual(
            merge({"a": 1}, {"a": None}),
            {"a": None},
        )

    def test_none_in_overlay_clears_base_dict(self):
        self.assertEqual(
            merge({"a": {"x": 1}}, {"a": None}),
            {"a": None},
        )

    def test_none_in_overlay_for_new_key(self):
        self.assertEqual(
            merge({}, {"a": None}),
            {"a": None},
        )

    def test_none_in_overlay_during_nested_merge(self):
        self.assertEqual(
            merge(
                {"a": {"x": 1, "y": 2}},
                {"a": {"y": None, "z": 3}},
            ),
            {"a": {"x": 1, "y": None, "z": 3}},
        )


class TestMergeLists(unittest.TestCase):

    def test_list_replaced_wholesale(self):
        self.assertEqual(
            merge({"a": [1, 2, 3]}, {"a": [4, 5]}),
            {"a": [4, 5]},
        )

    def test_list_vs_scalar_overlay_wins(self):
        self.assertEqual(
            merge({"a": [1, 2]}, {"a": 3}),
            {"a": 3},
        )

    def test_scalar_vs_list_overlay_wins(self):
        self.assertEqual(
            merge({"a": 3}, {"a": [1, 2]}),
            {"a": [1, 2]},
        )

    def test_list_not_mutated_in_result(self):
        overlay_list = [4, 5]
        result = merge({"a": [1, 2, 3]}, {"a": overlay_list})
        self.assertEqual(result["a"], [4, 5])
        overlay_list.append(6)
        self.assertEqual(
            result["a"],
            [4, 5],
            msg="The result must hold its own reference, not the overlay's list.",
        )


class TestMergeImmutability(unittest.TestCase):

    def test_base_not_mutated(self):
        base = {"a": {"x": 1}}
        overlay = {"a": {"y": 2}}
        merge(base, overlay)
        self.assertEqual(base, {"a": {"x": 1}})

    def test_overlay_not_mutated(self):
        base = {"a": {"x": 1}}
        overlay = {"a": {"y": 2}}
        merge(base, overlay)
        self.assertEqual(overlay, {"a": {"y": 2}})

    def test_nested_base_value_not_mutated(self):
        inner = {"x": 1}
        base = {"a": inner}
        overlay = {"a": {"y": 2}}
        merge(base, overlay)
        self.assertEqual(inner, {"x": 1})

    def test_result_independent_of_base_after_merge(self):
        base = {"a": {"x": 1}}
        result = merge(base, {"a": {"y": 2}})
        result["a"]["z"] = 3
        self.assertEqual(base, {"a": {"x": 1}})


class TestMergeTypes(unittest.TestCase):

    def test_overlay_type_change_wins(self):
        self.assertEqual(
            merge({"a": 1}, {"a": "hello"}),
            {"a": "hello"},
        )

    def test_overlay_tuple_replaces_scalar(self):
        self.assertEqual(
            merge({"a": 1}, {"a": (1, 2)}),
            {"a": (1, 2)},
        )

    def test_non_mapping_base_raises_type_error(self):
        with self.assertRaises(TypeError):
            merge([1, 2], {"a": 1})

    def test_non_mapping_overlay_raises_type_error(self):
        with self.assertRaises(TypeError):
            merge({"a": 1}, [1, 2])


class TestMergeMappingSubclass(unittest.TestCase):

    def test_input_accepts_mapping_subclass(self):
        # OrderedDict is a Mapping; the function should accept it. The result
        # is always a plain dict, which is the documented return type.
        from collections import OrderedDict

        base = OrderedDict([("a", 1), ("b", {"x": 1})])
        overlay = OrderedDict([("b", {"y": 2}), ("c", 3)])
        result = merge(base, overlay)
        self.assertEqual(result, {"a": 1, "b": {"x": 1, "y": 2}, "c": 3})
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
