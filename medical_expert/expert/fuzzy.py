def fuzzy_membership(x, low, high, direction="asc"):
    """Trả về độ phụ thuộc [0.0, 1.0] - Hàm liên thuộc mờ."""
    if low >= high:
        raise ValueError(f"fuzzy bounds require low < high, got ({low}, {high})")
    if direction == "asc":
        if x <= low:
            return 0.0
        if x >= high:
            return 1.0
        return (x - low) / (high - low)
    if direction == "desc":
        if x <= low:
            return 1.0
        if x >= high:
            return 0.0
        return (high - x) / (high - low)
    raise ValueError(f"unexpected fuzzy direction: {direction}")