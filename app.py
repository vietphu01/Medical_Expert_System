import os
from contextlib import closing
from math import isfinite

from flask import Flask, render_template, request, jsonify
import sqlite3
from diseases_config import DISEASES
from research_rules import evaluate_rules
from fusion import make_trace
from model_runtime import NAMES, load_run

app = Flask(__name__)

DATASET_BY_DISEASE = {
    'heart': 'cleveland', 'diabetes': 'pima', 'liver': 'ilpd', 'kidney': 'ckd',
}
MODEL_RUN = os.environ.get('MEDICAL_MODEL_RUN', 'results/t06-cv-seed42')
try:
    MODELS = load_run(MODEL_RUN)
    for disease, dataset in DATASET_BY_DISEASE.items():
        if dataset in MODELS and set(MODELS[dataset].feature_order) != set(DISEASES[disease]['feature_names']):
            raise ValueError(f'feature schema mismatch for {dataset}')
except (ValueError, OSError) as error:
    app.logger.warning('Model run unavailable: %s', error)
    MODELS = {}


def unavailable():
    return jsonify(errors={'model': 'Mô hình chưa sẵn sàng. Hãy huấn luyện hoặc cấu hình MEDICAL_MODEL_RUN hợp lệ.'}), 503

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
    model = MODELS.get(DATASET_BY_DISEASE[dkey])
    if model is None:
        return unavailable()
    return jsonify({
        "stats": model.stats,
        "tree_rules": model.tree_rules,
        "selected_model": model.variant,
        "evaluation": "train_cv",
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

    inputs, _, errors = validate_diagnosis_fields(data, dcfg)
    if errors:
        return jsonify(errors=errors), 400
    model = MODELS.get(DATASET_BY_DISEASE[dkey])
    if model is None:
        return unavailable()
    ml_prob = float(model.score(inputs))

    dataset = DATASET_BY_DISEASE[dkey]
    facts, fired = evaluate_rules(dataset, inputs)
    model_name = NAMES.get(model.variant, model.variant)
    trace = make_trace(dataset, model_name, ml_prob, facts, fired)
    fuzzy_values = {
        fact['key']: round(fact['membership'] * 100, 2)
        for fact in facts if fact['key'] is not None and fact['membership'] is not None
    }
    result_text = [
        f"{rule['conclusion']} — Điểm hỗ trợ luật: {rule['cf'] * 100:.1f}% (Luật: {rule['id']})"
        for rule in trace['fired_rules']
    ]
    if trace['result']['rule_status'] == 'no_matching_target_rule':
        result_text.append("Không có luật đích nào khớp với dữ kiện đã nhập.")

    # 6. Lưu lịch sử
    with closing(sqlite3.connect(app.config['DATABASE'])) as conn, conn:
        conn.execute("INSERT INTO history (disease, features, ml_prob, risk_level, advice) VALUES (?,?,?,?,?)",
                     (dkey, str(inputs), ml_prob, "HIGH" if ml_prob > 0.7 else "MEDIUM" if ml_prob > 0.4 else "LOW", " | ".join(result_text)))
    
    return jsonify({
        'ml_probability': round(ml_prob * 100, 2),
        'ml_model': model_name,
        'fuzzy_values': fuzzy_values,
        'expert_conclusions': result_text,
        'fired_rules': [rule['id'] for rule in fired],
        'trace': trace,
    })

@app.route('/api/history')
def get_history():
    with closing(sqlite3.connect(app.config['DATABASE'])) as conn:
        rows = conn.execute("SELECT * FROM history ORDER BY timestamp DESC LIMIT 10").fetchall()
    return jsonify(rows)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
