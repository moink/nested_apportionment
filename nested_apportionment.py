"""Apply nested max-remainder apportionment."""

import heapq
from collections import defaultdict


def nested_apportion(predictions: dict) -> dict:
    """Recursively round nested predictions using the max remainder method.

    Apply the maximum remainder rounding algorithm to the predictions, adjusting them to
    match the total sum while minimizing error at each level of nesting. Accumulate
    and share the errors at each level of recursion.

    Args:
        predictions: Floating-point predictions of observations in categories,
        possibly at nested levels.

    Returns:
        Has the same structure as predictions, with values rounded according to the max
        remainder method.

    Example:
        predictions = {
            "A": {"X": 2.3, "Y": 3.7},
            "B": {"X": 4.0, "Y": 1.0},
            "C": {"X": 0.5, "Y": 0.5},
        }
        result = nested_apportion(predictions)
        print(result)  # Expected:  {
        #    "A": {"X": 2, "Y": 4},
        #    "B": {"X": 4, "Y": 1},
        #    "C": {"X": 1, "Y": 0},
        #}
    """
    total = int(round(calculate_total(predictions)))
    errors = initialize_errors(predictions)

    def _recurse(subpredictions: dict, subtotal: int, level: int) -> dict:
        """Recursively round nested predictions using the max remainder method.

        Args:
            subpredictions: Floating-point predictions at the current level,
                possibly containing nested dictionaries.
            subtotal: The total sum to be matched for the rounded values at the
                current level.
            level: The current nesting level in the recursive structure.

        Returns:
            A dictionary with the same structure as `subpredictions`, with the
            values rounded according to the max remainder method. If the current
            level has no further nested dictionaries, returns the rounded values at
            that level.
        """
        flattened = sum_nested(subpredictions)
        rounded, sub_errors = max_remainder_round(flattened, subtotal, errors[level])
        for key, err in sub_errors.items():
            errors[level][key] += err
        example = next(iter(subpredictions.values()))
        if not isinstance(example, dict):
            return rounded
        sub_result = {}
        for key, value in subpredictions.items():
            sub_result[key] = _recurse(value, rounded[key], level + 1)
        return sub_result

    result = _recurse(predictions, total, 0)
    return result


def calculate_total(predictions: dict) -> int:
    """Calculate the total sum of all predictions."""
    return sum(sum_nested(predictions).values())


def sum_nested(values: dict) -> dict[str, float]:
    """Flatten a nested dictionary by summing values at all levels."""
    flattened = {}
    for key, value in values.items():
        if isinstance(value, dict):
            flattened[key] = sum(sum_nested(value).values())
        else:
            flattened[key] = value
    return flattened


def initialize_errors(predictions: dict) -> list[dict[str:float]]:
    """Initialize error state for nested predictions.

    Traverse the nested structure of the input argument and initializes an error
    dictionary at each level, setting all error values to zero.

    Also validate that the structure of the input argument has a consistent structure,
    with every dictionary on the same level having the same keys.

    Args:
        predictions: A dictionary of predictions that may contain nested dictionaries.

    Returns:
        A list of error dictionaries, where each dictionary corresponds to a level
        in the nested structure of `predictions`. Each dictionary's values are
        initialized to zero.

    Raises:
        ValueError: If, within a single level, there exist dictionaries with
        different keys.
    """
    errors = []
    if isinstance(predictions, dict):
        errors.append({key: 0.0 for key in predictions.keys()})
        example = next(iter(predictions.values()))
        dict_level = isinstance(example, dict)
        example_keys = set()
        if dict_level:
            example_keys = set(example.keys())
        for subpredictions in predictions.values():
            errors += initialize_errors(subpredictions)
            if dict_level and set(subpredictions.keys()) != example_keys:
                raise ValueError(
                    f"Inconsistent keys found: {example_keys} vs {set(subpredictions.keys())}"
                )
    return errors


def max_remainder_round(
    predictions: dict[str, float], total: int, errors: dict[str, float]
) -> tuple[dict[str, int], dict[str, float]]:
    """Round predictions using the max remainder method.

     Ensure that their sum is equal to the total. Also return newly added errors due
     to the rounding.

    Args:
        predictions: A dictionary of predicted values.
        total: The target total sum after rounding.
        errors: A dictionary of errors, to be updated during rounding.

    Returns:
        A tuple containing the rounded predictions and updated errors.
    """
    floor_preds = {k: int(v) for k, v in predictions.items()}
    remainders = {k: v - floor_preds[k] for k, v in predictions.items()}
    floor_sum = sum(floor_preds.values())
    remaining_sum = total - floor_sum
    allocation = allocate_remainder(remainders, remaining_sum, errors)
    rounded_preds = {k: v + allocation[k] for k, v in floor_preds.items()}
    new_errors = {k: rounded_preds[k] - v for k, v in predictions.items()}
    return rounded_preds, new_errors


def allocate_remainder(
    remainders: dict[str, float], total: int, errors: dict[str, float]
) -> dict[str, int]:
    """Allocate categories based on largest remainders and smallest errors for ties.

    Select the top `total` categories by prioritizing those with the largest
    remainders. In case of ties, choose categories with the smallest errors. If both
    are tied, choose categories with the earlier names when sorted lexically.

    Args:
        remainders: Difference from integers for each category.
        total: The number of categories that get allocated an additional value.
        errors: Rounding errors accumulated to date for each category.

    Returns:
        For each category, 1 if the category gets allocated an additional value and
        0 otherwise.

    Raises:
        ValueError:
         - If `total` exceeds the number of categories in `remainders`.
         - If `total` is negative
         - If the keys differ between `remainders` and `errors`

    Example:
        remainders = {"A": 0.1, "B": 0.7, "C": 0.4}
        errors = {"A": 0.0, "B": 0.0, "C": 0.0}
        total = 1
        result = allocate_remainder(remainders, total, errors)
        print(result)  # Expected: {"A": 0, "B": 1, "C": 0}
    """
    if total > len(remainders):
        raise ValueError("Total is larger than number of categories")
    if total < 0:
        raise ValueError("Total is negative")
    if not isinstance(errors, defaultdict) and remainders.keys() != errors.keys():
        raise ValueError("Remainders and errors have different keys")
    items = [(-remainders[cat], errors[cat], cat) for cat in remainders]
    allocated_items = heapq.nsmallest(total, items)
    allocated_categories = {item[2] for item in allocated_items}
    return {cat: (1 if cat in allocated_categories else 0) for cat in remainders}
