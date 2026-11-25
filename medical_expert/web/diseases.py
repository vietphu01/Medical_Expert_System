DISEASES = {
    "heart": {
        "name": "Bệnh Tim Mạch", "icon": "❤️",
        "fields": [
            {"key": "age",  "label": "Tuổi", "min": 20, "max": 85, "default": 50},
            {"key": "bp",   "label": "Huyết áp lúc nghỉ (mmHg)", "min": 90, "max": 200, "default": 130},
            {"key": "chol", "label": "Cholesterol toàn phần huyết thanh (mg/dL)", "min": 150, "max": 400, "default": 240}
        ],
        "symptoms": {"chest_pain": "Đau ngực?", "short_breath": "Khó thở?"},
        "feature_names": ["age", "bp", "chol"],
    },
    "diabetes": {
        "name": "Bệnh Tiểu Đường", "icon": "🩸",
        "fields": [
            {"key": "glucose", "label": "Glucose huyết tương sau 2 giờ OGTT (đơn vị chưa xác minh)", "min": 70, "max": 250, "default": 120},
            {"key": "bmi",     "label": "BMI (kg/m²)", "min": 15, "max": 50, "default": 28, "step": 0.1},
            {"key": "age",     "label": "Tuổi", "min": 20, "max": 85, "default": 45}
        ],
        "feature_names": ["glucose", "bmi", "age"],
    },
    "liver": {
        "name": "Bệnh Gan", "icon": "🫀",
        "fields": [
            {"key": "bilirubin", "label": "Bilirubin toàn phần (đơn vị nguồn chưa xác minh)", "min": 0.3, "max": 10, "default": 1.0, "step": 0.1},
            {"key": "albumin",   "label": "Albumin (đơn vị nguồn chưa xác minh)", "min": 2, "max": 6, "default": 4.0, "step": 0.1},
            {"key": "age",       "label": "Tuổi", "min": 20, "max": 85, "default": 45}
        ],
        "feature_names": ["bilirubin", "albumin", "age"],
    },
    "kidney": {
        "name": "Bệnh Thận", "icon": "🫘",
        "fields": [
            {"key": "creatinine", "label": "Creatinine (mg/dL)", "min": 0.4, "max": 10, "default": 1.2, "step": 0.1},
            {"key": "bp",         "label": "Huyết áp (mmHg; chưa rõ tâm thu hay tâm trương)", "min": 50, "max": 200, "default": 80},
            {"key": "age",        "label": "Tuổi", "min": 20, "max": 85, "default": 45}
        ],
        "feature_names": ["creatinine", "bp", "age"],
    }
}
