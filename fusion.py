"""Combine ML support with rules that support the same binary target."""

from numbers import Real


DECISION_THRESHOLD = 0.5


def _support(value, name):
    if isinstance(value, bool) or not isinstance(value, Real) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be a number in [0, 1]")
    return float(value)


def _combine(first, second):
    # Accumulating this update gives 1 - product(1 - support) without
    # subtracting a product close to one when the supports are small.
    return first + second * (1 - first)


def fusion_scores(ml_score, target_cfs):
    """Return support for ML, rules only, and both fusion variants."""
    ml = _support(ml_score, "ML score")
    rule = None
    combined_old = 0.0
    for cf in target_cfs:
        cf = _support(cf, "rule CF")
        rule = cf if rule is None else _combine(rule, cf)
        combined_old = _combine(combined_old, _combine(cf, ml))

    return {
        "ml": ml,
        "rule": rule,
        "combined_new": ml if rule is None else _combine(rule, ml),
        "combined_old": ml if rule is None else combined_old,
    }


def make_trace(dataset, model, score, facts, fired_rules):
    """Build a diagnosis trace, using only explicitly mapped target rules."""
    rules = []
    target_cfs = []
    for rule in fired_rules:
        cf = _support(rule["cf"], "rule CF")
        used = rule.get("target") == dataset
        if used:
            target_cfs.append(cf)
        rules.append({**rule, "cf": cf, "used_in_fusion": used})

    scores = fusion_scores(score, target_cfs)
    combined = scores["combined_new"]
    return {
        "target": dataset,
        "ml": {"model": model, "score": scores["ml"]},
        "facts": list(facts),
        "fired_rules": rules,
        "result": {
            "rule_status": "matched" if target_cfs else "no_matching_target_rule",
            "rule_score": scores["rule"],
            "combined_score": combined,
            "predicted_label": int(combined >= DECISION_THRESHOLD),
        },
    }
