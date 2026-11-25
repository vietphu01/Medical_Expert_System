"""Continuous fuzzy rules for the four dataset targets.

Rules scale their base certainty factor by the minimum premise membership
(alpha = min(mu_i) > 0), keep target base CF below 0.5 so a single rule boosts
borderline ML scores without vetoing strongly negative ML scores, and avoid
nested overlapping rules on the same feature.
"""

from medical_expert.expert.fuzzy import fuzzy_membership


FEATURE_UNITS = {
    "cleveland": {"age": "years", "bp": "mmHg", "chol": "mg/dL"},
    "pima": {"glucose": None, "bmi": "kg/m²", "age": "years"},
    "ilpd": {"bilirubin": None, "albumin": None, "age": "years"},
    "ckd": {"creatinine": "mg/dL", "bp": "mmHg", "age": "years"},
}
FACTS = {
    "cleveland": {
        "age_at_least_55": ("age", "at_least", 55),
        "chol_elevated": ("chol", "ramp", (180, 220)),
    },
    "pima": {
        "age_at_least_35": ("age", "at_least", 35),
        "bmi_elevated": ("bmi", "ramp", (25, 32)),
    },
    "ilpd": {},
    "ckd": {},
}
RULES = {
    "cleveland": (
        {
            "id": "CLEV_TARGET_01", "conditions": ("age_at_least_55", "chol_elevated"),
            "target": "cleveland", "cf": 0.35,
            "conclusion": "Tuổi và cholesterol hỗ trợ lớp dương Cleveland",
        },
        {
            "id": "CLEV_SECONDARY_01", "conditions": ("chol_elevated",),
            "target": None, "cf": 0.30,
            "conclusion": "Cholesterol toàn phần vượt mốc tham chiếu của đồ án",
        },
    ),
    "pima": (
        {
            "id": "PIMA_TARGET_01", "conditions": ("age_at_least_35", "bmi_elevated"),
            "target": "pima", "cf": 0.35,
            "conclusion": "Tuổi và mức BMI hỗ trợ lớp dương Pima",
        },
    ),
    "ilpd": (),
    "ckd": (),
}


def rule_schema(dataset):
    """Return JSON-serializable fact and target-rule metadata for the frontend."""
    facts_by_feature = {}
    for key, (feature, kind, bounds) in FACTS[dataset].items():
        facts_by_feature.setdefault(feature, []).append({
            "key": key,
            "kind": kind,
            "bounds": list(bounds) if isinstance(bounds, tuple) else bounds,
        })
    target_rules = [
        list(rule["conditions"])
        for rule in RULES[dataset]
        if rule["target"] == dataset
    ]
    return {"fact_specs": facts_by_feature, "target_rules": target_rules}


def _membership(value, kind, bounds):
    if value is None:
        return None
    if kind == "ramp":
        return fuzzy_membership(value, *bounds)
    if kind == "at_least":
        return float(value >= bounds)
    if kind == "between":
        low, high = bounds
        return float(low <= value <= high)
    raise ValueError(f"unexpected membership kind: {kind}")


def evaluate_rules(dataset, inputs):
    """Return facts on raw features and every rule fired with positive fuzzy degree."""
    units = FEATURE_UNITS[dataset]
    facts = []
    memberships = {}
    for key, (feature, kind, bounds) in FACTS[dataset].items():
        value = inputs.get(feature)
        membership = _membership(value, kind, bounds)
        active = None if membership is None else membership > 0.0
        memberships[key] = membership
        facts.append({
            "feature": feature, "unit": units[feature], "value": value,
            "membership": membership, "key": key, "value_boolean": active,
        })
    tagged = {fact["feature"] for fact in facts}
    for feature, unit in units.items():
        if feature not in tagged:
            facts.append({
                "feature": feature, "unit": unit, "value": inputs.get(feature),
                "membership": None, "key": None, "value_boolean": None,
            })
    fired = []
    for rule in RULES[dataset]:
        cond_degrees = [memberships[key] for key in rule["conditions"]]
        if any(degree is None for degree in cond_degrees):
            continue
        degree = min(cond_degrees)
        if degree > 0.0:
            base_cf = float(rule["cf"])
            fired.append({
                **rule,
                "conditions": list(rule["conditions"]),
                "base_cf": base_cf,
                "degree": float(degree),
                "cf": float(base_cf * degree),
            })
    return facts, fired
