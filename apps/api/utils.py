"""Utility functions for currency formatting, Indian number grouping, and common transforms."""


def format_inr(value: float | int, include_symbol: bool = True) -> str:
    """Format numeric value into Indian rupee format with standard lakh/crore digit grouping.

    Examples
    --------
    >>> format_inr(1246765)
    '₹12,46,765'
    >>> format_inr(75881028)
    '₹7,58,81,028'
    """
    val_int = int(round(value))
    is_neg = val_int < 0
    s = str(abs(val_int))
    if len(s) <= 3:
        res = s
    else:
        last3 = s[-3:]
        rem = s[:-3]
        groups = []
        while len(rem) > 2:
            groups.append(rem[-2:])
            rem = rem[:-2]
        if rem:
            groups.append(rem)
        groups.reverse()
        res = ",".join(groups) + "," + last3

    prefix = "-₹" if is_neg else ("₹" if include_symbol else "")
    return prefix + res
