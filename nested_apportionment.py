import heapq


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
    if remainders.keys() != errors.keys():
        raise ValueError("Remainders and errors have different keys")
    items = [(-remainders[cat], errors[cat], cat) for cat in remainders]
    allocated_items = heapq.nsmallest(total, items)
    allocated_categories = {item[2] for item in allocated_items}
    return {cat: (1 if cat in allocated_categories else 0) for cat in remainders}
