"""Tests for nested_apportionment.py module."""

import re
import unittest
from collections import defaultdict

from nested_apportionment import (
    allocate_remainder,
    max_remainder_round,
    nested_apportion,
    sum_nested,
)


class TestAllocateRemainder(unittest.TestCase):
    """Test cases for the allocate_remainder function."""

    def test_different_remainders_total_0(self):
        """Test allocation when total is 0."""
        remainders = {"A": 0.1, "B": 0.7, "C": 0.4}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 0
        expected_result = {"A": 0, "B": 0, "C": 0}
        result = allocate_remainder(remainders, total, errors)
        self.assertEqual(expected_result, result)

    def test_different_remainders_total_1(self):
        """Test allocation when total is 1."""
        remainders = {"A": 0.1, "B": 0.7, "C": 0.4}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 1
        expected_result = {"A": 0, "B": 1, "C": 0}
        result = allocate_remainder(remainders, total, errors)
        self.assertEqual(expected_result, result)

    def test_different_remainders_total_2(self):
        """Test allocation when total is 2."""
        remainders = {"A": 0.1, "B": 0.7, "C": 0.4}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 2
        expected_result = {"A": 0, "B": 1, "C": 1}
        result = allocate_remainder(remainders, total, errors)
        self.assertEqual(expected_result, result)

    def test_different_remainders_total_3(self):
        """Test allocation when total is 3."""
        remainders = {"A": 0.1, "B": 0.7, "C": 0.4}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 3
        expected_result = {"A": 1, "B": 1, "C": 1}
        result = allocate_remainder(remainders, total, errors)
        self.assertEqual(expected_result, result)

    def test_tie_break_with_errors(self):
        """Test tie-breaking using the smallest errors in case of remainder ties."""
        remainders = {"A": 0.7, "B": 0.7, "C": 0.1}
        errors = {"A": -0.2, "B": -0.3, "C": -1.1}
        total = 1
        expected_result = {"A": 0, "B": 1, "C": 0}
        result = allocate_remainder(remainders, total, errors)
        self.assertEqual(expected_result, result)

    def test_tie_break_lexically(self):
        """Test tie-breaking using lexical order when remainders & errors are equal."""
        remainders = {"A": 0.7, "B": 0.7, "C": 0.1}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 1
        expected_result = {"A": 1, "B": 0, "C": 0}
        result = allocate_remainder(remainders, total, errors)
        self.assertEqual(expected_result, result)

    def test_with_default_dict_errors(self):
        """Test that errors can be a defaultdict."""
        remainders = {"A": 0.1, "B": 0.7, "C": 0.4}
        errors = defaultdict(float)
        total = 1
        expected_result = {"A": 0, "B": 1, "C": 0}
        result = allocate_remainder(remainders, total, errors)
        self.assertEqual(expected_result, result)

    def test_raises_if_negative_total(self):
        """Test raises ValueError when total is negative."""
        remainders = {"A": 0.1, "B": 0.7, "C": 0.4}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = -1
        expected_msg = re.escape("Total is negative")
        with self.assertRaisesRegex(ValueError, expected_msg):
            allocate_remainder(remainders, total, errors)

    def test_raises_if_total_too_large(self):
        """Test raises ValueError when total exceeds the number of categories."""
        remainders = {"A": 0.1, "B": 0.7, "C": 0.4}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 4
        expected_msg = re.escape("Total is larger than number of categories")
        with self.assertRaisesRegex(ValueError, expected_msg):
            allocate_remainder(remainders, total, errors)

    def test_raises_remainders_and_errors_inconsistent(self):
        """Test raises ValueError when keys of remainders and errors differ."""
        remainders = {"A": 0.1, "B": 0.7, "C": 0.4}
        errors = {"A": 0.0, "B": 0.0, "D": 0.0}
        total = 0
        expected_msg = re.escape("Remainders and errors have different keys")
        with self.assertRaisesRegex(ValueError, expected_msg):
            allocate_remainder(remainders, total, errors)

    def test_empty_remainders(self):
        """Test when remainders and errors are empty."""
        remainders = {}
        errors = {}
        total = 0
        expected_result = {}
        result = allocate_remainder(remainders, total, errors)
        self.assertEqual(expected_result, result)


class TestCaseWithDictAlmostEqual(unittest.TestCase):
    """Test case with some useful comparison methods for data structures with floats."""

    def assertDictAlmostEqual(self, dict1: dict, dict2: dict, places: int = 7) -> None:
        """Assert two dicts (possibly nested) are equal within a tolerance for floats.

        Args:
            dict1: First dictionary to compare.
            dict2: Second dictionary to compare.
            places: Number of decimal places to consider (default 7).
        """
        self.assertEqual(len(dict1), len(dict2), "Dictionaries have different lengths")
        for key in dict1:
            self.assertIn(key, dict2, f"Key {key} not found in the second dictionary")
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                self.assertDictAlmostEqual(dict1[key], dict2[key], places)
            else:
                self.assertAlmostEqual(
                    dict1[key], dict2[key], places=places, msg=f"Error in key: {key}"
                )

    def assertListOfDictsAlmostEqual(self, list1, list2, places: int = 7):
        """Assert two lists of dictionaries are equal within a tolerance for floats.

        Args:
            list1: First dictionary to compare.
            list2: Second dictionary to compare.
            places: Number of decimal places to consider (default 7).
        """
        self.assertEqual(len(list1), len(list2))
        for dict1, dict2 in zip(list1, list2):
            self.assertDictAlmostEqual(dict1, dict2, places=places)


class TestMaxRemainderRound(TestCaseWithDictAlmostEqual):
    """Tests for the max_remainder_round function."""

    def test_rounding_with_no_fraction(self):
        """No rounding needed, total matches sum of predictions."""
        predictions = {"A": 3.0, "B": 5.0, "C": 2.0}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 10
        result, updated_errors = max_remainder_round(predictions, total, errors)
        expected_result = {"A": 3, "B": 5, "C": 2}
        expected_errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        self.assertDictAlmostEqual(expected_result, result)
        self.assertDictAlmostEqual(expected_errors, updated_errors)

    def test_rounding_with_no_additional(self):
        """No rounding up needed, predictions rounded down to total."""
        predictions = {"A": 3.8, "B": 5.8, "C": 2.8}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 10
        result, updated_errors = max_remainder_round(predictions, total, errors)
        expected_result = {"A": 3, "B": 5, "C": 2}
        expected_errors = {"A": -0.8, "B": -0.8, "C": -0.8}
        self.assertDictAlmostEqual(expected_result, result)
        self.assertDictAlmostEqual(expected_errors, updated_errors)

    def test_rounding_up_one(self):
        """Rounding up for one category due to a remainder."""
        predictions = {"A": 3.1, "B": 5.2, "C": 2.1}
        errors = {"A": 0.1, "B": 0.1, "C": 0.1}
        total = 11
        result, updated_errors = max_remainder_round(predictions, total, errors)
        expected_result = {"A": 3, "B": 6, "C": 2}
        expected_errors = {"A": -0.1, "B": 0.8, "C": -0.1}
        self.assertDictAlmostEqual(expected_result, result)
        self.assertDictAlmostEqual(expected_errors, updated_errors)

    def test_rounding_with_no_fraction_bigger_total(self):
        """No rounding needed, total is larger than sum of predictions."""
        predictions = {"A": 3.0, "B": 5.0, "C": 2.0}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 11
        result, updated_errors = max_remainder_round(predictions, total, errors)
        expected_result = {"A": 4, "B": 5, "C": 2}
        expected_errors = {"A": 1.0, "B": 0.0, "C": 0.0}
        self.assertDictAlmostEqual(expected_result, result)
        self.assertDictAlmostEqual(expected_errors, updated_errors)

    def test_rounding_with_fraction(self):
        """Rounding up for multiple categories to meet total."""
        predictions = {"A": 3.3, "B": 4.7, "C": 2.9}
        errors = {"A": 0.1, "B": 0.1, "C": 0.1}
        total = 11
        result, updated_errors = max_remainder_round(predictions, total, errors)
        expected_result = {"A": 3, "B": 5, "C": 3}
        expected_errors = {"A": -0.3, "B": 0.3, "C": 0.1}
        self.assertDictAlmostEqual(expected_result, result)
        self.assertDictAlmostEqual(expected_errors, updated_errors)

    def test_rounding_with_tie(self):
        """Tie in remainders, break tie using the smallest error."""
        predictions = {"A": 3.5, "B": 4.5, "C": 2.5}
        errors = {"A": 0.1, "B": 0.1, "C": 0.0}
        total = 11
        result, updated_errors = max_remainder_round(predictions, total, errors)
        expected_result = {"A": 4, "B": 4, "C": 3}
        expected_errors = {"A": 0.5, "B": -0.5, "C": 0.5}
        self.assertDictAlmostEqual(expected_result, result)
        self.assertDictAlmostEqual(expected_errors, updated_errors)

    def test_rounding_with_tie_and_error(self):
        """Tie in remainders and errors, break tie lexicographically."""
        predictions = {"A": 3.5, "B": 4.5, "C": 2.5}
        errors = {"A": 0.1, "B": 0.1, "C": 0.1}
        total = 11
        result, updated_errors = max_remainder_round(predictions, total, errors)
        expected_result = {"A": 4, "B": 5, "C": 2}
        expected_errors = {"A": 0.5, "B": 0.5, "C": -0.5}
        self.assertDictAlmostEqual(expected_result, result)
        self.assertDictAlmostEqual(expected_errors, updated_errors)

    def test_raises_if_total_too_large(self):
        """Raises ValueError if total exceeds sum of predictions plus category count."""
        predictions = {"A": 3.0, "B": 5.0, "C": 2.0}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 14
        with self.assertRaises(ValueError):
            max_remainder_round(predictions, total, errors)

    def test_raises_if_total_too_small(self):
        """Raises ValueError if total less than sum of floor of predictions."""
        predictions = {"A": 3.0, "B": 5.0, "C": 2.0}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 9
        with self.assertRaises(ValueError):
            max_remainder_round(predictions, total, errors)


class TestSumNested(TestCaseWithDictAlmostEqual):
    """Tests for the sum_nested function."""

    def test_sum_nested(self):
        """Test that nested dictionaries are flattened and summed correctly."""
        predictions = {"A": {"P": {"X": 1.2, "Y": 1.3}, "Q": {"X": 1.0, "Y": 0.7}}}
        expected_result = {"A": 4.2}
        result = sum_nested(predictions)
        self.assertEqual(expected_result, result)


class TestNestedApportion(TestCaseWithDictAlmostEqual):
    """Tests for nested_apportion."""

    def test_single_level_apportionment(self):
        """Apportion a flat set of categories with no nesting."""
        predictions = {"A": 2.3, "B": 3.7, "C": 4.0}
        result = nested_apportion(predictions)
        expected_result = {"A": 2, "B": 4, "C": 4}
        self.assertDictAlmostEqual(result, expected_result)

    def test_apportion_two_levels(self):
        """Handle two levels of nested predictions."""
        predictions = {
            "A": {"X": 2.3, "Y": 3.7},
            "B": {"X": 4.0, "Y": 1.0},
            "C": {"X": 0.5, "Y": 0.5},
        }
        expected_result = {
            "A": {"X": 2, "Y": 4},
            "B": {"X": 4, "Y": 1},
            "C": {"X": 1, "Y": 0},
        }
        result = nested_apportion(predictions)
        self.assertDictAlmostEqual(expected_result, result)

    def test_apportion_three_levels(self):
        """Handle three levels of nested predictions and error accumulation."""
        predictions = {
            "A": {"X": {"P": 1.2, "Q": 2.0}, "Y": {"P": 0.8, "Q": 1.7}},
            "B": {"X": {"P": 3.1, "Q": 0.9}, "Y": {"P": 4.2, "Q": 1.1}},
        }
        expected_result = {
            "A": {"X": {"P": 1, "Q": 2}, "Y": {"P": 1, "Q": 2}},
            "B": {"X": {"P": 3, "Q": 1}, "Y": {"P": 4, "Q": 1}},
        }
        result = nested_apportion(predictions)
        self.assertDictAlmostEqual(result, expected_result)

    def test_bigger_case(self):
        """Test multiple levels of nesting with many ties.

        This test demonstrates how the error counting methods make sure that the
        apportionment is approximately balanced even at the lower levels, in the case
        of ties.
        """
        predictions = {
            "car": {
                "german": {"red": 2.7, "blue": 2.7, "green": 2.7},
                "polish": {"red": 2.7, "blue": 2.7, "green": 2.7},
                "dutch": {"red": 2.7, "blue": 2.7, "green": 2.7},
            },
            "truck": {
                "german": {"red": 2.7, "blue": 2.7, "green": 2.7},
                "polish": {"red": 2.7, "blue": 2.7, "green": 2.7},
                "dutch": {"red": 2.7, "blue": 2.7, "green": 2.7},
            },
            "van": {
                "german": {"red": 2.7, "blue": 2.7, "green": 2.7},
                "polish": {"red": 2.7, "blue": 2.7, "green": 2.7},
                "dutch": {"red": 2.7, "blue": 2.7, "green": 2.7},
            },
            "bus": {
                "german": {"red": 1.6, "blue": 1.6, "green": 1.6},
                "polish": {"red": 1.6, "blue": 1.6, "green": 1.6},
                "dutch": {"red": 1.6, "blue": 1.6, "green": 1.6},
            },
        }
        result = nested_apportion(predictions)
        pred_pivots = self.get_pivots(predictions)
        result_pivots = self.get_pivots(result)
        for key, pred_val in pred_pivots.items():
            diff = result_pivots[key] - pred_val
            if abs(diff) > 1:
                self.fail(f"Sum of {key} was {pred_val} and is {result_pivots[key]}")

    @staticmethod
    def get_pivots(d):
        """Add up the sums of all categories in the predictions."""
        total_predictions = {
            "car": sum([sum(value.values()) for value in d["car"].values()]),
            "truck": sum([sum(value.values()) for value in d["truck"].values()]),
            "van": sum([sum(value.values()) for value in d["van"].values()]),
            "bus": sum([sum(value.values()) for value in d["bus"].values()]),
            "german": sum([sum(d[typ]["german"].values()) for typ in d]),
            "polish": sum([sum(d[typ]["polish"].values()) for typ in d]),
            "dutch": sum([sum(d[typ]["dutch"].values()) for typ in d]),
            "red": sum([sum(d[typ][nat]["red"] for nat in d[typ]) for typ in d]),
            "blue": sum([sum(d[typ][nat]["blue"] for nat in d[typ]) for typ in d]),
            "green": sum([sum(d[typ][nat]["green"] for nat in d[typ]) for typ in d]),
        }
        return total_predictions


if __name__ == "__main__":
    unittest.main()
