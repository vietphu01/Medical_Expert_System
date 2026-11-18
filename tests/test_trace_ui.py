"""Exercise the same trace renderer that Flask serves, with invented facts."""
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('node'), 'node is not installed')
class TraceUiTests(unittest.TestCase):
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
const modelName = nodes.traceResult.children.find(child => child.className === 'score-grid').children[0].children[0];
assert.equal(modelName.textContent, 'ML · <b>model</b>');
assert.equal(modelName.children.length, 0);
trace.result.rule_score = 0.5;
trace.result.predicted_label = 1;
trace.result.combined_score = 0.7;
trace.fired_rules.push({id:'fixture', conditions:['age_fact'], conclusion:'minh họa', cf:.5, used_in_fusion:true});
context.renderTrace(trace, disease);
assert.match(contents(nodes.traceRules), /Dùng để gộp/);
assert.doesNotMatch(contents(nodes.traceResult), /Không có luật đích/);
"""
        subprocess.run(['node', '-e', harness, str(ROOT / 'static/workspace.js')],
                       check=True, capture_output=True, text=True)
