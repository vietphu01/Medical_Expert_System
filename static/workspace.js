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
    {id: "c1", num: "01", title: "Hợp lệ", disease: "heart", inputs: {age: 60, bp: 135, chol: 230}},
    {id: "c2", num: "02", title: "Thiếu chol", disease: "heart", inputs: {age: 60, bp: 135, chol: null}},
    {id: "c3", num: "03", title: "Biên fuzzy 50%", disease: "heart", inputs: {age: 60, bp: 135, chol: 200}},
    {id: "c4", num: "04", title: "2 luật đích", disease: "diabetes", inputs: {glucose: 175, bmi: 33, age: 45}},
    {id: "c5", num: "05", title: "ML ≠ Luật", disease: "diabetes", inputs: {glucose: 90, bmi: 26, age: 45}},
    {id: "c6", num: "06", title: "Ngoài miền", disease: "heart", inputs: {age: 60, bp: 135, chol: 900}},
];

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
let historyRequest = 0;
let currentModelData = null;
let currentChartMetric = "f1";
let activePresetId = null;
const lastScoresByDisease = {};
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

/* ===== Glossary Popover with Top-Layer Exit Fallback ===== */
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

function initGlossaryPopover() {
    const popover = byId("glossaryPopover");
    const trigger = byId("glossaryTrigger");
    const closeBtn = byId("glossaryClose");
    if (!popover || !trigger) return;
    const hasNativePopover = typeof HTMLElement !== "undefined" && Object.hasOwn(HTMLElement.prototype, "popover");

    if (!hasNativePopover) {
        popover.removeAttribute("popover");
        trigger.addEventListener("click", () => {
            if (popover.classList.contains("is-open")) {
                closeTopLayer(popover, false);
            } else {
                popover.classList.add("is-open");
                closeBtn?.focus();
            }
        });
        document.addEventListener("keydown", event => {
            if (event.key === "Escape" && popover.classList.contains("is-open")) {
                closeTopLayer(popover, false);
                trigger.focus();
            }
        });
    }

    closeBtn?.addEventListener("click", () => {
        closeTopLayer(popover, hasNativePopover);
        trigger.focus();
    });
}

/* ===== View Navigation with Same-Document Transitions ===== */
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
    const reduced = typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (!reduced && host && typeof host.startViewTransition === "function") {
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

/* ===== Fuzzy Preview Helper (mirrors research_rules.py) ===== */
function evalFactMembership(value, spec) {
    if (value === null || !Number.isFinite(value)) return null;
    if (spec.kind === "at_least") return value >= spec.bounds ? 1 : 0;
    if (spec.kind === "between") return (value >= spec.bounds[0] && value <= spec.bounds[1]) ? 1 : 0;
    if (spec.kind === "ramp") {
        const [low, high] = spec.bounds;
        if (value <= low) return 0;
        if (value >= high) return 1;
        return (value - low) / (high - low);
    }
    return null;
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

function updateFieldPreview(container, field, value, isMissing, dataset) {
    container.replaceChildren();
    if (isMissing) {
        container.append(make("span", "Chưa biết → ML điền trung vị train · Luật bỏ qua", "preview-chip is-missing"));
        return;
    }
    const specs = (DATASET_FACT_SPECS[dataset] || {})[field.key] || [];
    if (!specs.length) return;
    for (const spec of specs) {
        const m = evalFactMembership(value, spec);
        if (m === null) continue;
        const isBoundary = Math.abs(m - 0.5) < 1e-9;
        const isTrue = m > 0.5;
        let text = spec.label + " · μ " + scoreFormat.format(m) + " → " + (isTrue ? "Đúng" : "Sai");
        let cls = "preview-chip" + (isTrue ? " is-true" : "");
        if (isBoundary) {
            text = spec.label + " · đúng biên 50% (cần >50% → Sai)";
            cls = "preview-chip is-boundary";
        }
        container.append(make("span", text, cls));
    }
}

function buildFuzzyZoneStrip(field, dataset) {
    const specs = (DATASET_FACT_SPECS[dataset] || {})[field.key] || [];
    if (!specs.length) return null;
    const strip = make("div", undefined, "fuzzy-zones");
    strip.setAttribute?.("aria-hidden", "true");
    const span = field.max - field.min;
    const pct = v => Math.min(100, Math.max(0, ((v - field.min) / span) * 100));

    const ramps = [];
    const ticks = [];
    for (const spec of specs) {
        if (spec.kind === "ramp") {
            const [low, high] = spec.bounds;
            const mid = (low + high) / 2;
            const activeBand = make("div", undefined, "fuzzy-zone-band is-active");
            activeBand.style.left = pct(high) + "%";
            activeBand.style.width = Math.max(0, 100 - pct(high)) + "%";
            strip.append(activeBand);
            const rampBand = make("div", undefined, "fuzzy-zone-band is-ramp");
            rampBand.style.left = pct(low) + "%";
            rampBand.style.width = Math.max(0, pct(high) - pct(low)) + "%";
            ramps.push(rampBand);
            const tick = make("div", undefined, "fuzzy-cutoff-tick");
            tick.style.left = pct(mid) + "%";
            ticks.push(tick);
        } else if (spec.kind === "at_least") {
            const activeBand = make("div", undefined, "fuzzy-zone-band is-active");
            activeBand.style.left = pct(spec.bounds) + "%";
            activeBand.style.width = Math.max(0, 100 - pct(spec.bounds)) + "%";
            strip.append(activeBand);
            const tick = make("div", undefined, "fuzzy-cutoff-tick");
            tick.style.left = pct(spec.bounds) + "%";
            ticks.push(tick);
        } else if (spec.kind === "between") {
            const [low, high] = spec.bounds;
            const activeBand = make("div", undefined, "fuzzy-zone-band is-active");
            activeBand.style.left = pct(low) + "%";
            activeBand.style.width = Math.max(0, pct(high) - pct(low)) + "%";
            strip.append(activeBand);
        }
    }
    strip.append(...ramps, ...ticks);
    return strip;
}

/* ===== Demo Presets Bar ===== */
function renderPresets() {
    const list = byId("presetList");
    if (!list) return;
    list.replaceChildren();
    for (const preset of DEMO_PRESETS) {
        const btn = make("button", undefined, "preset-chip");
        btn.type = "button";
        btn.dataset.presetId = preset.id;
        btn.setAttribute("aria-pressed", String(activePresetId === preset.id));
        btn.append(make("span", preset.num, "chip-num"), make("span", preset.title));
        btn.addEventListener("click", () => applyPreset(preset));
        list.append(btn);
    }
}

function updatePresetHighlight(id) {
    activePresetId = id;
    for (const btn of byId("presetList")?.children || []) {
        btn.setAttribute?.("aria-pressed", String(btn.dataset.presetId === id));
    }
}

function applyPreset(preset) {
    if (!diseases[preset.disease]) return;
    if (preset.disease !== currentDisease) {
        selectDisease(preset.disease, {transition: false});
    }
    if (!showAllViews && currentView !== "workspace") {
        switchView("workspace");
    }
    fillFormInputs(preset.inputs);
    updatePresetHighlight(preset.id);
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
        const preview = card?.querySelector?.(".field-preview");
        if (!numInput) continue;

        if (val === null || val === undefined || val === "") {
            numInput.value = "";
            card?.classList?.add("is-missing");
            toggle?.setAttribute?.("aria-pressed", "true");
            if (slider) slider.disabled = true;
            if (preview) updateFieldPreview(preview, field, null, true, disease.dataset);
        } else {
            numInput.value = String(val);
            card?.classList?.remove("is-missing");
            toggle?.setAttribute?.("aria-pressed", "false");
            if (slider) {
                slider.disabled = false;
                syncSliderVars(slider, Number(val));
                slider.setAttribute("aria-valuetext", numberFormat.format(Number(val)));
            }
            if (preview) updateFieldPreview(preview, field, Number(val), false, disease.dataset);
        }
    }
}

/* ===== Disease Selection & Form Rendering ===== */
function selectDisease(key, {transition = true} = {}) {
    const perform = () => {
        currentDisease = key;
        selection++;
        activePresetId = null;
        updatePresetHighlight(null);
        const disease = diseases[key];
        for (const tab of byId("diseaseTabs").children) {
            tab.setAttribute("aria-pressed", String(tab.dataset.disease === key));
        }
        byId("groupName").textContent = disease.name;
        const dataset = disease.dataset.toUpperCase();
        byId("outputDataset").textContent = dataset + (disease.has_target_rules ? " · ML + Hệ luật" : " · Chỉ ML");
        byId("modelDataset").textContent = dataset + " · Kiểm chứng chéo 5-fold";
        byId("emptyState").querySelector(".flow")?.classList.toggle("ml-only", !disease.has_target_rules);
        renderForm(disease);
        clearResult();
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
    initGlossaryPopover();
    initNavigation();
    initModelTableSorting();
    initChartMetricSwitcher();
    initTreeRawToggle();
    byId("refreshHistoryBtn")?.addEventListener("click", loadHistory);
    byId("resetDefaultsBtn")?.addEventListener("click", () => {
        const disease = diseases[currentDisease];
        if (!disease) return;
        const defaults = Object.fromEntries(disease.fields.map(f => [f.key, f.default]));
        fillFormInputs(defaults);
        updatePresetHighlight(null);
        markResultStale();
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

function clearResult() {
    byId("loading").hidden = true;
    byId("resultSection").hidden = true;
    byId("resultSection").classList?.remove("is-stale");
    const stale = byId("staleNotice");
    if (stale) stale.hidden = true;
    byId("emptyState").hidden = false;
}

function markResultStale() {
    const section = byId("resultSection");
    if (section && !section.hidden) {
        section.classList?.add("is-stale");
        const stale = byId("staleNotice");
        if (stale) stale.hidden = false;
    }
}

function renderForm(disease) {
    const form = byId("diagnosisForm");
    form.inert = false;
    form.replaceChildren(
        make("p", "Kéo thanh trượt hoặc nhập số trực tiếp. Gạt \"Chưa biết\" để gửi null (ML dùng trung vị train, luật giữ chưa biết).", "hint")
    );

    for (const field of disease.fields) {
        const group = make("div", undefined, "field");
        const top = make("div", undefined, "field-top");
        const label = make("label", field.label);
        const input = make("input");
        input.type = "number";
        input.id = "field_" + field.key;
        input.name = "inputs." + field.key;
        input.value = String(field.default);
        input.min = String(field.min);
        input.max = String(field.max);
        input.step = String(field.step || 1);
        input.inputMode = field.step && field.step < 1 ? "decimal" : "numeric";
        label.htmlFor = input.id;

        const missingBtn = make("button", "Chưa biết", "missing-toggle");
        missingBtn.type = "button";
        missingBtn.setAttribute("aria-pressed", "false");
        missingBtn.setAttribute("aria-label", "Đánh dấu " + field.label + " là chưa biết");
        top.append(label, missingBtn);

        const range = make("small", numberFormat.format(field.min) + " – " + numberFormat.format(field.max));
        range.id = input.id + "_range";
        input.setAttribute("aria-describedby", range.id);
        const entry = make("div", undefined, "entry");
        entry.append(input, range);

        const sliderWrap = make("div", undefined, "slider-wrap");
        const zones = buildFuzzyZoneStrip(field, disease.dataset);
        if (zones) sliderWrap.append(zones);

        const slider = make("input", undefined, "metric-slider");
        slider.type = "range";
        slider.min = String(field.min);
        slider.max = String(field.max);
        slider.step = String(field.step || 1);
        slider.setAttribute("aria-label", "Thanh trượt " + field.label);
        syncSliderVars(slider, Number(field.default));
        slider.setAttribute("aria-valuetext", numberFormat.format(Number(field.default)));
        sliderWrap.append(slider);

        const preview = make("div", undefined, "field-preview");
        updateFieldPreview(preview, field, Number(field.default), false, disease.dataset);

        let savedBeforeMissing = String(field.default);

        slider.addEventListener("input", () => {
            const val = Number(slider.value);
            input.value = slider.value;
            savedBeforeMissing = slider.value;
            syncSliderVars(slider, val);
            slider.setAttribute("aria-valuetext", numberFormat.format(val));
            group.classList.remove("is-missing");
            missingBtn.setAttribute("aria-pressed", "false");
            updateFieldPreview(preview, field, val, false, disease.dataset);
            clearErrors(form);
            updatePresetHighlight(null);
            markResultStale();
        });

        input.addEventListener("input", () => {
            clearErrors(form);
            updatePresetHighlight(null);
            markResultStale();
            if (input.value === "") {
                group.classList.add("is-missing");
                missingBtn.setAttribute("aria-pressed", "true");
                slider.disabled = true;
                updateFieldPreview(preview, field, null, true, disease.dataset);
            } else {
                const num = Number(input.value);
                savedBeforeMissing = input.value;
                group.classList.remove("is-missing");
                missingBtn.setAttribute("aria-pressed", "false");
                slider.disabled = false;
                if (Number.isFinite(num)) {
                    syncSliderVars(slider, num);
                    slider.setAttribute("aria-valuetext", numberFormat.format(num));
                }
                updateFieldPreview(preview, field, num, false, disease.dataset);
            }
        });

        missingBtn.addEventListener("click", () => {
            const makeMissing = missingBtn.getAttribute("aria-pressed") !== "true";
            clearErrors(form);
            updatePresetHighlight(null);
            markResultStale();
            if (makeMissing) {
                if (input.value !== "") savedBeforeMissing = input.value;
                input.value = "";
                slider.disabled = true;
                group.classList.add("is-missing");
                missingBtn.setAttribute("aria-pressed", "true");
                updateFieldPreview(preview, field, null, true, disease.dataset);
            } else {
                const restored = savedBeforeMissing || String(field.default);
                input.value = restored;
                slider.disabled = false;
                group.classList.remove("is-missing");
                missingBtn.setAttribute("aria-pressed", "false");
                syncSliderVars(slider, Number(restored));
                slider.setAttribute("aria-valuetext", numberFormat.format(Number(restored)));
                updateFieldPreview(preview, field, Number(restored), false, disease.dataset);
                input.focus();
            }
        });

        group.append(top, entry, sliderWrap, preview);
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
}

function clearErrors(form) {
    const errList = byId("diagnosisErrors");
    if (errList) {
        errList.replaceChildren();
        errList.hidden = true;
    }
    for (const input of form.querySelectorAll(".is-invalid")) {
        input.classList.remove("is-invalid");
        input.removeAttribute("aria-invalid");
        input.setAttribute("aria-describedby", input.id + "_range");
    }
}

function showErrors(form, errors) {
    const list = byId("diagnosisErrors");
    list.replaceChildren();
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
    const inputs = {};
    const errors = {};
    for (const field of disease.fields) {
        const el = form.elements.namedItem("inputs." + field.key);
        if (el.validity.badInput) errors[el.name] = field.label + " cần một giá trị số hợp lệ.";
        inputs[field.key] = el.value === "" ? null : el.value;
    }
    if (Object.keys(errors).length) {
        clearResult();
        showErrors(form, errors);
        return;
    }

    form.inert = true;
    const submit = form.querySelector("button[type=submit]");
    submit.disabled = true;
    byId("emptyState").hidden = true;
    byId("resultSection").classList?.add("is-stale");
    byId("loading").hidden = false;

    try {
        const data = await fetchJson("/api/diagnose", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({disease: currentDisease, inputs}),
        });
        loadHistory();
        if (version !== selection) return;
        const prev = lastScoresByDisease[currentDisease];
        renderTrace(data.trace, disease, prev);
        lastScoresByDisease[currentDisease] = data.trace.result.combined_score;
        byId("resultSection").hidden = false;
        byId("resultSection").classList?.remove("is-stale");
        const stale = byId("staleNotice");
        if (stale) stale.hidden = true;
        byId("outputTitle").focus({preventScroll: true});
        if (typeof window !== "undefined" && window.matchMedia?.("(max-width: 980px)").matches) {
            byId("outputTitle").scrollIntoView({block: "start"});
        }
    } catch (error) {
        if (version !== selection) return;
        form.inert = false;
        clearResult();
        showErrors(form, error.fields || {body: "Chưa nhận được kết quả. Vui lòng thử lại."});
    } finally {
        if (version === selection) {
            form.inert = false;
            submit.disabled = false;
            byId("loading").hidden = true;
        }
    }
}

/* ===== SVG Gauge & Live Fusion Pipeline ===== */
function buildSupportGauge(combined, mlScore, ruleScore) {
    const svg = makeSvg("svg", {viewBox: "0 0 180 112", class: "gauge-svg", "aria-hidden": "true"});
    if (!svg) return null;
    const cx = 90, cy = 94, r = 68;
    const pt = frac => {
        const ang = Math.PI * (1 - Math.min(1, Math.max(0, frac)));
        return [cx + r * Math.cos(ang), cy - r * Math.sin(ang)];
    };
    const arcLen = Math.PI * r;
    const bgPath = makeSvg("path", {
        d: `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`,
        fill: "none", stroke: "var(--surface-3)", "stroke-width": 13, "stroke-linecap": "round",
    });
    const fgPath = makeSvg("path", {
        d: `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`,
        fill: "none", stroke: "var(--tone-accent)", "stroke-width": 13, "stroke-linecap": "round",
        "stroke-dasharray": `${(arcLen * Math.min(1, Math.max(0, combined))).toFixed(1)} ${arcLen.toFixed(1)}`,
    });
    // 50% threshold tick at top center
    const tick = makeSvg("line", {
        x1: cx, y1: cy - r - 11, x2: cx, y2: cy - r + 11,
        stroke: "var(--ink)", "stroke-width": 2, "stroke-dasharray": "3 2", opacity: 0.72,
    });
    const tickLabel = makeSvg("text", {
        x: cx, y: 11, "text-anchor": "middle", fill: "var(--muted)", "font-size": 10, "font-family": "var(--font-mono)",
    });
    tickLabel.textContent = "50%";
    const leftLabel = makeSvg("text", {x: 16, y: 109, fill: "var(--muted)", "font-size": 9.5, "font-family": "var(--font-mono)"});
    leftLabel.textContent = "0%";
    const rightLabel = makeSvg("text", {x: 164, y: 109, "text-anchor": "end", fill: "var(--muted)", "font-size": 9.5, "font-family": "var(--font-mono)"});
    rightLabel.textContent = "100%";

    svg.append(bgPath, fgPath, tick, tickLabel, leftLabel, rightLabel);

    // Marker dots for ML and Rule
    const [mx, my] = pt(mlScore);
    svg.append(makeSvg("circle", {cx: mx.toFixed(1), cy: my.toFixed(1), r: 4.5, fill: "var(--brand)", stroke: "var(--surface)", "stroke-width": 2}));
    if (ruleScore !== null) {
        const [rx, ry] = pt(ruleScore);
        svg.append(makeSvg("circle", {cx: rx.toFixed(1), cy: ry.toFixed(1), r: 4.5, fill: "var(--conflict-accent)", stroke: "var(--surface)", "stroke-width": 2}));
    }
    return svg;
}

function buildCompareStrip(mlScore, ruleScore, combinedScore) {
    const strip = make("div", undefined, "compare-strip");
    const items = [
        {label: "ML", val: mlScore, cls: ""},
        {label: "Hệ luật", val: ruleScore, cls: " is-rule"},
        {label: "Kết hợp", val: combinedScore, cls: " is-combined"},
    ];
    for (const item of items) {
        const row = make("div", undefined, "compare-row");
        const track = make("div", undefined, "compare-track");
        const fill = make("div", undefined, "compare-fill" + item.cls + (item.val === null ? " is-empty" : ""));
        if (item.val !== null && fill.style) fill.style.width = (Math.min(1, Math.max(0, item.val)) * 100).toFixed(1) + "%";
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
    return strip;
}

function renderLivePipeline(trace, disease, missing) {
    const container = byId("livePipeline");
    if (!container) return;
    const result = trace.result;
    const targetRules = trace.fired_rules.filter(r => r.used_in_fusion);

    const nodes = make("div", undefined, "pipeline-nodes");
    const mlNode = make("div", undefined, "pipe-node");
    mlNode.append(
        make("small", "Nhánh ML" + (missing.length ? " (điền trung vị)" : "")),
        make("strong", "p = " + mathFormat.format(trace.ml.score))
    );

    const ruleNode = make("div", undefined, "pipe-node" + (result.rule_score === null ? " is-inactive" : ""));
    ruleNode.append(
        make("small", result.rule_score === null
            ? (disease.has_target_rules ? "Luật đích (0 khớp)" : "Chưa có luật đích")
            : ("Luật đích (" + targetRules.length + " luật khớp)")),
        make("strong", result.rule_score === null ? "C_rule = —" : ("C_rule = " + mathFormat.format(result.rule_score)))
    );

    const finalNode = make("div", undefined, "pipe-node is-final");
    finalNode.append(
        make("small", "Gộp mới → Nhãn " + result.predicted_label),
        make("strong", "C_new = " + mathFormat.format(result.combined_score))
    );

    nodes.append(mlNode, make("span", "+", "pipe-op"), ruleNode, make("span", "→", "pipe-op"), finalNode);

    const formula = make("div", undefined, "formula-box");
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

    container.replaceChildren(make("p", "Sơ đồ phép gộp trực tiếp", "pipeline-title"), nodes, formula);
    container.hidden = false;
}

/* ===== Main Trace Renderer (preserves exact tests/test_trace_ui.py contract) ===== */
function renderTrace(trace, disease, previousScore) {
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
        const matched = trace.facts.find(fact => fact.feature === field.key);
        const value = matched?.value;
        const unit = matched?.unit;
        if (value == null) missing.push(field.key);
        const item = make("li", undefined, "trace-input-chip" + (value == null ? " is-missing" : ""));
        const showUnit = unit && unit !== "years" && !field.label.includes(unit);
        item.append(
            make("span", field.label + " · "),
            make("strong", value == null ? "Chưa biết" : (numberFormat.format(value) + (showUnit ? " " + unit : "")))
        );
        inputs.append(item);
    }

    for (const fact of trace.facts.filter(f => f.key !== null)) {
        const row = make("li", undefined, "fact-card");
        const head = make("div", undefined, "fact-head");
        const stateText = fact.value_boolean === null ? "Chưa biết" : (fact.value_boolean ? "Đúng" : "Sai");
        const stateCls = fact.value_boolean === null ? "is-unknown" : (fact.value_boolean ? "is-true" : "is-false");
        head.append(
            make("b", factLabels[fact.key] || fact.key),
            make("span", stateText, "fact-status " + stateCls)
        );
        row.append(head);

        if (fact.membership !== null) {
            const meterRow = make("div", undefined, "fact-meter-row");
            const meter = make("div", undefined, "fact-meter");
            const isBoundary = Math.abs(fact.membership - 0.5) < 1e-9;
            const fill = make("div", undefined, "fact-meter-fill" + (fact.value_boolean ? " is-true" : (isBoundary ? " is-boundary" : "")));
            if (fill.style) fill.style.width = (Math.min(1, Math.max(0, fact.membership)) * 100).toFixed(1) + "%";
            meter.append(fill);
            const labelVal = "μ = " + scoreFormat.format(fact.membership) + (isBoundary ? " (đúng biên 50%)" : "");
            meterRow.append(meter, make("span", labelVal, "fact-meter-val"));
            row.append(meterRow);
        }
        facts.append(row);
    }
    if (!facts.children.length) {
        facts.append(make("li", "Bộ dữ liệu này chưa có dữ kiện dẫn xuất cho hệ luật.", "trace-empty"));
    }

    for (const rule of trace.fired_rules) {
        const row = make("li", undefined, "rule-card" + (rule.used_in_fusion ? "" : " is-secondary"));
        const top = make("div", undefined, "rule-top");
        const left = make("div", undefined, "rule-top-left");
        left.append(
            make("code", rule.id),
            make("span", rule.used_in_fusion ? "Dùng để gộp" : "Luật phụ", "rule-role")
        );
        top.append(left, make("span", "CF " + scoreFormat.format(rule.cf), "rule-cf"));

        const conds = make("div", undefined, "rule-conds");
        conds.append(make("span", "NẾU:"));
        rule.conditions.forEach((cond, idx) => {
            if (idx > 0) conds.append(make("span", "và"));
            conds.append(make("span", factLabels[cond] || cond, "cond-pill"));
        });

        row.append(top, make("p", rule.conclusion, "rule-conclusion"), conds);
        rules.append(row);
    }
    if (!rules.children.length) {
        rules.append(make("li", disease.has_target_rules ? "Chưa có luật nào khớp." : "Bộ dữ liệu này chưa có luật đích.", "trace-empty"));
    }

    // Semantic tone + disagreement detection
    const tone = result.predicted_label === 0
        ? "negative"
        : (result.combined_score >= 0.7 ? "high" : "moderate");
    summary.setAttribute?.("data-tone", tone);

    const topRow = make("div", undefined, "score-top");
    topRow.append(make("p", "Điểm hỗ trợ kết hợp", "score-label"));
    const badges = make("div", undefined, "score-badges");
    const verdictText = "Nhãn " + result.predicted_label + " · Lớp " + (result.predicted_label ? "dương" : "âm") + " của " + trace.target.toUpperCase();
    badges.append(make("span", verdictText, "verdict-badge"));
    if (typeof previousScore === "number" && Number.isFinite(previousScore)) {
        const diffPts = (result.combined_score - previousScore) * 100;
        const deltaText = Math.abs(diffPts) < 0.05
            ? "= Không đổi"
            : ((diffPts > 0 ? "▲ +" : "▼ ") + numberFormat.format(diffPts) + " điểm %");
        badges.append(make("span", deltaText, "delta-badge"));
    }
    topRow.append(badges);

    const hero = make("div", undefined, "score-hero");
    const heroText = make("div");
    heroText.append(
        make("strong", scoreFormat.format(result.combined_score), "score-value"),
        make("p", result.predicted_label ? "Vượt ngưỡng quyết định 50%" : "Dưới ngưỡng quyết định 50%", "score-sub")
    );
    hero.append(heroText);
    const gauge = buildSupportGauge(result.combined_score, trace.ml.score, result.rule_score);
    if (gauge) {
        const gaugeBox = make("div", undefined, "gauge-box");
        gaugeBox.append(gauge);
        hero.append(gaugeBox);
    }

    const compareStrip = buildCompareStrip(trace.ml.score, result.rule_score, result.combined_score);

    // Preserve exact .score-grid structure expected by tests/test_trace_ui.py
    const grid = make("div", undefined, "score-grid");
    const model = make("div");
    model.append(make("small", "ML · " + trace.ml.model), make("b", scoreFormat.format(trace.ml.score)));
    const rule = make("div");
    rule.append(make("small", "Hệ luật"), make("b", result.rule_score === null ? "Chưa có điểm" : scoreFormat.format(result.rule_score)));
    grid.append(model, rule);

    summary.replaceChildren(topRow, hero, compareStrip, grid);

    // Highlight ML vs Rules disagreement when both sides sit across 0.5
    if (result.rule_score !== null) {
        const mlPos = trace.ml.score >= 0.5;
        const rulePos = result.rule_score >= 0.5;
        if (mlPos !== rulePos) {
            const banner = make("p", undefined, "conflict-banner");
            const icon = make("span", "⇄", "conflict-icon");
            icon.setAttribute?.("aria-hidden", "true");
            const body = make("span");
            const strong = make("strong", "ML và Hệ luật bất đồng: ");
            const detail = mlPos
                ? ("ML vượt ngưỡng (" + scoreFormat.format(trace.ml.score) + ") trong khi điểm luật ở dưới 50% (" + scoreFormat.format(result.rule_score) + ").")
                : ("ML ở dưới ngưỡng (" + scoreFormat.format(trace.ml.score) + ") nhưng luật đích đạt " + scoreFormat.format(result.rule_score) + ", kéo điểm kết hợp lên " + scoreFormat.format(result.combined_score) + ".");
            body.append(strong, detail);
            banner.append(icon, body);
            summary.append(banner);
        }
    }

    if (result.rule_score === null) {
        const reason = disease.has_target_rules ? "Không có luật đích nào khớp." : "Bộ dữ liệu này chưa có luật đích.";
        summary.append(make("p", reason + " Điểm kết hợp bằng điểm ML.", "score-note"));
    }
    if (missing.length) {
        summary.append(make("p", "Đã nhập " + (disease.fields.length - missing.length) + "/" + disease.fields.length +
            " chỉ số. ML dùng trung vị học từ train cho " + missing.join(", ") + ". Hệ luật giữ dữ kiện thiếu ở trạng thái chưa biết.", "score-note"));
    }

    renderLivePipeline(trace, disease, missing);
}

/* ===== CV Benchmark Chart, Sortable Table & Decision Tree Cards ===== */
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
    for (const model of data.stats) {
        const val = model[metricKey];
        const isChosen = model.name === data.selected_model_name;
        const isBase = model === baseline;
        const row = make("div", undefined, "bar-row" + (isChosen ? " is-chosen" : "") + (isBase ? " is-baseline" : ""));
        const nameEl = make("span", model.name, "bar-name");
        const lane = make("div", undefined, "bar-lane");
        if (val != null) {
            const fill = make("div", undefined, "bar-fill");
            fill.style.width = Math.min(100, Math.max(0, val)) + "%";
            lane.append(fill);
            if (metricKey === "f1" && model.cv_std != null && model.cv_std > 0) {
                const lo = Math.max(0, val - model.cv_std);
                const hi = Math.min(100, val + model.cv_std);
                const whisker = make("div", undefined, "bar-whisker");
                whisker.style.left = lo + "%";
                whisker.style.width = Math.max(0.5, hi - lo) + "%";
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
    }

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

function renderTreeCards(rawRules) {
    const container = byId("treeCards");
    if (!container) return;
    container.replaceChildren();
    if (!rawRules) return;
    const lines = rawRules.split(/\r?\n/).map(line => line.trim()).filter(Boolean);
    for (const line of lines) {
        const match = line.match(/^IF\s+(.+?)\s+THEN\s+Class=(\d+)\s+\(n=(\d+)\)$/);
        const card = make("div", undefined, "tree-path");
        if (!match) {
            card.append(make("span", line, "tree-cond"));
            container.append(card);
            continue;
        }
        const [, condText, cls, count] = match;
        const condWrap = make("div", undefined, "tree-conds");
        for (const part of condText.split(/\s+AND\s+/)) {
            condWrap.append(make("span", part, "tree-cond"));
        }
        const leaf = make("div", undefined, "tree-leaf");
        const isPos = cls === "1";
        leaf.append(
            make("span", isPos ? "Lớp 1 · Dương" : "Lớp 0 · Âm", "leaf-pill " + (isPos ? "is-pos" : "is-neg")),
            make("span", "n = " + count, "leaf-count")
        );
        card.append(condWrap, leaf);
        container.append(card);
    }
}

function initTreeRawToggle() {
    const toggle = byId("treeRawToggle");
    if (!toggle) return;
    toggle.addEventListener("click", () => {
        const showRaw = toggle.getAttribute("aria-pressed") !== "true";
        toggle.setAttribute("aria-pressed", String(showRaw));
        toggle.textContent = showRaw ? "Xem dạng thẻ phân nhánh" : "Xem dạng văn bản thô";
        byId("treeRules").hidden = !showRaw;
        byId("treeCards").hidden = showRaw;
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
    // Fallback for browsers without Invoker Commands API
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

    try {
        const data = await fetchJson("/api/model_stats/" + key);
        if (version !== selection) return;
        currentModelData = data;
        const chosen = data.stats.find(m => m.name === data.selected_model_name);
        status.textContent = "Mô hình đã chọn theo F1 CV · " + data.selected_model_name +
            (chosen?.f1 != null ? (" (" + numberFormat.format(chosen.f1) + " ± " + numberFormat.format(chosen.cv_std) + "%)") : "");
        if (brief) {
            brief.textContent = data.selected_model_name + (chosen?.f1 != null ? (" · F1 " + numberFormat.format(chosen.f1) + "%") : "");
        }
        if (badge) {
            badge.textContent = String(data.stats.length);
            badge.hidden = false;
        }

        renderModelChart(data, currentChartMetric);

        for (const model of data.stats) {
            const row = make("tr");
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

        // Apply active column sort initially without triggering a view transition while hidden
        const sortedHeader = table.tHead.querySelector("th[aria-sort]");
        if (sortedHeader) sortModelTableBy(table, sortedHeader, sortedHeader.getAttribute("aria-sort"), {animate: false});

        table.hidden = false;
        byId("treeRules").textContent = data.tree_rules;
        renderTreeCards(data.tree_rules);
        byId("treeSection").hidden = !data.tree_rules;
    } catch (error) {
        if (version === selection) {
            currentModelData = null;
            status.textContent = error.fields?.model || "Chưa tải được thông tin mô hình.";
            if (brief) brief.textContent = "Chưa có artifact mô hình";
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
                    byId("diagnosisForm")?.querySelector?.('input[type="number"]')?.focus();
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
