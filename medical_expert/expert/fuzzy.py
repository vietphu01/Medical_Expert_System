def fuzzy_membership(x, low, high, direction="asc"):
    """Trả về độ phụ thuộc [0.0, 1.0] - Hàm liên thuộc mờ"""
    if direction == "asc":
        if x <= low: return 0.0
        if x >= high: return 1.0
        return (x - low) / (high - low)
    else:  # desc: giá trị thấp = nguy hiểm
        if x <= low: return 1.0
        if x >= high: return 0.0
        return (high - x) / (high - low)

def compute_fuzzy_facts(disease_cfg, inputs):
    """Tính các giá trị mờ cho 1 bệnh. Trả về (fuzzy_values, facts)"""
    fuzzy_values = {}
    facts = {}
    for cfg in disease_cfg["fuzzy"]:
        feat = cfg["feature"]
        val = inputs[feat]
        m = fuzzy_membership(val, cfg["low"], cfg["high"], cfg["dir"])
        fuzzy_values[feat] = round(m * 100, 1)
        # Ngưỡng 0.5 để chuyển sang boolean cho Rule Engine
        facts[f"high_{feat}" if cfg["dir"] == "asc" else f"low_{feat}"] = m > 0.5
    return fuzzy_values, facts