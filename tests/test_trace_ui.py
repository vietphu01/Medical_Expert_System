"""Exercise trace rendering with a small DOM stub, using invented values."""
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('node'), 'node is not installed')
class TraceUiTests(unittest.TestCase):
    def test_trace_rendering_treats_text_as_text_and_shows_unknown(self):
        html = (ROOT / 'templates/index.html').read_text(encoding='utf-8')
        start = html.index('        function appendTraceItem(')
        end = html.index('        // ===== SO SÁNH MODEL =====', start)
        code = html[start:end]
        harness = '''
const assert = require('assert');
const nodes = {};
function element() { return {children: [], textContent: '', className: '',
    appendChild(item) { this.children.push(item); },
    replaceChildren() { this.children = []; }}; }
const document = {getElementById(id) { return nodes[id] ||= element(); }, createElement: element};
''' + code + '''
const trace = {target: 'pima', ml: {model: '<b>model</b>', score: .4},
 facts: [{feature:'age', value:null, key:'age_fact', membership:null, value_boolean:null}],
 fired_rules: [], result: {rule_status:'no_matching_target_rule', rule_score:null,
 combined_score:.4, predicted_label:0}};
renderTrace(trace, {fields: [{key:'age', label:'Tuổi'}]});
assert.match(nodes.traceInputs.children[0].textContent, /Chưa biết/);
assert.match(nodes.traceFacts.children[0].textContent, /Chưa biết/);
assert.match(nodes.traceResult.children[1].textContent, /<b>model<\\/b>/);
assert.match(nodes.traceResult.children[2].textContent, /Không có luật đích/);
assert.equal(nodes.traceResult.children[1].children.length, 0);
'''
        subprocess.run(['node', '-e', harness], check=True, capture_output=True, text=True)
