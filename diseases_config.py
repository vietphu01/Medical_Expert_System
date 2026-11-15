import numpy as np

DISEASES = {
    "heart": {
        "name": "Bệnh Tim Mạch", "icon": "❤️",
        "fields": [
            {"key": "age",  "label": "Tuổi", "min": 20, "max": 85, "default": 50},
            {"key": "bp",   "label": "Huyết áp (mmHg)", "min": 90, "max": 200, "default": 130},
            {"key": "chol", "label": "Cholesterol (mg/dL)", "min": 150, "max": 400, "default": 240}
        ],
        "feature_names": ["age", "bp", "chol"],
        "fuzzy": [
            {"feature": "bp",   "low": 120, "high": 160, "dir": "asc"},
            {"feature": "chol", "low": 200, "high": 280, "dir": "asc"}
        ],
        "healthy_params": [(40, 12), (125, 15), (210, 25)],
        "sick_params":    [(55, 15), (145, 18), (260, 35)],
        "rule_file_prefix": "HEART"
    },
    "diabetes": {
        "name": "Bệnh Tiểu Đường", "icon": "🩸",
        "fields": [
            {"key": "glucose", "label": "Glucose (mg/dL)", "min": 70, "max": 250, "default": 120},
            {"key": "bmi",     "label": "Chỉ số BMI", "min": 15, "max": 50, "default": 28, "step": 0.1},
            {"key": "age",     "label": "Tuổi", "min": 20, "max": 85, "default": 45}
        ],
        "feature_names": ["glucose", "bmi", "age"],
        "fuzzy": [
            {"feature": "glucose", "low": 100, "high": 140, "dir": "asc"},
            {"feature": "bmi",     "low": 25,  "high": 32,  "dir": "asc"}
        ],
        "healthy_params": [(85, 10), (22, 2), (35, 8)],
        "sick_params":    [(160, 25), (35, 5), (55, 10)],
        "rule_file_prefix": "DIAB"
    },
    "liver": {
        "name": "Bệnh Gan", "icon": "🫀",
        "fields": [
            {"key": "bilirubin", "label": "Bilirubin (mg/dL)", "min": 0.3, "max": 10, "default": 1.0, "step": 0.1},
            {"key": "albumin",   "label": "Albumin (g/dL)", "min": 2, "max": 6, "default": 4.0, "step": 0.1},
            {"key": "age",       "label": "Tuổi", "min": 20, "max": 85, "default": 45}
        ],
        "feature_names": ["bilirubin", "albumin", "age"],
        "fuzzy": [
            {"feature": "bilirubin", "low": 1.2, "high": 3.0, "dir": "asc"},
            {"feature": "albumin",   "low": 3.5, "high": 4.5, "dir": "desc"}
        ],
        "healthy_params": [(0.8, 0.2), (4.3, 0.4), (35, 8)],
        "sick_params":    [(4.5, 2.0), (2.9, 0.5), (58, 10)],
        "rule_file_prefix": "LIVER"
    },
    "kidney": {
        "name": "Bệnh Thận", "icon": "🫘",
        "fields": [
            {"key": "creatinine", "label": "Creatinine (mg/dL)", "min": 0.4, "max": 10, "default": 1.2, "step": 0.1},
            {"key": "bp",         "label": "Huyết áp (mmHg)", "min": 90, "max": 200, "default": 130},
            {"key": "age",        "label": "Tuổi", "min": 20, "max": 85, "default": 45}
        ],
        "feature_names": ["creatinine", "bp", "age"],
        "fuzzy": [
            {"feature": "creatinine", "low": 1.3, "high": 3.0, "dir": "asc"},
            {"feature": "bp",         "low": 130, "high": 160, "dir": "asc"}
        ],
        "healthy_params": [(1.0, 0.2), (118, 10), (35, 8)],
        "sick_params":    [(4.5, 1.5), (155, 20), (60, 10)],
        "rule_file_prefix": "KIDNEY"
    }
}

def generate_dataset(disease_key, n=300, seed=42):
    d = DISEASES[disease_key]
    rng = np.random.RandomState(seed)
    X, y = [], []
    for i in range(n):
        label = i % 2
        params = d["sick_params"] if label == 1 else d["healthy_params"]
        feats = [rng.normal(m, s) for m, s in params]
        X.append(feats); y.append(label)
    return np.array(X), np.array(y)