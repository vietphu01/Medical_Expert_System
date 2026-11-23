"use strict";

const byId = id => document.getElementById(id);
const numberFormat = new Intl.NumberFormat("vi-VN", {maximumFractionDigits: 2});
const scoreFormat = new Intl.NumberFormat("vi-VN", {style: "percent", minimumFractionDigits: 1, maximumFractionDigits: 1});
const mathFormat = new Intl.NumberFormat("vi-VN", {minimumFractionDigits: 3, maximumFractionDigits: 3});
const collator = new Intl.Collator("vi-VN", {numeric: true, sensitivity: "base"});

const factLabels = {
    age_at_least_55: "Tuổi từ 55 trở lên",
    chol_elevated: "Cholesterol tăng theo quy tắc Cleveland",
    age_35_to_70: "Tuổi từ 35 đến 70",
    bmi_elevated: "BMI vượt mốc thứ nhất",
    bmi_higher: "BMI vượt mốc thứ hai",
};

const DATASET_FACT_SPECS = {
    cleveland: {
        age: [{key: "age_at_least_55", kind: "at_least", bounds: 55, label: "Tuổi ≥ 55"}],
        chol: [{key: "chol_elevated", kind: "ramp", bounds: [180, 220], label: "Cholesterol mờ 180–220"}],
    },
    pima: {
        age: [{key: "age_35_to_70", kind: "between", bounds: [35, 70], label: "Tuổi 35–70"}],
        bmi: [
            {key: "bmi_elevated", kind: "ramp", bounds: [23, 27], label: "BMI mốc 1 (23–27)"},
            {key: "bmi_higher", kind: "ramp", bounds: [28, 32], label: "BMI mốc 2 (28–32)"},
        ],
    },
    ilpd: {},
    ckd: {},
};

const DEMO_PRESETS = [
    {id: "c1", num: "01", title: "Hợp lệ", disease: "heart", diseaseLabel: "Tim mạch",
     inputs: {age: 60, bp: 135, chol: 230},
     summary: "Khớp 1 luật đích và 1 luật phụ"},
    {id: "c2", num: "02", title: "Thiếu cholesterol", disease: "heart", diseaseLabel: "Tim mạch",
     inputs: {age: 60, bp: 135, chol: null},
     summary: "Gửi null · ML điền trung vị, luật bỏ qua"},
    {id: "c3", num: "03", title: "Đúng biên 50%", disease: "heart", diseaseLabel: "Tim mạch",
     inputs: {age: 60, bp: 135, chol: 200},
     summary: "Cholesterol = 200 (μ = 50%, chưa vượt ngưỡng)"},
    {id: "c4", num: "04", title: "2 luật đích", disease: "diabetes", diseaseLabel: "Tiểu đường",
     inputs: {glucose: 175, bmi: 33, age: 45},
     summary: "Khớp 2 luật BMI rồi gộp ML một lần"},
    {id: "c5", num: "05", title: "ML bất đồng luật", disease: "diabetes", diseaseLabel: "Tiểu đường",
     inputs: {glucose: 90, bmi: 26, age: 45},
     summary: "ML 14,3% (âm) nhưng luật đẩy lên 57,1% (dương)"},
    {id: "c6", num: "06", title: "Ngoài miền nhập", disease: "heart", diseaseLabel: "Tim mạch",
     inputs: {age: 60, bp: 135, chol: 900},
     summary: "Cholesterol = 900 · báo lỗi ngay dưới ô nhập"},
];

const DATASET_INPUT_NOTES = {
    pima: "Đơn vị cột glucose 2 giờ OGTT trong tập Pima nguồn chưa được xác minh.",
    ilpd: "Đơn vị nguồn của bilirubin và albumin trong tập ILPD chưa được xác minh; nhóm này chỉ dùng ML.",
    ckd: "Huyết áp trong tập CKD chưa rõ tâm thu hay tâm trương nên chỉ dùng cho ML, không đưa vào hệ luật.",
};

const FIELD_UNITS = {
    cleveland: {age: "", bp: "mmHg", chol: "mg/dL"},
    pima: {glucose: "", bmi: "kg/m²", age: ""},
    ilpd: {bilirubin: "", albumin: "", age: ""},
    ckd: {creatinine: "mg/dL", bp: "mmHg", age: ""},
};

const DISEASE_ICON_PATHS = {
    heart: ["M12 20.5s-7-4.6-9.1-8.5C1.4 9.1 2.9 5.5 6.4 5.5c2 0 3.4 1.1 4.1 2.3.7-1.2 2.1-2.3 4.1-2.3 3.5 0 5 3.6 3.5 6.5C19 15.9 12 20.5 12 20.5Z", "M6.5 12h2.3l1.4-2.5 2.1 4.6 1.5-2.1h3.7"],
    diabetes: ["M12 3.2C9 7.4 6 10.6 6 14a6 6 0 1 0 12 0c0-3.4-3-6.6-6-10.8Z", "M9.5 14.2a2.5 2.5 0 0 0 2.5 2.3"],
    liver: ["M4.5 14.5c0-4.4 3.4-7.5 8.2-7.5h4.8c1.1 0 2 .9 2 2 0 3.7-2.6 6.8-6.4 7.5l-4.2.8c-2.6.5-4.4-.8-4.4-2.8Z", "M12.5 7v5.2l-3.4 2.1"],
    kidney: ["M9.2 5.2c-2.9 0-5 2.4-5 5.8 0 3.6 2 6.8 4.8 6.8 1.5 0 2.2-1 2.2-2.2 0-1.1-.7-1.8-.7-3.1 0-1.3.7-2 .7-3.1 0-2.5-.8-4.2-2-4.2Z", "M14.8 5.2c2.9 0 5 2.4 5 5.8 0 3.6-2 6.8-4.8 6.8-1.5 0-2.2-1-2.2-2.2 0-1.1.7-1.8.7-3.1 0-1.3-.7-2-.7-3.1 0-2.5.8-4.2 2-4.2Z"],
};

const METRIC_LABELS = {
    f1: "F1 ± std (%)",
    roc_auc: "ROC-AUC (%)",
    accuracy: "Accuracy (%)",
    precision: "Precision (%)",
    recall: "Recall (%)",
};

let diseases = {};
let currentDisease = "heart";
let currentView = "workspace";
let showAllViews = false;
let selection = 0;
let inputRevision = 0;
let diagnosisRequest = 0;
let historyRequest = 0;
let currentModelData = null;
let currentChartMetric = "f1";
let currentTreeFilter = "all";
let activePresetId = null;
let liveAutoRun = false;
let liveDebounceTimer = null;
let toastTimer = null;
let errorAnnounceTimer = null;
let announcedErrorField = null;
let whyExpanded = false;
let lastCopyMessage = "";
const copyTimers = new WeakMap();
let supportsDisplayTransition;

function make(tag, text, className) {
    const el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
}

function makeSvg(tag, attrs) {
    if (typeof document.createElementNS !== "function") return null;
    const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
    if (attrs) {
        for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
    }
    return el;
}

function makeIconSvg(paths) {
    const svg = makeSvg("svg", {viewBox: "0 0 24 24", width: 20, height: 20, fill: "none", stroke: "currentColor", "stroke-width": 1.9, "stroke-linecap": "round", "stroke-linejoin": "round", "aria-hidden": "true"});
    if (!svg) return make("span");
    for (const d of paths) svg.append(makeSvg("path", {d}));
    return svg;
}

function prefersReducedMotion() {
    return typeof window !== "undefined" && Boolean(window.matchMedia?.("(prefers-reduced-motion: reduce)").matches);
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

/* ===== Theme Toggle (follows dark-mode-toggle two-state protocol) ===== */
function getSystemScheme() {
    if (typeof window === "undefined" || !window.matchMedia) return "light";
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function getStoredScheme() {
    try {
        const val = localStorage.getItem("color-scheme");
        return val === "light" || val === "dark" ? val : null;
    } catch {
        return null;
    }
}

function applySchemeMeta(scheme) {
    const meta = document.querySelector?.('meta[name="color-scheme"]');
    if (meta) meta.content = scheme || "light dark";
}

function initThemeToggle() {
    const btn = byId("themeToggle");
    if (!btn) return;
    btn.addEventListener("click", () => {
        const system = getSystemScheme();
        const stored = getStoredScheme();
        const rendered = stored || system;
        const target = rendered === "dark" ? "light" : "dark";
        if (target === system) {
            try { localStorage.removeItem("color-scheme"); } catch {}
            applySchemeMeta(null);
        } else {
            try { localStorage.setItem("color-scheme", target); } catch {}
            applySchemeMeta(target);
        }
    });
    if (typeof window !== "undefined") {
        window.addEventListener("storage", event => {
            if (event.key === "color-scheme") applySchemeMeta(getStoredScheme());
        });
    }
}

/* ===== Discrete Display Probe, Toast & Popover Exit Helpers ===== */
function canTransitionDisplay() {
    if (supportsDisplayTransition !== undefined) return supportsDisplayTransition;
    if (typeof window === "undefined" || !window.CSS?.supports?.("transition-behavior", "allow-discrete") || !document.body) {
        return false;
    }
    const probe = document.createElement("div");
    probe.style.cssText = "transition: display 1s allow-discrete !important; display: block;";
    document.body.appendChild(probe);
    window.getComputedStyle(probe).display;
    probe.style.display = "none";
    supportsDisplayTransition = window.getComputedStyle(probe).display === "block";
    probe.remove();
    return supportsDisplayTransition;
}

function supportsTopLayerExit() {
    return typeof window !== "undefined" && Boolean(window.CSS?.supports?.("overlay", "auto") && canTransitionDisplay());
}

async function closeTopLayer(element, nativePopover) {
    if (!supportsTopLayerExit()) {
        element.setAttribute("data-closing", "");
        const animations = element.getAnimations?.({subtree: true}) || [];
        if (animations.length > 0) {
            await Promise.race([
                Promise.allSettled(animations.map(a => a.finished)),
                new Promise(resolve => setTimeout(resolve, 600)),
            ]);
        }
        if (!element.hasAttribute("data-closing")) return;
        element.removeAttribute("data-closing");
    }
    if (nativePopover && typeof element.hidePopover === "function") {
        element.hidePopover();
    } else {
        element.classList.remove("is-open");
    }
}

async function hideToastElement(el) {
    if (canTransitionDisplay()) {
        el.hidden = true;
        return;
    }
    el.setAttribute("data-closing", "");
    const animations = el.getAnimations?.() || [];
    if (animations.length > 0) {
        await Promise.race([
            Promise.allSettled(animations.map(a => a.finished)),
            new Promise(resolve => setTimeout(resolve, 600)),
        ]);
    }
    if (el.hasAttribute("data-closing")) {
        el.removeAttribute("data-closing");
        el.hidden = true;
    }
}

function showToast(message) {
    const el = byId("toastNotice");
    if (!el) return;
    clearTimeout(toastTimer);
    el.removeAttribute("data-closing");
    el.textContent = message;
    el.hidden = false;
    toastTimer = setTimeout(() => hideToastElement(el), 2400);
}

function hasNativePopoverSupport() {
    return typeof HTMLElement !== "undefined" && Object.hasOwn(HTMLElement.prototype, "popover");
}

function hidePopoverElement(popover) {
    if (!popover) return;
    if (hasNativePopoverSupport() && typeof popover.hidePopover === "function") {
        try {
            if (popover.matches?.(":popover-open")) popover.hidePopover();
        } catch {}
    } else if (popover.classList?.contains("is-open")) {
        closeTopLayer(popover, false);
    }
}

function initPopovers() {
    const nativePopover = hasNativePopoverSupport();
    const closePairs = [
        {popoverId: "glossaryPopover", triggerId: "glossaryTrigger", closeId: "glossaryClose"},
        {popoverId: "presetPickerPopover", triggerId: "presetPickerBtn", closeId: "presetPickerClose"},
    ];

    for (const {popoverId, triggerId, closeId} of closePairs) {
        const popover = byId(popoverId);
        const trigger = byId(triggerId);
        const closeBtn = byId(closeId);
        closeBtn?.addEventListener("click", () => {
            closeTopLayer(popover, nativePopover);
            trigger?.focus();
        });
    }

    if (nativePopover) return;

    const allPopovers = [...(document.querySelectorAll?.("[popover]") || [])];
    for (const el of allPopovers) el.removeAttribute("popover");
    let lastTrigger = null;

    const closeAll = () => {
        for (const el of allPopovers) {
            if (el.classList.contains("is-open")) closeTopLayer(el, false);
        }
    };

    document.addEventListener("click", event => {
        const trigger = event.target.closest?.("button[popovertarget]");
        if (trigger) {
            const target = byId(trigger.getAttribute("popovertarget"));
            if (!target) return;
            const wasOpen = target.classList.contains("is-open");
            closeAll();
            if (!wasOpen) {
                target.classList.add("is-open");
                lastTrigger = trigger;
            }
            return;
        }
        if (!event.target.closest?.(".glossary-popover, .info-popover, .preset-popover")) {
            closeAll();
        }
    });

    document.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            const openOne = allPopovers.find(el => el.classList.contains("is-open"));
            if (openOne) {
                closeAll();
                lastTrigger?.focus();
            }
        }
    });
}

/* ===== Copy Button (follows copy-button guide with Invoker Commands + fallback) ===== */
function legacyCopy(text) {
    const field = Object.assign(document.createElement("textarea"), {value: text});
    field.setAttribute("readonly", "");
    field.style.cssText = "position:fixed;inset-block-start:0;opacity:0";
    document.body.append(field);
    field.select();
    try { return document.execCommand("copy"); } catch { return false; } finally { field.remove(); }
}

function reportCopy(button, ok) {
    const tip = button.nextElementSibling;
    clearTimeout(copyTimers.get(button));
    button.removeAttribute("data-copied");
    button.removeAttribute("data-failed");
    let message = ok ? "Đã chép" : "Chép lỗi";
    if (message === lastCopyMessage) message += "\u00A0";
    lastCopyMessage = message;
    if (tip) tip.textContent = "";
    void button.offsetWidth;
    button.setAttribute(ok ? "data-copied" : "data-failed", "");
    if (tip) requestAnimationFrame(() => { tip.textContent = message; });
    copyTimers.set(button, setTimeout(() => {
        button.removeAttribute("data-copied");
        button.removeAttribute("data-failed");
        if (tip) tip.textContent = "";
    }, 2000));
}

async function copyTargetText(button, target) {
    const text = (target.innerText || target.textContent || "").trim();
    if (!text) return;
    try {
        if (navigator.clipboard?.writeText) {
            await navigator.clipboard.writeText(text);
        } else if (!legacyCopy(text)) {
            throw new Error("Copy failed");
        }
        reportCopy(button, true);
    } catch {
        if (legacyCopy(text)) reportCopy(button, true);
        else reportCopy(button, false);
    }
}

function initCopyCommands() {
    document.addEventListener("command", event => {
        if (event.command === "--copy" && event.source && event.target) {
            copyTargetText(event.source, event.target);
        }
    }, true);

    if (typeof window !== "undefined" && !("CommandEvent" in window)) {
        document.addEventListener("click", event => {
            const btn = event.target.closest?.('button[command="--copy"]');
            if (!btn) return;
            const target = byId(btn.getAttribute("commandfor"));
            if (target) copyTargetText(btn, target);
        });
    }
}

/* ===== View Navigation with Safe Same-Document Transitions ===== */
function applyViewLayout(view, allMode) {
    currentView = view;
    showAllViews = allMode;
    const sections = document.querySelectorAll?.(".view-section") || [];
    for (const sec of sections) {
        const secView = sec.dataset.view;
        sec.hidden = !allMode && secView !== view;
        sec.classList.toggle("is-single", !allMode && secView === view);
    }
    for (const link of document.querySelectorAll?.("[data-view-link]") || []) {
        if (link.closest?.(".view-nav")) {
            if (!allMode && link.dataset.viewLink === view) {
                link.setAttribute("aria-current", "page");
            } else {
                link.removeAttribute("aria-current");
            }
        }
    }
    const allBtn = byId("viewAllToggle");
    if (allBtn) allBtn.setAttribute("aria-pressed", String(allMode));
}

function runViewTransition(host, update, onDone) {
    if (!prefersReducedMotion() && host && typeof host.startViewTransition === "function") {
        try {
            const transition = host.startViewTransition(update);
            transition.ready?.catch?.(() => {});
            transition.finished?.catch?.(() => {}).finally(() => onDone?.());
            return;
        } catch {}
    }
    update();
    onDone?.();
}

function switchView(view, {allMode = false, focusHeading = false} = {}) {
    const update = () => applyViewLayout(view, allMode);
    const focusTarget = () => {
        if (!focusHeading) return;
        const map = {workspace: "workspaceTitle", models: "modelsTitle", history: "historyTitle"};
        byId(map[view])?.focus?.({preventScroll: false});
    };

    runViewTransition(document, update, focusTarget);
    if (typeof window !== "undefined" && !allMode && window.history?.replaceState) {
        window.history.replaceState(null, "", "#" + view);
    }
}

function initNavigation() {
    for (const link of document.querySelectorAll?.("[data-view-link]") || []) {
        link.addEventListener("click", event => {
            event.preventDefault();
            switchView(link.dataset.viewLink, {allMode: false, focusHeading: true});
        });
    }
    byId("viewAllToggle")?.addEventListener("click", () => {
        switchView(currentView, {allMode: !showAllViews});
    });
    byId("activeModelPill")?.addEventListener("click", () => {
        switchView("models", {allMode: false, focusHeading: true});
    });
    const hash = typeof window !== "undefined" ? window.location.hash.replace("#", "") : "";
    if (["workspace", "models", "history"].includes(hash)) {
        applyViewLayout(hash, false);
    } else {
        applyViewLayout("workspace", false);
    }
}

/* ===== Fact Curves and Form Labels ===== */
function findFactSpec(dataset, factKey) {
    const groups = DATASET_FACT_SPECS[dataset];
    if (!groups) return null;
    for (const [feature, specs] of Object.entries(groups)) {
        const hit = specs.find(s => s.key === factKey);
        if (hit) return {...hit, feature};
    }
    return null;
}

// Preview the same target-rule conditions shown in research_rules.py; the API
// remains the source of the actual inference result.
const TARGET_RULE_CONDS = {
    cleveland: [["age_at_least_55", "chol_elevated"]],
    pima: [["age_35_to_70", "bmi_elevated"], ["age_35_to_70", "bmi_higher"]],
};
const SHORT_MODEL_NAMES = {
    "Gaussian Naive Bayes": "Gaussian NB",
    "K-Nearest Neighbors": "KNN (k=7)",
    "Logistic Regression": "Logistic Reg.",
    "Decision Tree (ID3)": "Decision Tree",
    "Ensemble Voting": "Ensemble",
};

function previewTargetRules(dataset, values) {
    const facts = {};
    for (const [feature, specs] of Object.entries(DATASET_FACT_SPECS[dataset] || {})) {
        for (const spec of specs) {
            const value = values[feature];
            if (value == null || !Number.isFinite(value)) {
                facts[spec.key] = null;
            } else if (spec.kind === "at_least") {
                facts[spec.key] = value >= spec.bounds;
            } else if (spec.kind === "between") {
                facts[spec.key] = value >= spec.bounds[0] && value <= spec.bounds[1];
            } else {
                const [low, high] = spec.bounds;
                facts[spec.key] = Math.min(1, Math.max(0, (value - low) / (high - low))) > 0.5;
            }
        }
    }
    const outcomes = (TARGET_RULE_CONDS[dataset] || []).map(conditions => {
        if (conditions.some(key => facts[key] === false)) return false;
        return conditions.some(key => facts[key] == null) ? null : true;
    });
    return {matched: outcomes.filter(value => value === true).length, pending: outcomes.some(value => value === null)};
}

function updateWaitingPlaceholder() {
    const disease = diseases[currentDisease];
    const form = byId("diagnosisForm");
    if (!disease || !form?.elements) return;
    const values = {};
    const chips = byId("waitInputChips");
    chips?.replaceChildren();
    let filled = 0;
    let invalid = false;

    for (const field of disease.fields) {
        const el = form.elements.namedItem("inputs." + field.key);
        if (!el) continue;
        const raw = el.value;
        const missing = raw === "" && !el.validity?.badInput;
        const number = missing ? null : Number(raw);
        const bad = !missing && (el.validity?.badInput || !Number.isFinite(number) ||
            number < field.min || number > field.max || (field.key === "age" && !Number.isInteger(number)));
        invalid ||= Boolean(bad);
        values[field.key] = missing || bad ? null : number;
        if (!missing && !bad) filled++;
        const label = missing ? "Chưa biết" : bad ? "Không hợp lệ" : numberFormat.format(number);
        chips?.append(make("span", field.key + ": " + label, "bp-chip" + (missing ? " is-missing" : "")));
    }

    byId("waitNodeInputs").textContent = filled + "/" + disease.fields.length + " chỉ số";
    const nodeRules = byId("waitNodeRules");
    const preview = byId("waitRulePreview");
    let matched = 0;
    if (invalid) {
        nodeRules.textContent = "Chưa sẵn sàng";
        preview.textContent = "Kiểm tra chỉ số đầu vào";
    } else if (!disease.has_target_rules) {
        nodeRules.textContent = "Chưa có luật đích";
        preview.textContent = "Chỉ chạy ML · chưa có luật đích";
    } else {
        const state = previewTargetRules(disease.dataset, values);
        matched = state.matched;
        nodeRules.textContent = !matched && state.pending ? "Chờ dữ kiện" : matched + " luật dự khớp";
        preview.textContent = matched ? "Dự kiến " + matched + " luật đích khớp" :
            state.pending ? "Thiếu dữ kiện để xét luật" : "Chưa đạt tiền đề luật đích";
    }
    preview.classList.toggle("is-match", matched > 0);
}

function replayWaitingPulse() {
    if (prefersReducedMotion()) return;
    for (const el of byId("emptyState")?.querySelectorAll?.(".flow-pulse, .bp-arc-sweep, .bp-shimmer") || []) {
        el.style.animation = "none";
        void el.getBoundingClientRect();
        el.style.animation = "";
    }
}

function syncSliderVars(slider, val) {
    const min = Number(slider.min || 0);
    const max = Number(slider.max || 100);
    const clamped = Math.min(max, Math.max(min, Number.isFinite(val) ? val : min));
    slider.value = String(clamped);
    slider.style?.setProperty?.("--attr-min", String(min));
    slider.style?.setProperty?.("--attr-max", String(max));
    slider.style?.setProperty?.("--control-value", String(clamped));
}

function cleanFieldLabel(field) {
    return field.label
        .replace(/\s*\([^)]*chưa (?:xác minh|rõ)[^)]*\)/gi, match => {
            const unitMatch = match.match(/^\s*\((mmHg|mg\/dL|kg\/m²)\s*;/i);
            return unitMatch ? " (" + unitMatch[1] + ")" : "";
        })
        .trim();
}

function getFieldUnit(field, dataset) {
    return FIELD_UNITS[dataset]?.[field.key] || "";
}

function formatFieldGuidance(field, dataset, kind = "range") {
    const minTxt = numberFormat.format(field.min);
    const maxTxt = numberFormat.format(field.max);
    if (field.key === "age") {
        return "Nhập số nguyên từ " + minTxt + " đến " + maxTxt + ".";
    }
    const unit = getFieldUnit(field, dataset);
    const suffix = unit ? " " + unit : "";
    if (kind === "badInput") {
        return "Nhập số hợp lệ từ " + minTxt + " đến " + maxTxt + suffix + ".";
    }
    return "Nhập giá trị từ " + minTxt + " đến " + maxTxt + suffix + ".";
}

function updateInputInfoPopover(disease) {
    const datasetNote = byId("inputInfoDataset");
    if (!datasetNote || !disease) return;
    const text = DATASET_INPUT_NOTES[disease.dataset] || "";
    datasetNote.textContent = text;
    datasetNote.hidden = !text;
}

/* ===== Demo Case Picker (on-demand popover) ===== */
function renderPresets() {
    const list = byId("presetList");
    if (!list) return;
    list.replaceChildren();
    for (const preset of DEMO_PRESETS) {
        const btn = make("button", undefined, "preset-option");
        btn.type = "button";
        btn.dataset.presetId = preset.id;
        btn.setAttribute("aria-pressed", String(activePresetId === preset.id));

        const top = make("span", undefined, "preset-option-top");
        top.append(
            make("span", "Ca " + Number(preset.num) + " · " + preset.title, "preset-option-name"),
            make("span", preset.diseaseLabel, "preset-option-tag")
        );
        btn.append(top, make("span", preset.summary, "preset-option-desc"));
        btn.addEventListener("click", () => applyPreset(preset));
        list.append(btn);
    }
}

function updatePresetHighlight(id) {
    activePresetId = id;
    for (const btn of byId("presetList")?.children || []) {
        btn.setAttribute?.("aria-pressed", String(btn.dataset.presetId === id));
    }
    const nameEl = byId("activePresetName");
    if (nameEl) {
        const hit = DEMO_PRESETS.find(p => p.id === id);
        nameEl.textContent = hit ? ("Ca " + Number(hit.num) + " · " + hit.title) : "Chưa chọn";
        nameEl.classList?.toggle("is-selected", Boolean(hit));
    }
}

function applyPreset(preset) {
    if (!diseases[preset.disease]) return;
    cancelPendingDiagnosis();
    hidePopoverElement(byId("presetPickerPopover"));
    if (preset.disease !== currentDisease) {
        selectDisease(preset.disease, {transition: false});
    }
    if (!showAllViews && currentView !== "workspace") {
        switchView("workspace");
    }
    whyExpanded = false;
    const techDetails = byId("techDetails");
    if (techDetails) techDetails.open = false;
    fillFormInputs(preset.inputs);
    updatePresetHighlight(preset.id);
    markResultStale();
    byId("diagnosisForm")?.requestSubmit?.();
}

function fillFormInputs(values) {
    const form = byId("diagnosisForm");
    const disease = diseases[currentDisease];
    if (!form || !disease) return;
    clearErrors(form);
    for (const field of disease.fields) {
        if (!(field.key in values)) continue;
        const val = values[field.key];
        const numInput = form.elements.namedItem("inputs." + field.key);
        const card = numInput?.closest?.(".field");
        const slider = card?.querySelector?.(".metric-slider");
        const toggle = card?.querySelector?.(".missing-toggle");
        if (!numInput) continue;

        if (val === null || val === undefined || val === "") {
            numInput.value = "";
            numInput.placeholder = "Chưa biết";
            card?.classList?.add("is-missing");
            toggle?.setAttribute?.("aria-pressed", "true");
            if (slider) slider.disabled = true;
        } else {
            numInput.value = String(val);
            numInput.placeholder = "";
            card?.classList?.remove("is-missing");
            toggle?.setAttribute?.("aria-pressed", "false");
            if (slider) {
                slider.disabled = false;
                syncSliderVars(slider, Number(val));
                slider.setAttribute("aria-valuetext", numberFormat.format(Number(val)));
            }
        }
    }
    updateWaitingPlaceholder();
}

/* ===== Disease Selection, Live What-If & Form Rendering ===== */
function scheduleLiveDiagnosis() {
    if (!liveAutoRun) return;
    clearTimeout(liveDebounceTimer);
    liveDebounceTimer = setTimeout(() => {
        const form = byId("diagnosisForm");
        if (form && !form.inert) {
            runDiagnosis({preventDefault() {}, currentTarget: form}, {preserveFocus: true});
        }
    }, 220);
}

function selectDisease(key, {transition = true} = {}) {
    const perform = () => {
        cancelPendingDiagnosis();
        currentDisease = key;
        selection++;
        activePresetId = null;
        whyExpanded = false;
        updatePresetHighlight(null);
        const disease = diseases[key];
        for (const tab of byId("diseaseTabs").children) {
            tab.setAttribute("aria-pressed", String(tab.dataset.disease === key));
        }
        byId("groupName").textContent = disease.name;
        const dataset = disease.dataset.toUpperCase();
        byId("outputDataset").textContent = dataset + (disease.has_target_rules ? " · ML + Hệ luật" : " · Chỉ ML");
        byId("modelDataset").textContent = dataset + " · Kiểm chứng chéo 5-fold";
        updateInputInfoPopover(disease);
        const techDetails = byId("techDetails");
        if (techDetails) techDetails.open = false;
        renderForm(disease);
        byId("emptyState").querySelector(".flow")?.classList.toggle("ml-only", !disease.has_target_rules);
        updateWaitingPlaceholder();
        clearResult();
        replayWaitingPulse();
        loadModelStats(key, selection);
    };

    if (transition) {
        runViewTransition(document, perform);
    } else {
        perform();
    }
}

async function start() {
    initThemeToggle();
    initPopovers();
    initCopyCommands();
    initNavigation();
    initModelTableSorting();
    initChartMetricSwitcher();
    initTreeControls();

    byId("refreshHistoryBtn")?.addEventListener("click", () => {
        loadHistory();
        showToast("Đã làm mới lịch sử từ SQLite.");
    });

    byId("staleRerunBtn")?.addEventListener("click", () => {
        byId("diagnosisForm")?.requestSubmit?.();
    });
    byId("waitRunBtn")?.addEventListener("click", () => {
        byId("diagnosisForm")?.requestSubmit?.();
    });
    byId("waitDemoBtn")?.addEventListener("click", () => {
        const preset = DEMO_PRESETS.find(item => item.id === "c5");
        if (preset) applyPreset(preset);
    });

    byId("liveAutoToggle")?.addEventListener("click", event => {
        liveAutoRun = !liveAutoRun;
        if (!liveAutoRun) clearTimeout(liveDebounceTimer);
        event.currentTarget.setAttribute("aria-pressed", String(liveAutoRun));
        showToast(liveAutoRun
            ? "Đã bật tự chạy khi kéo thanh trượt."
            : "Đã tắt tự chạy khi kéo.");
        if (liveAutoRun) scheduleLiveDiagnosis();
    });

    byId("resetDefaultsBtn")?.addEventListener("click", () => {
        const disease = diseases[currentDisease];
        if (!disease) return;
        cancelPendingDiagnosis();
        const defaults = Object.fromEntries(disease.fields.map(f => [f.key, f.default]));
        fillFormInputs(defaults);
        updatePresetHighlight(null);
        markResultStale();
        showToast("Đã đặt lại chỉ số mặc định.");
        if (liveAutoRun) scheduleLiveDiagnosis();
    });

    document.addEventListener("keydown", event => {
        if ((event.ctrlKey || event.metaKey) && event.key === "Enter" && currentView === "workspace") {
            const form = byId("diagnosisForm");
            if (form && !form.inert) {
                event.preventDefault();
                form.requestSubmit?.();
            }
        }
    });

    try {
        diseases = await fetchJson("/api/diseases");
        renderPresets();
        const tabs = byId("diseaseTabs");
        tabs.replaceChildren();
        for (const key of ["heart", "diabetes", "liver", "kidney"]) {
            const disease = diseases[key];
            const tab = make("button", undefined, "disease-tab");
            tab.type = "button";
            tab.dataset.disease = key;
            const iconBox = make("span", undefined, "tab-icon");
            iconBox.append(makeIconSvg(DISEASE_ICON_PATHS[key] || DISEASE_ICON_PATHS.heart));
            const top = make("span", undefined, "tab-top");
            top.append(
                make("span", disease.dataset.toUpperCase(), "tab-code"),
                make("span", disease.has_target_rules ? "ML + Luật" : "Chỉ ML", "tab-mode" + (disease.has_target_rules ? " is-hybrid" : ""))
            );
            const title = make("strong", disease.name.replace(/^Bệnh /, ""));
            tab.append(iconBox, top, title);
            tab.addEventListener("click", () => { if (key !== currentDisease) selectDisease(key); });
            tabs.append(tab);
        }
        selectDisease(currentDisease, {transition: false});
    } catch {
        byId("diagnosisForm").textContent = "Chưa tải được biểu mẫu. Hãy tải lại trang để thử lại.";
        byId("modelStatus").textContent = "Chưa tải được thông tin bộ dữ liệu.";
        const brief = byId("activeModelBrief");
        if (brief) brief.textContent = "Chưa sẵn sàng";
    }
    loadHistory();
}

function setSubmitStale(isStale) {
    const submit = byId("diagnosisForm")?.querySelector?.("button[type=submit]");
    if (!submit) return;
    submit.classList?.toggle("is-stale", isStale);
    submit.textContent = isStale ? "Chạy lại suy luận" : "Chạy suy luận";
}

function clearResult() {
    byId("loading").hidden = true;
    byId("resultSection").hidden = true;
    byId("resultSection").classList?.remove("is-stale");
    const stale = byId("staleNotice");
    if (stale) stale.hidden = true;
    setSubmitStale(false);
    byId("emptyState").hidden = false;
}

function cancelPendingDiagnosis() {
    clearTimeout(liveDebounceTimer);
    diagnosisRequest++;
    const form = byId("diagnosisForm");
    if (form) {
        form.inert = false;
        const submit = form.querySelector?.("button[type=submit]");
        if (submit) submit.disabled = false;
    }
    const loading = byId("loading");
    if (loading) loading.hidden = true;
    if (byId("resultSection")?.hidden && byId("emptyState")) {
        byId("emptyState").hidden = false;
    }
}

function markResultStale() {
    inputRevision++;
    const section = byId("resultSection");
    if (section && !section.hidden) {
        section.classList?.add("is-stale");
        const stale = byId("staleNotice");
        if (stale) stale.hidden = false;
        setSubmitStale(true);
    }
}

/* ===== Accessible Inline Field Error Helpers ===== */
function linkFieldError(input, shown) {
    const errorId = input.dataset?.error;
    if (!errorId) return;
    const ids = (input.getAttribute?.("aria-describedby") || "")
        .split(/\s+/)
        .filter(id => id && id !== errorId);
    if (shown) ids.push(errorId);
    if (ids.length) input.setAttribute?.("aria-describedby", ids.join(" "));
    else input.removeAttribute?.("aria-describedby");
}

function announceFieldError(input, message) {
    const announcer = byId("formErrorAnnouncer");
    if (!announcer) return;
    const label = input.labels?.[0]?.textContent?.trim();
    clearTimeout(errorAnnounceTimer);
    announcer.textContent = "";
    announcedErrorField = input;
    errorAnnounceTimer = setTimeout(() => {
        announcer.textContent = (label ? label + ": " : "") + message;
    }, 500);
}

function setFieldError(input, message, {announce = false} = {}) {
    const errorId = input.dataset?.error;
    const errEl = errorId ? byId(errorId) : null;
    const card = input.closest?.(".field");
    if (errEl) {
        const icon = make("span", "!", "field-error-icon");
        icon.setAttribute?.("role", "img");
        icon.setAttribute?.("aria-label", "Lỗi");
        errEl.replaceChildren(icon, make("span", message));
        errEl.hidden = false;
    }
    input.classList?.add("is-invalid");
    card?.classList?.add("has-error");
    input.setAttribute?.("aria-invalid", "true");
    linkFieldError(input, true);
    if (announce) announceFieldError(input, message);
}

function clearFieldError(input) {
    const errorId = input.dataset?.error;
    const errEl = errorId ? byId(errorId) : null;
    const card = input.closest?.(".field");
    if (errEl) {
        errEl.replaceChildren();
        errEl.hidden = true;
    }
    input.classList?.remove("is-invalid");
    card?.classList?.remove("has-error");
    input.setAttribute?.("aria-invalid", "false");
    linkFieldError(input, false);
    if (announcedErrorField === input) {
        clearTimeout(errorAnnounceTimer);
        const announcer = byId("formErrorAnnouncer");
        if (announcer) announcer.textContent = "";
        announcedErrorField = null;
    }
}

function validateSingleField(input, field, dataset, {announce = false} = {}) {
    if (input.validity?.badInput) {
        setFieldError(input, formatFieldGuidance(field, dataset, "badInput"), {announce});
        return false;
    }
    if (input.value === "") {
        clearFieldError(input);
        return true;
    }
    const num = Number(input.value);
    if (!Number.isFinite(num)) {
        setFieldError(input, formatFieldGuidance(field, dataset, "badInput"), {announce});
        return false;
    }
    if (num < field.min || num > field.max) {
        setFieldError(input, formatFieldGuidance(field, dataset, "range"), {announce});
        return false;
    }
    if (field.key === "age" && !Number.isInteger(num)) {
        setFieldError(input, formatFieldGuidance(field, dataset, "integer"), {announce});
        return false;
    }
    clearFieldError(input);
    return true;
}

function renderForm(disease) {
    const form = byId("diagnosisForm");
    clearTimeout(errorAnnounceTimer);
    announcedErrorField = null;
    const announcer = byId("formErrorAnnouncer");
    if (announcer) announcer.textContent = "";
    form.inert = false;
    form.replaceChildren();

    for (const field of disease.fields) {
        const group = make("div", undefined, "field");
        const top = make("div", undefined, "field-top");
        const displayLabel = cleanFieldLabel(field);
        const label = make("label", displayLabel);
        const input = make("input");
        input.type = "number";
        input.id = "field_" + field.key;
        input.name = "inputs." + field.key;
        input.value = String(field.default);
        input.min = String(field.min);
        input.max = String(field.max);
        input.step = String(field.step || 1);
        input.inputMode = field.step && field.step < 1 ? "decimal" : "numeric";
        input.setAttribute("aria-invalid", "false");
        input.dataset.error = input.id + "_error";
        label.htmlFor = input.id;

        const missingBtn = make("button", "Chưa biết", "missing-toggle");
        missingBtn.type = "button";
        missingBtn.setAttribute("aria-pressed", "false");
        missingBtn.setAttribute("aria-label", "Đánh dấu " + displayLabel + " là chưa biết");
        top.append(label, missingBtn);

        const range = make("small", numberFormat.format(field.min) + " – " + numberFormat.format(field.max));
        range.id = input.id + "_range";
        input.setAttribute("aria-describedby", range.id);
        const entry = make("div", undefined, "entry");
        entry.append(input, range);

        const fieldError = make("p", undefined, "field-error");
        fieldError.id = input.id + "_error";
        fieldError.hidden = true;

        const sliderWrap = make("div", undefined, "slider-wrap");
        const slider = make("input", undefined, "metric-slider");
        slider.type = "range";
        slider.min = String(field.min);
        slider.max = String(field.max);
        slider.step = String(field.step || 1);
        slider.setAttribute("aria-label", "Thanh trượt " + displayLabel);
        syncSliderVars(slider, Number(field.default));
        slider.setAttribute("aria-valuetext", numberFormat.format(Number(field.default)));
        sliderWrap.append(slider);

        let savedBeforeMissing = String(field.default);

        slider.addEventListener("input", () => {
            const val = Number(slider.value);
            input.value = slider.value;
            input.placeholder = "";
            savedBeforeMissing = slider.value;
            syncSliderVars(slider, val);
            slider.setAttribute("aria-valuetext", numberFormat.format(val));
            group.classList.remove("is-missing");
            missingBtn.setAttribute("aria-pressed", "false");
            clearFieldError(input);
            clearFormErrorList();
            updatePresetHighlight(null);
            markResultStale();
            updateWaitingPlaceholder();
            scheduleLiveDiagnosis();
        });

        input.addEventListener("input", () => {
            clearFormErrorList();
            updatePresetHighlight(null);
            markResultStale();
            if (input.value === "" && !input.validity?.badInput) {
                input.placeholder = "Chưa biết";
                group.classList.add("is-missing");
                missingBtn.setAttribute("aria-pressed", "true");
                slider.disabled = true;
                clearFieldError(input);
            } else {
                const num = Number(input.value);
                input.placeholder = "";
                savedBeforeMissing = input.value;
                group.classList.remove("is-missing");
                missingBtn.setAttribute("aria-pressed", "false");
                slider.disabled = false;
                if (Number.isFinite(num)) {
                    syncSliderVars(slider, num);
                    slider.setAttribute("aria-valuetext", numberFormat.format(num));
                }
                if (input.classList.contains("is-invalid")) {
                    validateSingleField(input, field, disease.dataset, {announce: false});
                }
            }
            updateWaitingPlaceholder();
        });

        input.addEventListener("blur", () => {
            validateSingleField(input, field, disease.dataset, {announce: true});
        });

        missingBtn.addEventListener("click", () => {
            const makeMissing = missingBtn.getAttribute("aria-pressed") !== "true";
            clearFieldError(input);
            clearFormErrorList();
            updatePresetHighlight(null);
            markResultStale();
            if (makeMissing) {
                if (input.value !== "") savedBeforeMissing = input.value;
                input.value = "";
                input.placeholder = "Chưa biết";
                slider.disabled = true;
                group.classList.add("is-missing");
                missingBtn.setAttribute("aria-pressed", "true");
            } else {
                const restored = savedBeforeMissing || String(field.default);
                input.value = restored;
                input.placeholder = "";
                slider.disabled = false;
                group.classList.remove("is-missing");
                missingBtn.setAttribute("aria-pressed", "false");
                syncSliderVars(slider, Number(restored));
                slider.setAttribute("aria-valuetext", numberFormat.format(Number(restored)));
                input.focus();
            }
            updateWaitingPlaceholder();
            scheduleLiveDiagnosis();
        });

        group.append(top, entry, fieldError, sliderWrap);
        form.append(group);
    }

    const errors = make("ul", undefined, "errors");
    errors.id = "diagnosisErrors";
    errors.setAttribute("role", "alert");
    errors.hidden = true;
    const button = make("button", "Chạy suy luận", "submit");
    button.type = "submit";
    form.append(errors, button);
    form.onsubmit = event => runDiagnosis(event, {preserveFocus: false});
}

function clearFormErrorList() {
    const errList = byId("diagnosisErrors");
    if (errList) {
        errList.replaceChildren();
        errList.hidden = true;
    }
}

function clearErrors(form) {
    clearFormErrorList();
    for (const input of form.querySelectorAll?.('input[type="number"]') || []) {
        clearFieldError(input);
    }
}

function showErrors(form, errors) {
    const list = byId("diagnosisErrors");
    const disease = diseases[currentDisease];
    const fieldByKey = Object.fromEntries((disease?.fields || []).map(f => [f.key, f]));
    list.replaceChildren();
    let hasGeneralError = false;

    for (const [path, message] of Object.entries(errors)) {
        const input = form.elements.namedItem(path);
        if (input && path.startsWith("inputs.")) {
            const key = path.slice("inputs.".length);
            const field = fieldByKey[key];
            let inlineMsg = message;
            if (field && disease) {
                if (/trong khoảng|số nguyên/i.test(message)) {
                    inlineMsg = formatFieldGuidance(field, disease.dataset, "range");
                } else if (/số hợp lệ|hữu hạn|phải là số/i.test(message)) {
                    inlineMsg = formatFieldGuidance(field, disease.dataset, "badInput");
                }
            }
            setFieldError(input, inlineMsg, {announce: false});
        } else {
            const li = make("li", message);
            li.id = "error_" + path.replaceAll(".", "_");
            list.append(li);
            hasGeneralError = true;
        }
    }
    list.hidden = !hasGeneralError;
    form.querySelector(".is-invalid")?.focus();
}

async function runDiagnosis(event, {preserveFocus = false} = {}) {
    event.preventDefault();
    const form = event.currentTarget;
    if (form.inert) return;
    const disease = diseases[currentDisease];
    const version = selection;
    clearErrors(form);
    const inputs = {};
    const errors = {};
    for (const field of disease.fields) {
        const el = form.elements.namedItem("inputs." + field.key);
        if (el.validity.badInput) {
            errors[el.name] = formatFieldGuidance(field, disease.dataset, "badInput");
        }
        inputs[field.key] = el.value === "" ? null : el.value;
    }
    if (Object.keys(errors).length) {
        clearResult();
        showErrors(form, errors);
        return;
    }

    const requestId = ++diagnosisRequest;
    const revision = inputRevision;
    const isCurrentRequest = () => version === selection && requestId === diagnosisRequest;
    if (!preserveFocus) form.inert = true;
    const submit = form.querySelector("button[type=submit]");
    submit.disabled = true;
    byId("emptyState").hidden = true;
    byId("resultSection").classList?.add("is-stale");
    if (!preserveFocus) byId("loading").hidden = false;

    try {
        const data = await fetchJson("/api/diagnose", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({disease: currentDisease, inputs}),
        });
        loadHistory();
        if (!isCurrentRequest() || revision !== inputRevision) return;
        renderTrace(data.trace, disease, {preserveWhy: preserveFocus});
        byId("resultSection").hidden = false;
        byId("resultSection").classList?.remove("is-stale");
        const stale = byId("staleNotice");
        if (stale) stale.hidden = true;
        setSubmitStale(false);
        if (!preserveFocus) {
            byId("outputTitle").focus({preventScroll: true});
            if (typeof window !== "undefined" && window.matchMedia?.("(max-width: 980px)").matches) {
                byId("outputTitle").scrollIntoView({block: "start"});
            }
        }
    } catch (error) {
        if (!isCurrentRequest() || revision !== inputRevision) return;
        form.inert = false;
        clearResult();
        showErrors(form, error.fields || {body: "Chưa nhận được kết quả. Vui lòng thử lại."});
    } finally {
        if (isCurrentRequest()) {
            form.inert = false;
            submit.disabled = false;
            byId("loading").hidden = true;
            if (byId("resultSection").hidden) byId("emptyState").hidden = false;
        }
    }
}

/* ===== Comparison, Pipeline & Fuzzy Curve ===== */
function buildSupportGauge(combined, mlScore, ruleScore, hasTargetRules) {
    const svg = makeSvg("svg", {viewBox: "0 0 180 114", class: "gauge-svg", "aria-hidden": "true"});
    if (!svg) return null;
    const cx = 90, cy = 94, r = 68;
    const clamp = v => Math.min(1, Math.max(0, v));
    const pt = frac => {
        const ang = Math.PI * (1 - clamp(frac));
        return [cx + r * Math.cos(ang), cy - r * Math.sin(ang)];
    };
    const arcLen = Math.PI * r;
    const clampedCombined = clamp(combined);

    const bgPath = makeSvg("path", {
        d: `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`,
        fill: "none", stroke: "var(--surface-3)", "stroke-width": 13, "stroke-linecap": "round",
    });
    const fgPath = makeSvg("path", {
        d: `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`,
        fill: "none", stroke: "var(--tone-accent)", "stroke-width": 13, "stroke-linecap": "round",
        class: "gauge-arc-fg",
    });
    fgPath.style?.setProperty?.("--arc-total", arcLen.toFixed(1));
    fgPath.style?.setProperty?.("--arc-offset", (arcLen * (1 - clampedCombined)).toFixed(1));

    // 50% threshold tick at top center
    const tick = makeSvg("line", {
        x1: cx, y1: cy - r - 11, x2: cx, y2: cy - r + 11,
        stroke: "var(--ink)", "stroke-width": 2, "stroke-dasharray": "3 2", opacity: 0.72,
    });
    const tickLabel = makeSvg("text", {
        x: cx, y: 11, "text-anchor": "middle", fill: "var(--muted)", "font-size": 10, "font-family": "var(--font-mono)",
    });
    tickLabel.textContent = "50%";
    const leftLabel = makeSvg("text", {x: 16, y: 110, fill: "var(--muted)", "font-size": 9.5, "font-family": "var(--font-mono)"});
    leftLabel.textContent = "0%";
    const rightLabel = makeSvg("text", {x: 164, y: 110, "text-anchor": "end", fill: "var(--muted)", "font-size": 9.5, "font-family": "var(--font-mono)"});
    rightLabel.textContent = "100%";

    // Animated pointer needle sweeping to combined_score
    const needleGroup = makeSvg("g", {class: "gauge-needle"});
    const deg = -90 + clampedCombined * 180;
    needleGroup.style?.setProperty?.("--needle-deg", deg.toFixed(1) + "deg");
    needleGroup.append(
        makeSvg("line", {x1: cx, y1: cy, x2: cx, y2: cy - r + 14, stroke: "var(--tone-accent)", "stroke-width": 2.4, "stroke-linecap": "round"}),
        makeSvg("circle", {cx, cy, r: 4.5, fill: "var(--tone-accent)", stroke: "var(--surface)", "stroke-width": 2})
    );

    svg.append(bgPath, fgPath, tick, tickLabel, leftLabel, rightLabel, needleGroup);

    // Marker pins for ML and Rule with spring pop-in
    const [mx, my] = pt(mlScore);
    const mlPin = makeSvg("circle", {cx: mx.toFixed(1), cy: my.toFixed(1), r: 4.8, fill: "var(--brand)", stroke: "var(--surface)", "stroke-width": 2, class: "gauge-pin"});
    mlPin.style?.setProperty?.("--delay", "240ms");
    const mlTitle = makeSvg("title");
    mlTitle.textContent = "ML: " + scoreFormat.format(mlScore);
    mlPin.append(mlTitle);
    svg.append(mlPin);

    if (ruleScore !== null) {
        const [rx, ry] = pt(ruleScore);
        const ripple = makeSvg("circle", {cx: rx.toFixed(1), cy: ry.toFixed(1), r: 5, fill: "none", stroke: "var(--conflict-accent)", "stroke-width": 1.6, class: "gauge-pin-pulse"});
        const rulePin = makeSvg("circle", {cx: rx.toFixed(1), cy: ry.toFixed(1), r: 4.8, fill: "var(--conflict-accent)", stroke: "var(--surface)", "stroke-width": 2, class: "gauge-pin"});
        rulePin.style?.setProperty?.("--delay", "360ms");
        const ruleTitle = makeSvg("title");
        ruleTitle.textContent = "Hệ luật: " + scoreFormat.format(ruleScore);
        rulePin.append(ruleTitle);
        svg.append(ripple, rulePin);
    }

    const wrap = make("div", undefined, "gauge-wrap");
    wrap.setAttribute?.("aria-hidden", "true");
    const legend = make("div", undefined, "gauge-legend");
    const mlKey = make("span", undefined, "gauge-key");
    mlKey.append(make("i"), "ML");
    legend.append(mlKey);
    if (ruleScore !== null) {
        const ruleKey = make("span", undefined, "gauge-key is-rule");
        ruleKey.append(make("i"), "Luật");
        legend.append(ruleKey);
    }
    wrap.append(svg, make("span", hasTargetRules ? "Kim: điểm kết hợp" : "Kim: điểm ML", "gauge-caption"), legend);
    return wrap;
}

function buildCompareStrip(mlScore, ruleScore, combinedScore, hasTargetRules) {
    const strip = make("div", undefined, "compare-strip");
    strip.append(make("strong", "So sánh điểm hỗ trợ", "compare-title"));
    const items = [{label: "ML", val: mlScore, cls: "", delay: "40ms"}];
    if (hasTargetRules || ruleScore !== null) {
        items.push(
            {label: "Hệ luật", val: ruleScore, cls: " is-rule", delay: "130ms"},
            {label: "Kết hợp", val: combinedScore, cls: " is-combined", delay: "220ms"}
        );
    }
    for (const item of items) {
        const row = make("div", undefined, "compare-row");
        const track = make("div", undefined, "compare-track");
        const fill = make("div", undefined, "compare-fill" + item.cls + (item.val === null ? " is-empty" : ""));
        if (item.val !== null && fill.style) {
            fill.style.width = (Math.min(1, Math.max(0, item.val)) * 100).toFixed(1) + "%";
            fill.style.setProperty?.("--delay", item.delay);
        }
        track.append(fill);
        row.append(
            make("span", item.label),
            track,
            make("span", item.val === null ? "—" : scoreFormat.format(item.val))
        );
        strip.append(row);
    }
    const axis = make("div", undefined, "compare-axis");
    axis.append(make("span", "0%"), make("span", "Ngưỡng 50%"), make("span", "100%"));
    strip.append(axis);
    if (ruleScore === null) {
        strip.append(make("p", hasTargetRules ? "Không có luật đích khớp." : "Bộ dữ liệu chưa có luật đích.", "compare-note"));
    }
    return strip;
}

function makePipeConnector(symbol, delayMs) {
    const svg = makeSvg("svg", {viewBox: "0 0 36 18", class: "pipe-connector", "aria-hidden": "true"});
    if (!svg) return make("span", symbol, "pipe-op");
    if (symbol === "+") {
        svg.append(
            makeSvg("line", {x1: 2, y1: 9, x2: 34, y2: 9, class: "pipe-conn-base"}),
            makeSvg("circle", {cx: 18, cy: 9, r: 7.5, fill: "var(--surface)", stroke: "var(--line-strong)", "stroke-width": 1.4}),
            makeSvg("path", {d: "M15 9h6M18 6v6", stroke: "var(--brand)", "stroke-width": 1.8, "stroke-linecap": "round"})
        );
    } else {
        const pulse = makeSvg("path", {d: "M 2 9 L 30 9", class: "pipe-conn-pulse"});
        pulse.style?.setProperty?.("--delay", delayMs + "ms");
        svg.append(
            makeSvg("path", {d: "M 2 9 L 30 9 M 25 4 L 31 9 L 25 14", class: "pipe-conn-base"}),
            pulse
        );
    }
    return svg;
}

function buildFuzzyCurveFigure(fact, disease, dataset, index) {
    if (typeof document.createElementNS !== "function") return null;
    const spec = findFactSpec(dataset, fact.key);
    const field = disease.fields.find(f => f.key === fact.feature);
    if (!spec || !field) return null;

    const min = field.min;
    const max = field.max;
    const span = max - min || 1;
    const w = 108, h = 42, padX = 6, padY = 6;
    const xOf = v => padX + (Math.min(max, Math.max(min, v)) - min) / span * (w - padX * 2);
    const yOf = m => h - padY - Math.min(1, Math.max(0, m)) * (h - padY * 2);

    let pts = [];
    if (spec.kind === "ramp") {
        const [lo, hi] = spec.bounds;
        pts = [[xOf(min), yOf(0)], [xOf(lo), yOf(0)], [xOf(hi), yOf(1)], [xOf(max), yOf(1)]];
    } else if (spec.kind === "at_least") {
        const cut = spec.bounds;
        pts = [[xOf(min), yOf(0)], [xOf(cut), yOf(0)], [xOf(cut), yOf(1)], [xOf(max), yOf(1)]];
    } else if (spec.kind === "between") {
        const [lo, hi] = spec.bounds;
        pts = [[xOf(min), yOf(0)], [xOf(lo), yOf(0)], [xOf(lo), yOf(1)], [xOf(hi), yOf(1)], [xOf(hi), yOf(0)], [xOf(max), yOf(0)]];
    }
    if (!pts.length) return null;

    const lineStr = pts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
    const areaStr = `${xOf(min).toFixed(1)},${yOf(0).toFixed(1)} ${lineStr} ${xOf(max).toFixed(1)},${yOf(0).toFixed(1)}`;

    const svg = makeSvg("svg", {viewBox: `0 0 ${w} ${h}`, class: "fuzzy-curve-svg", "aria-hidden": "true"});
    const cutY = yOf(0.5).toFixed(1);
    const curveLine = makeSvg("polyline", {points: lineStr, class: "fuzzy-curve-line"});
    curveLine.style?.setProperty?.("--delay", (60 + index * 70) + "ms");

    svg.append(
        makeSvg("polygon", {points: areaStr, class: "fuzzy-curve-area"}),
        makeSvg("line", {x1: padX, y1: cutY, x2: w - padX, y2: cutY, class: "fuzzy-curve-cut"}),
        curveLine
    );

    if (fact.value !== null && fact.membership !== null) {
        const vx = xOf(fact.value);
        const vy = yOf(fact.membership);
        const isBoundary = Math.abs(fact.membership - 0.5) < 1e-9;
        const dotColor = fact.value_boolean ? "var(--brand)" : (isBoundary ? "var(--mod-accent)" : "var(--muted)");
        const drop = makeSvg("line", {x1: vx.toFixed(1), y1: vy.toFixed(1), x2: vx.toFixed(1), y2: yOf(0).toFixed(1), class: "fuzzy-curve-drop"});
        drop.style?.setProperty?.("--tone-dot", dotColor);
        const dot = makeSvg("circle", {cx: vx.toFixed(1), cy: vy.toFixed(1), r: 3.8, fill: dotColor, stroke: "var(--surface)", "stroke-width": 1.6, class: "fuzzy-curve-dot"});
        dot.style?.setProperty?.("--dot-delay", (260 + index * 70) + "ms");
        svg.append(drop, dot);
    }

    const fig = make("figure", undefined, "fuzzy-curve-figure");
    fig.append(svg);
    return fig;
}

function renderLivePipeline(trace, disease, missing) {
    const container = byId("livePipeline");
    const details = byId("fusionDetails");
    if (!container || !details) return;
    const result = trace.result;
    const targetRules = trace.fired_rules.filter(r => r.used_in_fusion);

    const head = make("div", undefined, "pipeline-head");
    head.append(make("p", "Công thức phép gộp", "pipeline-title"));

    // Copy formula button (follows copy-button guide)
    const copyWrap = make("span", undefined, "copy-wrap");
    const copyBtn = make("button", undefined, "copy-btn");
    copyBtn.type = "button";
    copyBtn.setAttribute?.("command", "--copy");
    copyBtn.setAttribute?.("commandfor", "fusionFormulaText");
    copyBtn.setAttribute?.("aria-label", "Sao chép công thức phép gộp");
    copyBtn.append(
        make("span", "⧉", "icon-copy"),
        make("span", "✓", "icon-check"),
        make("span", "Chép công thức")
    );
    const copyTip = make("span", "", "copy-tip");
    copyTip.setAttribute?.("role", "status");
    copyWrap.append(copyBtn, copyTip);
    head.append(copyWrap);

    const nodes = make("div", undefined, "pipeline-nodes");
    const mlNode = make("div", undefined, "pipe-node");
    mlNode.style?.setProperty?.("--delay", "20ms");
    mlNode.append(
        make("small", "Nhánh ML · " + trace.ml.model + (missing.length ? " (điền trung vị)" : "")),
        make("strong", scoreFormat.format(trace.ml.score))
    );

    const ruleNode = make("div", undefined, "pipe-node" + (result.rule_score === null ? " is-inactive" : ""));
    ruleNode.style?.setProperty?.("--delay", "110ms");
    ruleNode.append(
        make("small", result.rule_score === null
            ? (disease.has_target_rules ? "Luật đích (0 khớp)" : "Chưa có luật đích")
            : ("Luật đích (" + targetRules.length + " luật khớp)")),
        make("strong", result.rule_score === null ? "Chưa có điểm" : scoreFormat.format(result.rule_score))
    );

    const finalNode = make("div", undefined, "pipe-node is-final");
    finalNode.style?.setProperty?.("--delay", "200ms");
    finalNode.append(
        make("small", (disease.has_target_rules ? "Kết hợp" : "Điểm ML") + " · Nhãn " + result.predicted_label),
        make("strong", scoreFormat.format(result.combined_score))
    );

    nodes.append(mlNode, makePipeConnector("+", 90), ruleNode, makePipeConnector("→", 180), finalNode);

    const formula = make("div", undefined, "formula-box");
    formula.id = "fusionFormulaText";
    if (result.rule_score === null) {
        formula.append(
            make("span", "Không có luật đích kích hoạt — giữ nguyên điểm ML:"),
            "C_new = p = " + mathFormat.format(trace.ml.score) + " (" + scoreFormat.format(result.combined_score) + ")"
        );
    } else {
        if (targetRules.length > 1) {
            const factors = targetRules.map(r => "(1 − " + mathFormat.format(r.cf) + ")").join(" × ");
            formula.append(make("span", "1) Gộp " + targetRules.length + " luật đích: C_rule = 1 − " + factors + " = " + mathFormat.format(result.rule_score)));
        }
        formula.append(
            make("span", (targetRules.length > 1 ? "2) " : "") + "Gộp ML một lần: C_new = C_rule + p × (1 − C_rule)"),
            mathFormat.format(result.rule_score) + " + " + mathFormat.format(trace.ml.score) + " × (1 − " + mathFormat.format(result.rule_score) + ") = " + mathFormat.format(result.combined_score)
        );
    }

    container.replaceChildren(make("p", disease.has_target_rules ? "Sơ đồ kết hợp điểm" : "Sơ đồ điểm ML", "pipeline-title"), nodes);
    container.hidden = false;
    details.replaceChildren(head, formula);
    details.hidden = false;
}

/* ===== Main Trace Renderer ===== */
function renderTrace(trace, disease, {preserveWhy = false} = {}) {
    const result = trace.result;
    const inputs = byId("traceInputs");
    const facts = byId("traceFacts");
    const rules = byId("traceRules");
    const summary = byId("traceResult");
    inputs.replaceChildren();
    facts.replaceChildren();
    rules.replaceChildren();

    const missing = [];
    disease.fields.forEach((field, idx) => {
        const matched = trace.facts.find(fact => fact.feature === field.key);
        const value = matched?.value;
        const unit = matched?.unit;
        if (value == null) missing.push(field.key);
        const item = make("li", undefined, "trace-input-chip" + (value == null ? " is-missing" : ""));
        item.style?.setProperty?.("--delay", (idx * 45) + "ms");
        const labelText = cleanFieldLabel(field);
        const showUnit = unit && unit !== "years" && !labelText.includes(unit);
        item.append(
            make("span", labelText + " · "),
            make("strong", value == null ? "Chưa biết" : (numberFormat.format(value) + (showUnit ? " " + unit : "")))
        );
        inputs.append(item);
    });

    const derivedFacts = trace.facts.filter(f => f.key !== null);
    derivedFacts.forEach((fact, idx) => {
        const row = make("li", undefined, "fact-card");
        row.style?.setProperty?.("--delay", (idx * 65) + "ms");
        const head = make("div", undefined, "fact-head");
        const stateText = fact.value_boolean === null ? "Chưa biết" : (fact.value_boolean ? "Đúng" : "Sai");
        const stateCls = fact.value_boolean === null ? "is-unknown" : (fact.value_boolean ? "is-true" : "is-false");
        head.append(
            make("b", factLabels[fact.key] || fact.key),
            make("span", stateText, "fact-status " + stateCls)
        );
        row.append(head);

        const curveFig = buildFuzzyCurveFigure(fact, disease, trace.target, idx);
        if (fact.membership !== null || curveFig) {
            const bodyGrid = make("div", undefined, "fact-body-grid" + (curveFig ? "" : " is-bar-only"));
            if (fact.membership !== null) {
                const meterRow = make("div", undefined, "fact-meter-row");
                const meter = make("div", undefined, "fact-meter");
                const isBoundary = Math.abs(fact.membership - 0.5) < 1e-9;
                const fill = make("div", undefined, "fact-meter-fill" + (fact.value_boolean ? " is-true" : (isBoundary ? " is-boundary" : "")));
                if (fill.style) {
                    fill.style.width = (Math.min(1, Math.max(0, fact.membership)) * 100).toFixed(1) + "%";
                    fill.style.setProperty?.("--delay", (80 + idx * 70) + "ms");
                }
                meter.append(fill);
                const labelVal = "μ = " + scoreFormat.format(fact.membership) + (isBoundary ? " (biên 50%)" : "");
                meterRow.append(meter, make("span", labelVal, "fact-meter-val"));
                bodyGrid.append(meterRow);
            } else {
                bodyGrid.append(make("span", "Chưa có giá trị để tính mức liên thuộc", "fact-meter-val"));
            }
            if (curveFig) bodyGrid.append(curveFig);
            row.append(bodyGrid);
        }
        facts.append(row);
    });
    if (!facts.children.length) {
        facts.append(make("li", "Bộ dữ liệu này chưa có dữ kiện dẫn xuất cho hệ luật.", "trace-empty"));
    }

    trace.fired_rules.forEach((rule, idx) => {
        const row = make("li", undefined, "rule-card" + (rule.used_in_fusion ? "" : " is-secondary"));
        row.style?.setProperty?.("--delay", (idx * 75) + "ms");
        const top = make("div", undefined, "rule-top");
        const left = make("div", undefined, "rule-top-left");
        left.append(
            make("code", rule.id),
            make("span", rule.used_in_fusion ? "Dùng để gộp" : "Luật phụ", "rule-role")
        );
        top.append(left, make("span", "CF " + scoreFormat.format(rule.cf), "rule-cf"));

        const conds = make("div", undefined, "rule-conds");
        conds.append(make("span", "NẾU:"));
        rule.conditions.forEach((cond, cIdx) => {
            if (cIdx > 0) conds.append(make("span", "và"));
            conds.append(make("span", factLabels[cond] || cond, "cond-pill"));
        });

        const cfBar = make("div", undefined, "rule-cf-bar");
        const cfFill = make("div", undefined, "rule-cf-fill");
        if (cfFill.style) {
            cfFill.style.width = (Math.min(1, Math.max(0, rule.cf)) * 100).toFixed(1) + "%";
            cfFill.style.setProperty?.("--delay", (120 + idx * 75) + "ms");
        }
        cfBar.append(cfFill);

        row.append(top, make("p", rule.conclusion, "rule-conclusion"), conds, cfBar);
        rules.append(row);
    });
    if (!rules.children.length) {
        rules.append(make("li", disease.has_target_rules ? "Chưa có luật nào khớp." : "Bộ dữ liệu này chưa có luật đích.", "trace-empty"));
    }

    // Semantic tone & streamlined presentation-first result
    const mlScore = trace.ml.score;
    const ruleScore = result.rule_score;
    const combined = result.combined_score;
    const mlPos = mlScore >= 0.5;
    const finalPos = result.predicted_label === 1;
    const scoreIncreased = ruleScore !== null && combined > mlScore + 1e-4;
    const isOpen = preserveWhy ? whyExpanded : false;
    whyExpanded = isOpen;

    const tone = !finalPos
        ? "negative"
        : (combined >= 0.7 ? "high" : "moderate");
    summary.setAttribute?.("data-tone", tone);

    let verdictText;
    const thresholdWord = combined === 0.5 ? "đạt" : "vượt";
    if (ruleScore !== null) {
        if (!mlPos && finalPos) {
            verdictText = "Điểm " + thresholdWord + " ngưỡng 50% sau khi kết hợp luật.";
        } else if (finalPos) {
            verdictText = scoreIncreased
                ? "Điểm " + thresholdWord + " ngưỡng 50% và tăng thêm khi kết hợp luật."
                : "Điểm " + thresholdWord + " ngưỡng 50% sau khi kết hợp luật.";
        } else {
            verdictText = "Điểm vẫn dưới ngưỡng 50% sau khi kết hợp luật.";
        }
    } else {
        verdictText = finalPos
            ? "Điểm " + thresholdWord + " ngưỡng 50% theo mô hình ML."
            : "Điểm dưới ngưỡng 50% theo mô hình ML.";
    }
    const verdictEl = make("p", verdictText, "result-verdict");

    const scoreLine = make("div", undefined, "result-score-line");
    const termWrap = make("span", undefined, "score-term");
    termWrap.append(make("span", "Điểm hỗ trợ"));
    const infoBtn = make("button", undefined, "info-btn");
    infoBtn.type = "button";
    infoBtn.setAttribute?.("popovertarget", "supportScoreInfo");
    infoBtn.setAttribute?.("aria-label", "Giải thích Điểm hỗ trợ");
    const infoGlyph = make("span", "ⓘ");
    infoGlyph.setAttribute?.("aria-hidden", "true");
    infoBtn.append(infoGlyph);
    termWrap.append(infoBtn);

    const transition = make("div", undefined, "score-transition");
    const mlPart = make("span", undefined, "score-part is-ml");
    const mlNumEl = make("strong", scoreFormat.format(mlScore), "score-ml-num");
    mlPart.append(mlNumEl, make("span", "(ML)", "score-tag"));

    if (disease.has_target_rules || ruleScore !== null) {
        const arrow = make("span", "→", "score-arrow");
        arrow.setAttribute?.("aria-hidden", "true");
        const finalPart = make("span", undefined, "score-part is-final");
        const finalNumEl = make("strong", scoreFormat.format(combined), "score-final-num");
        finalPart.append(finalNumEl, make("span", "(ML + luật)", "score-tag"));
        transition.append(mlPart, arrow, finalPart);
    } else {
        mlNumEl.className = "score-final-num";
        transition.append(mlPart);
    }
    scoreLine.append(termWrap, transition);

    const visuals = make("div", undefined, "result-visuals");
    const gauge = buildSupportGauge(combined, mlScore, ruleScore, disease.has_target_rules);
    if (gauge) visuals.append(gauge);
    visuals.append(buildCompareStrip(mlScore, ruleScore, combined, disease.has_target_rules));

    const targetRules = trace.fired_rules.filter(r => r.used_in_fusion);
    const secondaryRules = trace.fired_rules.filter(r => !r.used_in_fusion);
    const boundaryFacts = derivedFacts.filter(f => f.membership !== null && Math.abs(f.membership - 0.5) < 1e-9);

    let whyLabel = "Vì sao có kết quả này?";
    if (scoreIncreased) {
        whyLabel = "Vì sao điểm tăng?";
    } else if (disease.has_target_rules && ruleScore === null) {
        whyLabel = "Vì sao điểm không đổi?";
    }

    const whyRow = make("div", undefined, "why-row");
    const whyBtn = make("button", undefined, "why-toggle");
    whyBtn.type = "button";
    whyBtn.setAttribute?.("aria-expanded", String(isOpen));
    whyBtn.setAttribute?.("aria-controls", "whyExplainPanel");
    whyBtn.append(make("span", whyLabel));
    const whyChevron = make("span", "▾", "why-chevron");
    whyChevron.setAttribute?.("aria-hidden", "true");
    whyBtn.append(whyChevron);
    whyRow.append(whyBtn);

    let whySentence;
    if (ruleScore !== null) {
        if (!mlPos && finalPos) {
            whySentence = "Mô hình ML cho điểm dưới ngưỡng (" + scoreFormat.format(mlScore) +
                "), nhưng " + targetRules.length + " luật đích khớp đạt " + scoreFormat.format(ruleScore) +
                ", kéo điểm kết hợp lên " + scoreFormat.format(combined) + ".";
        } else if (targetRules.length > 1) {
            whySentence = "Mô hình ML cho " + scoreFormat.format(mlScore) + " và có " + targetRules.length +
                " luật đích cùng khớp (tổng điểm luật " + scoreFormat.format(ruleScore) +
                "), gộp với ML một lần cho ra " + scoreFormat.format(combined) + ".";
        } else {
            whySentence = "Mô hình ML cho " + scoreFormat.format(mlScore) + " và có 1 luật đích khớp (" +
                scoreFormat.format(ruleScore) + "); điểm kết hợp là " + scoreFormat.format(combined) + ".";
        }
        if (secondaryRules.length) {
            whySentence += " Ngoài ra có " + secondaryRules.length + " luật phụ hiển thị trong Chi tiết kỹ thuật, không cộng vào điểm.";
        }
    } else if (disease.has_target_rules) {
        whySentence = "Không có luật đích nào khớp với các chỉ số hiện tại, nên điểm kết hợp giữ nguyên theo ML.";
        if (boundaryFacts.length) {
            whySentence += " Dữ kiện ở đúng biên 50% chưa được tính là đúng; cần lớn hơn 50%.";
        }
    } else {
        whySentence = "Bộ dữ liệu này chưa có luật đích nên điểm kết hợp giữ nguyên theo mô hình ML.";
    }

    const whyPanel = make("div", undefined, "why-explain");
    whyPanel.id = "whyExplainPanel";
    whyPanel.hidden = !isOpen;
    whyPanel.append(make("p", whySentence, "why-text"));
    if (missing.length) {
        const missingLabels = disease.fields.filter(field => missing.includes(field.key)).map(cleanFieldLabel);
        whyPanel.append(make("p", "Đã nhập " + (disease.fields.length - missing.length) + "/" + disease.fields.length +
            " chỉ số. ML dùng trung vị học từ train cho " + missingLabels.join(", ") + "; hệ luật giữ dữ kiện thiếu ở trạng thái chưa biết.", "why-note"));
    }

    whyBtn.addEventListener?.("click", () => {
        whyExpanded = !whyExpanded;
        whyBtn.setAttribute("aria-expanded", String(whyExpanded));
        whyPanel.hidden = !whyExpanded;
    });

    summary.replaceChildren(verdictEl, scoreLine, visuals, whyRow, whyPanel);

    renderLivePipeline(trace, disease, missing);
}

/* ===== CV Benchmark Chart with Linked Brushing, Sortable Table & Filtered Tree Cards ===== */
function setLinkedModelHighlight(modelName) {
    for (const row of byId("modelChart")?.querySelectorAll?.(".bar-row") || []) {
        row.classList.toggle("is-linked", Boolean(modelName) && row.dataset.model === modelName);
    }
    for (const tr of byId("modelTable")?.tBodies?.[0]?.rows || []) {
        tr.classList.toggle("is-linked", Boolean(modelName) && tr.dataset.model === modelName);
    }
}

function renderModelChart(data, metricKey) {
    const card = byId("modelChart");
    if (!card || !data?.stats?.length) return;
    card.replaceChildren();

    const baseline = data.stats.find(m => m.name.toLowerCase().includes("baseline"));
    const baselineVal = baseline ? baseline[metricKey] : null;

    const legend = make("div", undefined, "chart-legend");
    legend.append(make("strong", "So sánh " + (METRIC_LABELS[metricKey] || metricKey)));
    const items = make("div", undefined, "legend-items");
    items.append(
        make("span", "Mô hình chọn", "legend-dot"),
        make("span", "Mô hình khác", "legend-dot is-other")
    );
    if (baselineVal != null) {
        items.append(make("span", "Mốc Baseline (" + numberFormat.format(baselineVal) + "%)", "legend-dot is-baseline"));
    }
    legend.append(items);

    const chart = make("div", undefined, "bar-chart");
    data.stats.forEach((model, idx) => {
        const val = model[metricKey];
        const isChosen = model.name === data.selected_model_name;
        const isBase = model === baseline;
        const row = make("div", undefined, "bar-row" + (isChosen ? " is-chosen" : "") + (isBase ? " is-baseline" : ""));
        row.dataset.model = model.name;
        row.addEventListener("pointerenter", () => setLinkedModelHighlight(model.name));
        row.addEventListener("pointerleave", () => setLinkedModelHighlight(null));

        const nameEl = make("span", model.name, "bar-name");
        const lane = make("div", undefined, "bar-lane");
        if (val != null) {
            const fill = make("div", undefined, "bar-fill");
            fill.style.width = Math.min(100, Math.max(0, val)) + "%";
            fill.style.setProperty("--delay", (idx * 48) + "ms");
            lane.append(fill);
            if (metricKey === "f1" && model.cv_std != null && model.cv_std > 0) {
                const lo = Math.max(0, val - model.cv_std);
                const hi = Math.min(100, val + model.cv_std);
                const whisker = make("div", undefined, "bar-whisker");
                whisker.style.left = lo + "%";
                whisker.style.width = Math.max(0.5, hi - lo) + "%";
                whisker.style.setProperty("--whisker-delay", (260 + idx * 48) + "ms");
                lane.append(whisker);
            }
        }
        if (baselineVal != null) {
            const ref = make("div", undefined, "bar-ref-line");
            ref.style.left = Math.min(100, Math.max(0, baselineVal)) + "%";
            lane.append(ref);
        }
        const valText = val == null
            ? "—"
            : (metricKey === "f1" && model.cv_std != null
                ? numberFormat.format(val) + " ± " + numberFormat.format(model.cv_std)
                : numberFormat.format(val) + "%");
        row.append(nameEl, lane, make("span", valText, "bar-val"));
        chart.append(row);
    });

    card.append(legend, chart);
    card.hidden = false;
}

function initChartMetricSwitcher() {
    const switcher = byId("chartMetricSwitcher");
    if (!switcher) return;
    switcher.addEventListener("click", event => {
        const btn = event.target.closest?.("button[data-metric]");
        if (!btn) return;
        currentChartMetric = btn.dataset.metric;
        for (const item of switcher.querySelectorAll("button")) {
            item.setAttribute("aria-pressed", String(item === btn));
        }
        if (currentModelData) renderModelChart(currentModelData, currentChartMetric);
    });
}

function renderTreeCards(rawRules, filter = currentTreeFilter) {
    const container = byId("treeCards");
    if (!container) return;
    container.replaceChildren();
    if (!rawRules) return;
    const lines = rawRules.split(/\r?\n/).map(line => line.trim()).filter(Boolean);
    const parsed = lines.map(line => {
        const m = line.match(/^IF\s+(.+?)\s+THEN\s+Class=(\d+)\s+\(n=(\d+)\)$/);
        return m ? {conds: m[1].split(/\s+AND\s+/), cls: m[2], count: m[3], raw: line} : {raw: line, cls: null};
    });

    const total = parsed.length;
    const posCount = parsed.filter(p => p.cls === "1").length;
    const negCount = parsed.filter(p => p.cls === "0").length;
    for (const btn of byId("treeFilterGroup")?.querySelectorAll?.("button") || []) {
        const f = btn.dataset.treeFilter;
        if (f === "all") btn.textContent = "Tất cả (" + total + ")";
        else if (f === "1") btn.textContent = "Lớp 1 · Dương (" + posCount + ")";
        else if (f === "0") btn.textContent = "Lớp 0 · Âm (" + negCount + ")";
    }

    const visible = filter === "all" ? parsed : parsed.filter(p => p.cls === filter);
    visible.forEach((item, idx) => {
        const card = make("div", undefined, "tree-path");
        card.style?.setProperty?.("--delay", (Math.min(idx, 12) * 32) + "ms");
        if (!item.conds) {
            card.append(make("span", item.raw, "tree-cond"));
            container.append(card);
            return;
        }
        const condWrap = make("div", undefined, "tree-conds");
        for (const part of item.conds) {
            condWrap.append(make("span", part, "tree-cond"));
        }
        const leaf = make("div", undefined, "tree-leaf");
        const isPos = item.cls === "1";
        leaf.append(
            make("span", isPos ? "Lớp 1 · Dương" : "Lớp 0 · Âm", "leaf-pill " + (isPos ? "is-pos" : "is-neg")),
            make("span", "n = " + item.count, "leaf-count")
        );
        card.append(condWrap, leaf);
        container.append(card);
    });
}

function initTreeControls() {
    const toggle = byId("treeRawToggle");
    toggle?.addEventListener("click", () => {
        const showRaw = toggle.getAttribute("aria-pressed") !== "true";
        toggle.setAttribute("aria-pressed", String(showRaw));
        toggle.textContent = showRaw ? "Thẻ phân nhánh" : "Văn bản thô";
        byId("treeRules").hidden = !showRaw;
        byId("treeCards").hidden = showRaw;
    });

    const filterGroup = byId("treeFilterGroup");
    filterGroup?.addEventListener("click", event => {
        const btn = event.target.closest?.("button[data-tree-filter]");
        if (!btn) return;
        currentTreeFilter = btn.dataset.treeFilter;
        for (const item of filterGroup.querySelectorAll("button")) {
            item.setAttribute("aria-pressed", String(item === btn));
        }
        if (currentModelData?.tree_rules) renderTreeCards(currentModelData.tree_rules, currentTreeFilter);
    });
}

/* ===== Sortable Table (follows sortable-table & dynamic-sort guides) ===== */
function reorderRows(container, orderedNodes) {
    const move = typeof Element !== "undefined" && Object.hasOwn(Element.prototype, "moveBefore")
        ? node => container.moveBefore(node, null)
        : node => container.append(node);
    for (const node of orderedNodes) move(node);
}

function sortModelTableBy(table, th, direction, {animate = true} = {}) {
    const tbody = table.tBodies[0];
    const index = th.cellIndex;
    const type = th.dataset.type || "text";
    const factor = direction === "ascending" ? 1 : -1;
    const rows = [...tbody.rows];

    rows.sort((a, b) => {
        const cellA = a.cells[index];
        const cellB = b.cells[index];
        if (type === "number") {
            const rawA = cellA.dataset.value;
            const rawB = cellB.dataset.value;
            const numA = rawA === "" || rawA === undefined ? null : Number(rawA);
            const numB = rawB === "" || rawB === undefined ? null : Number(rawB);
            if (numA === null && numB === null) return 0;
            if (numA === null) return 1;
            if (numB === null) return -1;
            return factor * (numA - numB);
        }
        const txtA = cellA.dataset.value ?? cellA.textContent.trim();
        const txtB = cellB.dataset.value ?? cellB.textContent.trim();
        return factor * collator.compare(txtA, txtB);
    });

    const update = () => reorderRows(tbody, rows);
    if (!animate || table.hidden) {
        update();
    } else if (typeof table.startViewTransition === "function") {
        runViewTransition(table, update);
    } else {
        runViewTransition(document, update);
    }
}

function handleTableSortTrigger(table, button) {
    const th = button.closest("th");
    if (!th) return;
    const current = th.getAttribute("aria-sort");
    const direction = current === "ascending" ? "descending" : "ascending";
    for (const header of table.tHead.rows[0].cells) header.removeAttribute("aria-sort");
    th.setAttribute("aria-sort", direction);
    sortModelTableBy(table, th, direction, {animate: true});
    const status = byId("tableSortStatus");
    if (status) {
        const dirText = direction === "ascending" ? "tăng dần" : "giảm dần";
        status.textContent = "Đã sắp xếp theo " + button.textContent.trim() + ", " + dirText + ", " + table.tBodies[0].rows.length + " mô hình.";
    }
}

function initModelTableSorting() {
    const table = byId("modelTable");
    if (!table) return;
    table.addEventListener("command", event => {
        if (event.command !== "--sort" || !event.source) return;
        handleTableSortTrigger(table, event.source);
    });
    const hasInvoker = typeof HTMLButtonElement !== "undefined" && ("commandForElement" in HTMLButtonElement.prototype);
    if (!hasInvoker) {
        table.tHead?.addEventListener("click", event => {
            const btn = event.target.closest?.('button[command="--sort"]');
            if (btn) handleTableSortTrigger(table, btn);
        });
    }
}

async function loadModelStats(key, version) {
    const status = byId("modelStatus");
    const table = byId("modelTable");
    const body = table.tBodies[0];
    const chart = byId("modelChart");
    const brief = byId("activeModelBrief");
    const badge = byId("modelCountBadge");

    body.replaceChildren();
    table.hidden = true;
    if (chart) chart.hidden = true;
    byId("treeSection").hidden = true;
    byId("treeSection").open = false;
    status.textContent = "Đang tải mô hình…";
    if (brief) brief.textContent = "Đang tải…";
    byId("waitNodeModel").textContent = "Đang tải…";

    try {
        const data = await fetchJson("/api/model_stats/" + key);
        if (version !== selection) return;
        currentModelData = data;
        currentTreeFilter = "all";
        for (const btn of byId("treeFilterGroup")?.querySelectorAll?.("button") || []) {
            btn.setAttribute("aria-pressed", String(btn.dataset.treeFilter === "all"));
        }

        const chosen = data.stats.find(m => m.name === data.selected_model_name);
        status.textContent = "Mô hình đã chọn theo F1 CV · " + data.selected_model_name +
            (chosen?.f1 != null ? (" (" + numberFormat.format(chosen.f1) + " ± " + numberFormat.format(chosen.cv_std) + "%)") : "");
        if (brief) {
            brief.textContent = data.selected_model_name + (chosen?.f1 != null ? (" · F1 " + numberFormat.format(chosen.f1) + "%") : "");
        }
        byId("waitNodeModel").textContent = SHORT_MODEL_NAMES[data.selected_model_name] || data.selected_model_name;
        if (badge) {
            badge.textContent = String(data.stats.length);
            badge.hidden = false;
        }

        renderModelChart(data, currentChartMetric);

        for (const model of data.stats) {
            const row = make("tr");
            row.dataset.model = model.name;
            row.addEventListener("pointerenter", () => setLinkedModelHighlight(model.name));
            row.addEventListener("pointerleave", () => setLinkedModelHighlight(null));
            const isChosen = model.name === data.selected_model_name;
            if (isChosen) row.className = "chosen";

            const nameTd = make("td");
            nameTd.dataset.value = model.name;
            nameTd.append(model.name);
            if (isChosen) nameTd.append(make("span", "Đang dùng", "model-badge"));
            row.append(nameTd);

            const f1Td = make("td");
            f1Td.dataset.value = model.f1 == null ? "" : String(model.f1);
            const f1 = make("div", undefined, "f1-cell");
            if (model.f1 != null) {
                const meter = make("meter");
                meter.max = 100;
                meter.value = model.f1;
                meter.setAttribute("aria-hidden", "true");
                f1.append(meter, numberFormat.format(model.f1) + " ± " + numberFormat.format(model.cv_std));
            } else {
                f1.textContent = "—";
            }
            f1Td.append(f1);
            row.append(f1Td);

            for (const metric of ["accuracy", "precision", "recall", "roc_auc"]) {
                const td = make("td", model[metric] == null ? "—" : numberFormat.format(model[metric]));
                td.dataset.value = model[metric] == null ? "" : String(model[metric]);
                row.append(td);
            }
            body.append(row);
        }

        const sortedHeader = table.tHead.querySelector("th[aria-sort]");
        if (sortedHeader) sortModelTableBy(table, sortedHeader, sortedHeader.getAttribute("aria-sort"), {animate: false});

        table.hidden = false;
        byId("treeRules").textContent = data.tree_rules;
        renderTreeCards(data.tree_rules, "all");
        byId("treeSection").hidden = !data.tree_rules;
    } catch (error) {
        if (version === selection) {
            currentModelData = null;
            status.textContent = error.fields?.model || "Chưa tải được thông tin mô hình.";
            if (brief) brief.textContent = "Chưa có artifact mô hình";
            byId("waitNodeModel").textContent = "Chưa có mô hình";
        }
    }
}

/* ===== Interactive History (parse SQLite features + one-click reload) ===== */
function parseStoredFeatures(raw) {
    if (!raw || typeof raw !== "string") return null;
    const text = raw.trim();
    if (!text.startsWith("{") || !text.endsWith("}")) return null;
    const result = {};
    const pairRe = /['"]([a-zA-Z0-9_]+)['"]\s*:\s*(None|-?\d+(?:\.\d+)?)/g;
    let found = false;
    let match;
    while ((match = pairRe.exec(text)) !== null) {
        found = true;
        result[match[1]] = match[2] === "None" ? null : Number(match[2]);
    }
    return found ? result : null;
}

function formatLocalTimestamp(utcStr) {
    if (!utcStr) return {local: "—", utc: ""};
    const iso = utcStr.includes("T") ? utcStr : utcStr.replace(" ", "T") + "Z";
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return {local: utcStr, utc: ""};
    return {
        local: new Intl.DateTimeFormat("vi-VN", {
            hour: "2-digit", minute: "2-digit", second: "2-digit",
            day: "2-digit", month: "2-digit", year: "numeric",
        }).format(date),
        utc: utcStr + " UTC",
    };
}

async function loadHistory() {
    const requestId = ++historyRequest;
    const body = byId("historyBody");
    const badge = byId("historyCountBadge");
    if (!body) return;

    function showMessage(text) {
        const row = make("tr");
        const cell = make("td", text);
        cell.colSpan = 6;
        row.append(cell);
        body.replaceChildren(row);
    }

    try {
        const rows = await fetchJson("/api/history");
        if (requestId !== historyRequest) return;
        body.replaceChildren();
        if (badge) {
            badge.textContent = String(rows.length);
            badge.hidden = rows.length === 0;
        }
        if (!rows.length) showMessage("Chưa có lượt suy luận nào được lưu.");

        for (const [id, diseaseKey, featuresRaw, score, , , time] of rows) {
            const row = make("tr");
            const parsed = parseStoredFeatures(featuresRaw);

            const featCell = make("td");
            const chips = make("div", undefined, "history-chips");
            if (parsed) {
                for (const [k, v] of Object.entries(parsed)) {
                    chips.append(make("span", k + ": " + (v === null ? "—" : numberFormat.format(v)), "history-chip" + (v === null ? " is-null" : "")));
                }
            } else {
                chips.append(make("span", "—", "history-chip"));
            }
            featCell.append(chips);

            const scoreCell = make("td");
            const scoreWrap = make("span", undefined, "history-score");
            const dotCls = score == null ? "" : (score >= 0.7 ? " is-high" : (score >= 0.5 ? " is-med" : ""));
            scoreWrap.append(make("span", undefined, "history-dot" + dotCls), score == null ? "—" : scoreFormat.format(score));
            scoreCell.append(scoreWrap);

            const timeCell = make("td");
            const formatted = formatLocalTimestamp(time);
            const timeWrap = make("div", undefined, "history-time");
            timeWrap.append(make("span", formatted.local));
            if (formatted.utc) timeWrap.append(make("small", formatted.utc));
            timeCell.append(timeWrap);

            const actionCell = make("td");
            if (parsed && diseases[diseaseKey]) {
                const reloadBtn = make("button", "Nạp lại", "reload-btn");
                reloadBtn.type = "button";
                reloadBtn.addEventListener("click", () => {
                    if (diseaseKey !== currentDisease) selectDisease(diseaseKey, {transition: false});
                    if (!showAllViews && currentView !== "workspace") switchView("workspace");
                    fillFormInputs(parsed);
                    updatePresetHighlight(null);
                    showToast("Đã nạp lại lượt #" + id + " (" + diseases[diseaseKey].name + ").");
                    if (liveAutoRun) {
                        scheduleLiveDiagnosis();
                    } else {
                        byId("diagnosisForm")?.querySelector?.('input[type="number"]')?.focus();
                    }
                });
                actionCell.append(reloadBtn);
            } else {
                actionCell.textContent = "—";
            }

            row.append(
                make("td", "#" + id),
                make("td", diseases[diseaseKey]?.name || diseaseKey),
                featCell,
                scoreCell,
                timeCell,
                actionCell
            );
            body.append(row);
        }
    } catch {
        if (requestId === historyRequest) showMessage("Chưa đọc được lịch sử.");
    }
}

document.addEventListener("DOMContentLoaded", start);
