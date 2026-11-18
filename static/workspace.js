"use strict";

const byId = id => document.getElementById(id);
const numberFormat = new Intl.NumberFormat("vi-VN", {maximumFractionDigits: 2});
const scoreFormat = new Intl.NumberFormat("vi-VN", {style: "percent", minimumFractionDigits: 1, maximumFractionDigits: 1});
const factLabels = {
    age_at_least_55: "Tuổi từ 55 trở lên",
    chol_elevated: "Cholesterol tăng theo quy tắc Cleveland",
    age_35_to_70: "Tuổi từ 35 đến 70",
    bmi_elevated: "BMI vượt mốc thứ nhất",
    bmi_higher: "BMI vượt mốc thứ hai"
};
let diseases = {};
let currentDisease = "heart";
let selection = 0;
let historyRequest = 0;

function make(tag, text, className) {
    const el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
}

async function fetchJson(url, options) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
        const error = new Error("Yêu cầu chưa hoàn tất.");
        error.fields = data.errors;
        throw error;
    }
    return data;
}

function selectDisease(key) {
    currentDisease = key;
    selection++;
    const disease = diseases[key];
    for (const tab of byId("diseaseTabs").children) {
        tab.setAttribute("aria-pressed", String(tab.dataset.disease === key));
    }
    byId("groupName").textContent = disease.name;
    const dataset = disease.dataset.toUpperCase();
    byId("outputDataset").textContent = dataset;
    byId("modelDataset").textContent = dataset + " · Kiểm chứng chéo";
    byId("emptyState").querySelector(".flow").classList.toggle("ml-only", !disease.has_target_rules);
    renderForm(disease);
    clearResult();
    loadModelStats(key, selection);
}

async function start() {
    try {
        diseases = await fetchJson("/api/diseases");
        for (const key of ["heart", "diabetes", "liver", "kidney"]) {
            const disease = diseases[key];
            const tab = make("button", undefined, "disease-tab");
            tab.type = "button";
            tab.dataset.disease = key;
            tab.append(make("small", disease.dataset.toUpperCase()), make("strong", disease.name.replace(/^Bệnh /, "")));
            tab.addEventListener("click", () => { if (key !== currentDisease) selectDisease(key); });
            byId("diseaseTabs").append(tab);
        }
        selectDisease(currentDisease);
    } catch {
        byId("diagnosisForm").textContent = "Chưa tải được biểu mẫu. Hãy tải lại trang để thử lại.";
        byId("modelStatus").textContent = "Chưa tải được thông tin bộ dữ liệu.";
    }
    loadHistory();
}

function clearResult() {
    byId("loading").hidden = true;
    byId("resultSection").hidden = true;
    byId("emptyState").hidden = false;
}

function renderForm(disease) {
    const form = byId("diagnosisForm");
    form.inert = false;
    form.replaceChildren(make("p", "Có thể để trống chỉ số chưa biết. Khoảng bên cạnh mỗi ô là miền nhập của bản demo.", "hint"));
    for (const field of disease.fields) {
        const group = make("div", undefined, "field");
        const label = make("label", field.label);
        const input = make("input");
        input.type = "number";
        input.id = "field_" + field.key;
        input.name = "inputs." + field.key;
        input.value = field.default;
        input.min = field.min;
        input.max = field.max;
        input.step = field.step || 1;
        label.htmlFor = input.id;
        const range = make("small", numberFormat.format(field.min) + " – " + numberFormat.format(field.max));
        range.id = input.id + "_range";
        input.setAttribute("aria-describedby", range.id);
        const entry = make("div", undefined, "entry");
        entry.append(input, range);
        group.append(label, entry);
        form.append(group);
    }

    const errors = make("ul", undefined, "errors");
    errors.id = "diagnosisErrors";
    errors.setAttribute("role", "alert");
    errors.hidden = true;
    const button = make("button", "Chạy suy luận", "submit");
    button.type = "submit";
    form.append(errors, button);
    form.onsubmit = runDiagnosis;
    form.oninput = () => {
        clearErrors(form);
        clearResult();
    };
}

function clearErrors(form) {
    byId("diagnosisErrors").replaceChildren();
    byId("diagnosisErrors").hidden = true;
    for (const input of form.querySelectorAll(".is-invalid")) {
        input.classList.remove("is-invalid");
        input.removeAttribute("aria-invalid");
        input.setAttribute("aria-describedby", input.id + "_range");
    }
}

function showErrors(form, errors) {
    const list = byId("diagnosisErrors");
    for (const [path, message] of Object.entries(errors)) {
        const li = make("li", message);
        li.id = "error_" + path.replaceAll(".", "_");
        list.append(li);
        const input = form.elements.namedItem(path);
        if (input) {
            input.classList.add("is-invalid");
            input.setAttribute("aria-invalid", "true");
            input.setAttribute("aria-describedby", input.id + "_range " + li.id);
        }
    }
    list.hidden = false;
    form.querySelector(".is-invalid")?.focus();
}

async function runDiagnosis(event) {
    event.preventDefault();
    const form = event.currentTarget;
    if (form.inert) return;
    const disease = diseases[currentDisease];
    const version = selection;
    clearErrors(form);
    clearResult();
    const inputs = {};
    const errors = {};
    for (const field of disease.fields) {
        const el = form.elements.namedItem("inputs." + field.key);
        if (el.validity.badInput) errors[el.name] = field.label + " cần một giá trị số hợp lệ.";
        inputs[field.key] = el.value === "" ? null : el.value;
    }
    if (Object.keys(errors).length) {
        showErrors(form, errors);
        return;
    }
    form.inert = true;
    const submit = form.querySelector("button[type=submit]");
    submit.disabled = true;
    byId("emptyState").hidden = true;
    byId("loading").hidden = false;
    try {
        const data = await fetchJson("/api/diagnose", {
            method: "POST", headers: {"Content-Type": "application/json"},
            body: JSON.stringify({disease: currentDisease, inputs})
        });
        loadHistory();
        if (version !== selection) return;
        renderTrace(data.trace, disease);
        byId("resultSection").hidden = false;
        byId("outputTitle").focus({preventScroll: true});
        if (window.matchMedia("(max-width: 760px)").matches) byId("outputTitle").scrollIntoView({block: "start"});
    } catch (error) {
        if (version !== selection) return;
        form.inert = false;
        byId("emptyState").hidden = false;
        showErrors(form, error.fields || {body: "Chưa nhận được kết quả. Vui lòng thử lại."});
    } finally {
        if (version === selection) {
            form.inert = false;
            submit.disabled = false;
            byId("loading").hidden = true;
        }
    }
}

function renderTrace(trace, disease) {
    const result = trace.result;
    const inputs = byId("traceInputs");
    const facts = byId("traceFacts");
    const rules = byId("traceRules");
    const summary = byId("traceResult");
    inputs.replaceChildren();
    facts.replaceChildren();
    rules.replaceChildren();
    const missing = [];
    for (const field of disease.fields) {
        const value = trace.facts.find(fact => fact.feature === field.key)?.value;
        if (value == null) missing.push(field.key);
        inputs.append(make("li", field.label + " · " + (value == null ? "Chưa biết" : numberFormat.format(value))));
    }
    for (const fact of trace.facts.filter(f => f.key !== null)) {
        const row = make("li");
        const state = fact.value_boolean === null ? "Chưa biết" : (fact.value_boolean ? "Đúng" : "Sai");
        const membership = fact.membership === null ? "" : " · Mức liên thuộc " + scoreFormat.format(fact.membership);
        row.append(make("b", factLabels[fact.key] || fact.key), " · " + state + membership);
        facts.append(row);
    }
    if (!facts.children.length) facts.append(make("li", "Bộ dữ liệu này chưa có dữ kiện dẫn xuất cho hệ luật."));
    for (const rule of trace.fired_rules) {
        const row = make("li");
        row.append(make("code", rule.id), rule.conclusion + " · " + (rule.used_in_fusion ? "Dùng để gộp" : "Luật phụ"),
            make("div", rule.conditions.join(" và ") + " · CF " + scoreFormat.format(rule.cf)));
        rules.append(row);
    }
    if (!rules.children.length) rules.append(make("li", disease.has_target_rules ? "Chưa có luật nào khớp." : "Bộ dữ liệu này chưa có luật đích."));

    const grid = make("div", undefined, "score-grid");
    const model = make("div");
    model.append(make("small", "ML · " + trace.ml.model), make("b", scoreFormat.format(trace.ml.score)));
    const rule = make("div");
    rule.append(make("small", "Hệ luật"), make("b", result.rule_score === null ? "Chưa có điểm" : scoreFormat.format(result.rule_score)));
    grid.append(model, rule);
    summary.replaceChildren(make("p", "Điểm hỗ trợ kết hợp", "score-label"),
        make("strong", scoreFormat.format(result.combined_score), "score-value"),
        make("p", "Nhãn " + result.predicted_label + " · Lớp " + (result.predicted_label ? "dương" : "âm") + " của " + trace.target.toUpperCase()), grid);
    if (result.rule_score === null) {
        const reason = disease.has_target_rules ? "Không có luật đích nào khớp." : "Bộ dữ liệu này chưa có luật đích.";
        summary.append(make("p", reason + " Điểm kết hợp bằng điểm ML.", "score-note"));
    }
    if (missing.length) {
        summary.append(make("p", "Đã nhập " + (disease.fields.length - missing.length) + "/" + disease.fields.length +
            " chỉ số. ML dùng trung vị học từ train cho " + missing.join(", ") + ". Hệ luật giữ dữ kiện thiếu ở trạng thái chưa biết.", "score-note"));
    }
}

async function loadModelStats(key, version) {
    const status = byId("modelStatus");
    const body = byId("modelTable").tBodies[0];
    body.replaceChildren();
    byId("modelTable").hidden = true;
    byId("treeSection").hidden = true;
    byId("treeSection").open = false;
    status.textContent = "Đang tải mô hình…";
    try {
        const data = await fetchJson("/api/model_stats/" + key);
        if (version !== selection) return;
        status.textContent = "Mô hình đã chọn theo F1 · " + data.selected_model_name;
        for (const model of data.stats) {
            const row = make("tr");
            if (model.name === data.selected_model_name) row.className = "chosen";
            row.append(make("td", model.name));
            const cell = make("td");
            const f1 = make("div", undefined, "f1-cell");
            if (model.f1 != null) {
                const meter = make("meter");
                meter.max = 100;
                meter.value = model.f1;
                meter.setAttribute("aria-hidden", "true");
                f1.append(meter, numberFormat.format(model.f1) + " ± " + numberFormat.format(model.cv_std));
            } else f1.textContent = "—";
            cell.append(f1);
            row.append(cell);
            for (const metric of ["accuracy", "precision", "recall", "roc_auc"]) {
                row.append(make("td", model[metric] == null ? "—" : numberFormat.format(model[metric])));
            }
            body.append(row);
        }
        byId("modelTable").hidden = false;
        byId("treeRules").textContent = data.tree_rules;
        byId("treeSection").hidden = !data.tree_rules;
    } catch (error) {
        if (version === selection) status.textContent = error.fields?.model || "Chưa tải được thông tin mô hình.";
    }
}

async function loadHistory() {
    const requestId = ++historyRequest;
    const body = byId("historyBody");
    function showMessage(text) {
        const row = make("tr");
        const cell = make("td", text);
        cell.colSpan = 4;
        row.append(cell);
        body.replaceChildren(row);
    }
    try {
        const rows = await fetchJson("/api/history");
        if (requestId !== historyRequest) return;
        body.replaceChildren();
        if (!rows.length) showMessage("Chưa có lượt suy luận nào được lưu.");
        for (const [id, disease, , score, , , time] of rows) {
            const row = make("tr");
            row.append(make("td", "#" + id), make("td", diseases[disease]?.name || disease),
                make("td", score == null ? "—" : scoreFormat.format(score)), make("td", time || "—"));
            body.append(row);
        }
    } catch {
        if (requestId === historyRequest) showMessage("Chưa đọc được lịch sử.");
    }
}

document.addEventListener("DOMContentLoaded", start);
