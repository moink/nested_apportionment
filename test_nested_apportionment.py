import re
import unittest
from nested_apportionment import allocate_remainder


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


if __name__ == "__main__":
    unittest.main()
