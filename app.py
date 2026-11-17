import os
from contextlib import closing
from math import isfinite

from flask import Flask, render_template, request, jsonify
import numpy as np, sqlite3
from math_ml_from_scratch import (
    StandardScalerScratch, train_test_split_scratch,
    LogisticRegressionScratch, KNNScratch, GaussianNBScratch,
    DecisionTreeScratch, EnsembleVotingScratch,
    accuracy_score_scratch, precision_score_scratch, recall_score_scratch,
    f1_score_scratch, confusion_matrix_scratch, k_fold_cv_scratch
)
from diseases_config import DISEASES, generate_dataset
from fuzzy_engine import compute_fuzzy_facts
from inference_engine import ExpertEngine

app = Flask(__name__)
engine = ExpertEngine('knowledge_base.json')

# ===== HUẤN LUYỆN MÔ HÌNH CHO TẤT CẢ BỆNH (Khi khởi động) =====
MODELS = {}       # {disease: {model_name: (model, scaler)}}
MODEL_STATS = {}  # {disease: [metrics per model]}
TREE_RULES = {}   # {disease: [rule_text]}

def train_all():
    for dkey, dcfg in DISEASES.items():
        X, y = generate_dataset(dkey, n=300, seed=42)
        X_tr, X_te, y_tr, y_te = train_test_split_scratch(X, y, test_size=0.25, random_state=42)
        
        scaler = StandardScalerScratch().fit(X_tr)
        X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)
        
        model_defs = {
            "Logistic Regression": lambda: LogisticRegressionScratch(lr=0.1, epochs=300),
            "K-Nearest Neighbors": lambda: KNNScratch(k=7),
            "Gaussian Naive Bayes": lambda: GaussianNBScratch(),
            "Decision Tree (ID3)": lambda: DecisionTreeScratch(max_depth=4),
            "Ensemble Voting": lambda: EnsembleVotingScratch([
                LogisticRegressionScratch(lr=0.1, epochs=300),
                KNNScratch(k=7), GaussianNBScratch(),
                DecisionTreeScratch(max_depth=4)
            ])
        }
        
        MODELS[dkey] = {}
        MODEL_STATS[dkey] = []
        
        for mname, factory in model_defs.items():
            m = factory().fit(X_tr_s, y_tr)
            y_pred = m.predict(X_te_s)
            
            # Cross-validation
            cv_mean, cv_std = k_fold_cv_scratch(factory, scaler.transform(X), y, k=5)
            
            MODEL_STATS[dkey].append({
                "name": mname,
                "accuracy": round(accuracy_score_scratch(y_te, y_pred) * 100, 2),
                "precision": round(precision_score_scratch(y_te, y_pred) * 100, 2),
                "recall": round(recall_score_scratch(y_te, y_pred) * 100, 2),
                "f1": round(f1_score_scratch(y_te, y_pred) * 100, 2),
                "cv_mean": round(cv_mean * 100, 2),
                "cv_std": round(cv_std * 100, 2),
                "confusion": confusion_matrix_scratch(y_te, y_pred),
                "loss": m.loss_history[-30:] if hasattr(m, 'loss_history') and m.loss_history else []
            })
            MODELS[dkey][mname] = (m, scaler)
        
        # Lưu luật của Decision Tree
        dt = MODELS[dkey]["Decision Tree (ID3)"][0]
        TREE_RULES[dkey] = dt.export_rules(dcfg["feature_names"])

train_all()

# ===== DATABASE =====
app.config['DATABASE'] = os.environ.get('MEDICAL_HISTORY_DB', 'medical_history.db')

def init_db():
    with closing(sqlite3.connect(app.config['DATABASE'])) as conn, conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS history
            (id INTEGER PRIMARY KEY AUTOINCREMENT, disease TEXT, features TEXT,
             ml_prob REAL, risk_level TEXT, advice TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

init_db()

# ===== API =====
@app.route('/')
def home(): return render_template('index.html')

@app.route('/api/diseases')
def list_diseases():
    return jsonify({k: {kk: vv for kk, vv in v.items() if kk in ['name', 'icon', 'fields', 'symptoms']}
                    for k, v in DISEASES.items()})

@app.route('/api/model_stats/<dkey>')
def model_stats(dkey):
    if dkey not in DISEASES:
        return jsonify(errors={'disease': 'Nhóm bệnh không được hỗ trợ.'}), 404
    return jsonify({
        "stats": MODEL_STATS[dkey],
        "tree_rules": TREE_RULES[dkey]
    })

def validate_diagnosis_fields(data, disease):
    errors = {
        f'body.{key}': f'Trường {key} không được hỗ trợ.'
        for key in data.keys() - {'disease', 'inputs', 'extra_facts'}
    }
    values = data.get('inputs')
    inputs = {}
    if not isinstance(values, dict):
        errors['inputs'] = 'Cần gửi các chỉ số trong một đối tượng JSON.'
    else:
        fields = {field['key']: field for field in disease['fields']}
        for key in values.keys() - fields.keys():
            errors[f'inputs.{key}'] = f'Chỉ số {key} không được hỗ trợ cho nhóm bệnh này.'

        for key, field in fields.items():
            path = f'inputs.{key}'
            label = field['label']
            value = values.get(key)
            if key not in values or (isinstance(value, str) and not value.strip()):
                errors[path] = f'Vui lòng nhập {label}.'
                continue
            if type(value) not in (int, float, str):
                errors[path] = f'{label} phải là số.'
                continue
            try:
                number = float(value)
            except (ValueError, OverflowError):
                errors[path] = f'{label} phải là số hữu hạn.'
                continue
            minimum, maximum = field['min'], field['max']
            if not isfinite(number):
                errors[path] = f'{label} phải là số hữu hạn.'
            elif not minimum <= number <= maximum:
                errors[path] = f'{label} phải nằm trong khoảng {minimum} đến {maximum}.'
            elif key == 'age' and not number.is_integer():
                errors[path] = f'{label} phải là số nguyên.'
            else:
                inputs[key] = number

    symptoms = data.get('extra_facts', {})
    if not isinstance(symptoms, dict):
        errors['extra_facts'] = 'Cần gửi các triệu chứng trong một đối tượng JSON.'
    else:
        allowed = disease.get('symptoms', {})
        for key, value in symptoms.items():
            path = f'extra_facts.{key}'
            if key not in allowed:
                errors[path] = f'Triệu chứng {key} không được hỗ trợ cho nhóm bệnh này.'
            elif not isinstance(value, bool):
                errors[path] = f'{allowed[key]} Chọn Có hoặc Không.'

    return inputs, symptoms, errors

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(errors={'body': 'Cần gửi nội dung là một đối tượng JSON hợp lệ.'}), 400
    dkey = data.get('disease')
    if not isinstance(dkey, str) or dkey not in DISEASES:
        return jsonify(errors={'disease': 'Chọn một nhóm bệnh được hỗ trợ.'}), 400
    dcfg = DISEASES[dkey]

    inputs, symptoms, errors = validate_diagnosis_fields(data, dcfg)
    if errors:
        return jsonify(errors=errors), 400
    X_input = np.array([[inputs[k] for k in dcfg['feature_names']]])
    
    # 2. Chạy Ensemble Voting (mô hình mạnh nhất) để dự đoán
    ensemble_model, scaler = MODELS[dkey]["Ensemble Voting"]
    X_scaled = scaler.transform(X_input)
    ml_prob = float(ensemble_model.predict_proba(X_scaled)[0])
    
    # 3. Tính Logic Mờ
    fuzzy_values, fuzzy_facts = compute_fuzzy_facts(dcfg, inputs)
    
    # 4. Thêm facts từ triệu chứng lâm sàng (nếu user nhập)
    facts = {**symptoms, **fuzzy_facts, "old_age": inputs['age'] >= 50}
    
    # 5. Suy diễn chuyên gia
    conclusions, fired = engine.forward_chaining(dcfg["rule_file_prefix"], facts, ml_prob)
    
    result_text = []
    if not conclusions:
        result_text.append("✅ Không phát hiện dấu hiệu bệnh lý rõ ràng. Duy trì lối sống lành mạnh.")
    else:
        sorted_c = sorted(conclusions.items(), key=lambda x: x[1]['cf'], reverse=True)
        for name, det in sorted_c:
            result_text.append(f"{name} — Độ tin cậy: {det['cf']*100:.1f}% (Luật: {', '.join(det['rules'])})")
    
    # 6. Lưu lịch sử
    with closing(sqlite3.connect(app.config['DATABASE'])) as conn, conn:
        conn.execute("INSERT INTO history (disease, features, ml_prob, risk_level, advice) VALUES (?,?,?,?,?)",
                     (dkey, str(inputs), ml_prob, "HIGH" if ml_prob > 0.7 else "MEDIUM" if ml_prob > 0.4 else "LOW", " | ".join(result_text)))
    
    return jsonify({
        'ml_probability': round(ml_prob * 100, 2),
        'fuzzy_values': fuzzy_values,
        'expert_conclusions': result_text,
        'fired_rules': fired
    })

@app.route('/api/history')
def get_history():
    with closing(sqlite3.connect(app.config['DATABASE'])) as conn:
        rows = conn.execute("SELECT * FROM history ORDER BY timestamp DESC LIMIT 10").fetchall()
    return jsonify(rows)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
