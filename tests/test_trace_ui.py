"""Exercise the same trace renderer that Flask serves, with invented facts."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from medical_expert.expert.rules import evaluate_rules


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('node'), 'node is not installed')
class TraceUiTests(unittest.TestCase):
    def test_waiting_rule_preview_agrees_with_backend_for_fixture_inputs(self):
        cases = [
            {'dataset': 'cleveland', 'inputs': {'age': 60, 'bp': 135, 'chol': 180}},
            {'dataset': 'cleveland', 'inputs': {'age': 60, 'bp': 135, 'chol': 200}},
            {'dataset': 'cleveland', 'inputs': {'age': 60, 'bp': 135, 'chol': None}},
            {'dataset': 'cleveland', 'inputs': {'age': 50, 'bp': 135, 'chol': None}},
            {'dataset': 'pima', 'inputs': {'age': 45, 'glucose': 90, 'bmi': 25}},
            {'dataset': 'pima', 'inputs': {'age': 45, 'glucose': 90, 'bmi': 26}},
            {'dataset': 'pima', 'inputs': {'age': 75, 'glucose': 175, 'bmi': 33}},
            {'dataset': 'pima', 'inputs': {'age': 45, 'glucose': None, 'bmi': None}},
            {'dataset': 'ilpd', 'inputs': {'age': 45, 'albumin': 4, 'bilirubin': 1}},
        ]
        harness = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const context = vm.createContext({document: {addEventListener() {}}});
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(cases.map(item => context.previewTargetRules(item.dataset, item.inputs))));
"""
        output = subprocess.run(['node', '-e', harness, str(ROOT / 'medical_expert/web/static/workspace.js')],
                                input=json.dumps(cases), check=True, capture_output=True, text=True)
        previews = json.loads(output.stdout)
        for case, preview in zip(cases, previews):
            with self.subTest(case=case):
                _, fired = evaluate_rules(case['dataset'], case['inputs'])
                target_count = sum(rule['target'] == case['dataset'] for rule in fired)
                self.assertEqual(preview['matched'], target_count)
        self.assertEqual(previews[0]['matched'], 0)
        self.assertEqual(previews[1]['matched'], 1)
        self.assertTrue(previews[2]['pending'])
        self.assertFalse(previews[3]['pending'])
        self.assertEqual(previews[6]['matched'], 1)

    def test_result_visuals_use_trace_scores_and_handle_missing_rules(self):
        harness = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const nodes = {};
function element(tag) {
    return {tag, children: [], textContent: '', className: '', attrs: {},
        style: {vars: {}, setProperty(key, value) { this.vars[key] = value; }},
        append(...items) { this.children.push(...items); },
        replaceChildren(...items) { this.children = items; },
        setAttribute(key, value) { this.attrs[key] = value; }
    };
}
function contents(el) {
    if (typeof el === 'string') return el;
    return [el.textContent, ...el.children.map(contents)].join(' ');
}
function find(el, predicate) {
    if (typeof el === 'string') return undefined;
    return predicate(el) ? el : el.children.map(child => find(child, predicate)).find(Boolean);
}
const document = {
    getElementById(id) { return nodes[id] ||= element('div'); },
    createElement: element,
    createElementNS(_, tag) { return element(tag); },
    addEventListener() {},
};
const context = vm.createContext({document});
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
const trace = {target:'pima', ml:{model:'KNN', score:1/7},
 facts:[{feature:'age', value:45, unit:'years', key:null}],
 fired_rules:[{id:'fixture', conditions:[], conclusion:'minh họa', cf:.5, used_in_fusion:true}],
 result:{rule_status:'matched', rule_score:.5, combined_score:4/7, predicted_label:1}};
const disease = {has_target_rules:true, fields:[{key:'age', label:'Tuổi'}]};
context.renderTrace(trace, disease);
const strip = find(nodes.traceResult, el => el.className === 'compare-strip');
assert.match(contents(strip), /14,3%.*50,0%.*57,1%/);
const needle = find(nodes.traceResult, el => el.attrs.class === 'gauge-needle');
assert.equal(needle.style.vars['--needle-deg'], '12.9deg');
assert.match(contents(nodes.livePipeline), /14,3%.*50,0%.*57,1%/);
assert.doesNotMatch(contents(nodes.livePipeline), /C_new/);
assert.match(contents(nodes.fusionDetails), /C_new/);

trace.fired_rules = [];
trace.result.rule_score = null;
trace.result.combined_score = trace.ml.score;
trace.result.predicted_label = 0;
context.renderTrace(trace, disease);
assert.match(contents(nodes.traceResult), /Không có luật đích khớp/);
assert.match(contents(nodes.livePipeline), /Chưa có điểm/);

disease.has_target_rules = false;
context.renderTrace(trace, disease);
const onlyMl = find(nodes.traceResult, el => el.className === 'compare-strip');
assert.match(contents(onlyMl), /Bộ dữ liệu chưa có luật đích/);
assert.doesNotMatch(contents(onlyMl), /Kết hợp/);
"""
        subprocess.run(['node', '-e', harness, str(ROOT / 'medical_expert/web/static/workspace.js')],
                       check=True, capture_output=True, text=True)

    def test_trace_rendering_treats_text_as_text_and_shows_unknown(self):
        harness = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const nodes = {};
function element(tag) {
    return { tag, children: [], className: '', textContent: '',
        append(...items) { this.children.push(...items); },
        replaceChildren(...items) { this.children = items; }
    };
}
function contents(el) {
    if (typeof el === 'string') return el;
    return [el.textContent, ...el.children.map(contents)].join(' ');
}
function find(el, predicate) {
    if (typeof el === 'string') return undefined;
    return predicate(el) ? el : el.children.map(child => find(child, predicate)).find(Boolean);
}
const document = {
    getElementById(id) { return nodes[id] ||= element('div'); },
    createElement: element,
    addEventListener() {},
};
const context = vm.createContext({document});
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
const trace = {target:'pima', ml:{model:'<b>model</b>', score:.4},
 facts:[{feature:'age', value:null, key:'age_fact', membership:null, value_boolean:null}],
 fired_rules:[], result:{rule_status:'no_matching_target_rule', rule_score:null, combined_score:.4, predicted_label:0}};
const disease = {has_target_rules:true, fields:[{key:'age', label:'Tuổi'}]};
context.renderTrace(trace, disease);
assert.match(contents(nodes.traceInputs), /Chưa biết/);
assert.match(contents(nodes.traceFacts), /Chưa biết/);
assert.match(contents(nodes.traceResult), /Không có luật đích/);
assert.match(contents(nodes.traceResult), /0\/1 chỉ số/);
const modelName = find(nodes.livePipeline, el => el.tag === 'small' && el.textContent.includes('<b>model</b>'));
assert.equal(modelName.textContent, 'Nhánh ML · <b>model</b> (điền trung vị)');
assert.equal(modelName.children.length, 0);
assert.match(contents(nodes.traceResult), /giữ nguyên theo ML/);
assert.doesNotMatch(contents(nodes.traceResult), /vì thiếu dữ kiện/);
trace.result.rule_score = 0.5;
trace.result.predicted_label = 1;
trace.result.combined_score = 0.7;
trace.fired_rules.push({id:'fixture', conditions:['age_fact'], conclusion:'minh họa', cf:.5, used_in_fusion:true});
context.renderTrace(trace, disease);
assert.match(contents(nodes.traceRules), /Dùng để gộp/);
assert.doesNotMatch(contents(nodes.traceResult), /Không có luật đích/);
trace.result.combined_score = 0.5;
context.renderTrace(trace, disease);
assert.match(contents(nodes.traceResult), /đạt ngưỡng 50%/);
trace.ml.score = 1;
trace.result.combined_score = 1;
context.renderTrace(trace, disease);
assert.doesNotMatch(contents(nodes.traceResult), /nâng điểm kết hợp/);
"""
        subprocess.run(['node', '-e', harness, str(ROOT / 'medical_expert/web/static/workspace.js')],
                       check=True, capture_output=True, text=True)

    def test_outdated_responses_cannot_replace_current_inputs_or_newer_results(self):
        harness = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const nodes = {};
function element() {
    return {hidden: false, inert: false, disabled: false, textContent: '',
        classList: {add() {}, remove() {}, toggle() {}},
        replaceChildren() {}, setAttribute() {}, removeAttribute() {}};
}
for (const id of ['loading', 'resultSection', 'emptyState', 'staleNotice', 'diagnosisErrors']) nodes[id] = element();
nodes.resultSection.hidden = true;
const submit = element();
const field = {name:'inputs.age', value:'45', validity:{badInput:false}};
const form = nodes.diagnosisForm = element();
form.elements = {namedItem: () => field};
form.querySelector = selector => selector === 'button[type=submit]' ? submit : null;
form.querySelectorAll = () => [];
const document = {
    getElementById: id => nodes[id],
    addEventListener() {},
};
const context = vm.createContext({document, setTimeout, clearTimeout});
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
vm.runInContext("diseases = {heart: {dataset: 'cleveland', fields: [{key: 'age'}]}}; currentDisease = 'heart'", context);
const pending = [];
const rendered = [];
context.fetchJson = () => new Promise(resolve => pending.push(resolve));
context.renderTrace = trace => rendered.push(trace.id);
context.loadHistory = () => {};
const event = () => ({preventDefault() {}, currentTarget: form});
const response = id => ({trace:{id, result:{combined_score:0.5}}});

(async () => {
    const old = context.runDiagnosis(event(), {preserveFocus:true});
    field.value = '46';
    context.markResultStale();
    pending.shift()(response('outdated input'));
    await old;
    assert.deepEqual(rendered, []);
    assert.equal(nodes.emptyState.hidden, false);

    const first = context.runDiagnosis(event(), {preserveFocus:true});
    field.value = '47';
    context.markResultStale();
    const second = context.runDiagnosis(event(), {preserveFocus:true});
    const resolveFirst = pending.shift();
    const resolveSecond = pending.shift();
    resolveSecond(response('newest'));
    await second;
    resolveFirst(response('late'));
    await first;
    assert.deepEqual(rendered, ['newest']);
    assert.equal(nodes.resultSection.hidden, false);
    assert.equal(nodes.staleNotice.hidden, true);
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
        subprocess.run(['node', '-e', harness, str(ROOT / 'medical_expert/web/static/workspace.js')],
                       check=True, capture_output=True, text=True)
