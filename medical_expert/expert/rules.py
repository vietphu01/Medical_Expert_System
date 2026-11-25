"""Rule candidates for the four dataset targets, reviewed before the holdout."""

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
        "age_35_to_70": ("age", "between", (35, 70)),
        "bmi_elevated": ("bmi", "ramp", (23, 27)),
        "bmi_higher": ("bmi", "ramp", (28, 32)),
    },
    "ilpd": {},
    "ckd": {},
}
RULES = {
    "cleveland": (
        {
            "id": "CLEV_TARGET_01", "conditions": ("age_at_least_55", "chol_elevated"),
            "target": "cleveland", "cf": 0.55,
            "conclusion": "Tuổi và cholesterol hỗ trợ lớp dương Cleveland",
        },
        {
            "id": "CLEV_SECONDARY_01", "conditions": ("chol_elevated",),
            "target": None, "cf": 0.4,
            "conclusion": "Cholesterol toàn phần vượt mốc tham chiếu của đồ án",
        },
    ),
    "pima": (
        {
            "id": "PIMA_TARGET_01", "conditions": ("age_35_to_70", "bmi_elevated"),
            "target": "pima", "cf": 0.5,
            "conclusion": "Tuổi và BMI hỗ trợ lớp dương Pima",
        },
        {
            "id": "PIMA_TARGET_02", "conditions": ("age_35_to_70", "bmi_higher"),
            "target": "pima", "cf": 0.55,
            "conclusion": "Tuổi và mức BMI cao hơn hỗ trợ lớp dương Pima",
        },
    ),
    "ilpd": (),
    "ckd": (),
}


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
    """Return facts on raw features and every rule matched by known-true facts."""
    units = FEATURE_UNITS[dataset]
    facts = []
    values = {}
    for key, (feature, kind, bounds) in FACTS[dataset].items():
        value = inputs.get(feature)
        membership = _membership(value, kind, bounds)
        boolean = None if membership is None else membership > 0.5
        values[key] = boolean
        facts.append({
            "feature": feature, "unit": units[feature], "value": value,
            "membership": membership, "key": key, "value_boolean": boolean,
        })
    tagged = {fact["feature"] for fact in facts}
    for feature, unit in units.items():
        if feature not in tagged:
            facts.append({
                "feature": feature, "unit": unit, "value": inputs.get(feature),
                "membership": None, "key": None, "value_boolean": None,
            })
    fired = [
        {**rule, "conditions": list(rule["conditions"])}
        for rule in RULES[dataset]
        if all(values[key] is True for key in rule["conditions"])
    ]
    return facts, fired
