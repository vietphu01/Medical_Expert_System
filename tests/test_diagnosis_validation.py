import importlib.util
import os
import shutil
import sqlite3
import unittest
from contextlib import chdir, closing
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from diseases_config import DISEASES


ROOT = Path(__file__).resolve().parents[1]


class DiagnosisValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = Path(cls.enterClassContext(TemporaryDirectory()))
        shutil.copyfile(ROOT / 'knowledge_base.json', cls.directory / 'knowledge_base.json')
        spec = importlib.util.spec_from_file_location('validation_test_app', ROOT / 'app.py')
        cls.module = importlib.util.module_from_spec(spec)
        with chdir(cls.directory), patch.dict(
            os.environ, MEDICAL_HISTORY_DB=str(cls.directory / 'startup.db')
        ):
            spec.loader.exec_module(cls.module)

    def setUp(self):
        self.enterContext(chdir(self.directory))
        db_dir = Path(self.enterContext(TemporaryDirectory()))
        self.db = db_dir / 'history.db'
        self.enterContext(patch.dict(self.module.app.config, DATABASE=str(self.db)))
        self.module.init_db()
        self.client = self.module.app.test_client()

    def count_history(self):
        with closing(sqlite3.connect(self.db)) as conn:
            return conn.execute('SELECT COUNT(*) FROM history').fetchone()[0]

    @staticmethod
    def payload(disease='heart'):
        return {
            'disease': disease,
            'inputs': {field['key']: field['default'] for field in DISEASES[disease]['fields']},
        }

    def assert_invalid(self, field, *, payload=None, data=None, content_type=None):
        before = self.count_history()
        with (
            patch.object(self.module, 'compute_fuzzy_facts') as fuzzy,
            patch.object(self.module.engine, 'forward_chaining') as inference,
        ):
            if data is not None:
                response = self.client.post('/api/diagnose', data=data, content_type=content_type)
            else:
                response = self.client.post('/api/diagnose', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.is_json)
        errors = response.get_json()['errors']
        self.assertIn(field, errors)
        self.assertIsInstance(errors[field], str)
        self.assertTrue(errors[field])
        fuzzy.assert_not_called()
        inference.assert_not_called()
        self.assertEqual(self.count_history(), before)

    def test_valid_requests_for_all_diseases_and_form_strings(self):
        for disease in DISEASES:
            for use_strings in (False, True):
                with self.subTest(disease=disease, strings=use_strings):
                    payload = self.payload(disease)
                    if disease == 'heart':
                        payload['inputs']['bp'] = 160
                        payload['extra_facts'] = {'chest_pain': True, 'short_breath': True}
                    if use_strings:
                        payload['inputs'] = {key: str(value) for key, value in payload['inputs'].items()}
                    before = self.count_history()
                    response = self.client.post('/api/diagnose', json=payload)
                    self.assertEqual(response.status_code, 200)
                    result = response.get_json()
                    expected_keys = {'ml_probability', 'fuzzy_values', 'expert_conclusions', 'fired_rules'}
                    self.assertLessEqual(expected_keys, result.keys())
                    if disease == 'heart':
                        self.assertIn('HEART_R1', result['fired_rules'])
                    self.assertEqual(self.count_history(), before + 1)

    def test_body_must_be_valid_json_object(self):
        for data, content_type in [
            ('{', 'application/json'), ('null', 'application/json'),
            ('[]', 'application/json'), ('"heart"', 'application/json'),
            ('', 'application/json'), ('{}', 'text/plain'),
        ]:
            with self.subTest(data=data, content_type=content_type):
                self.assert_invalid('body', data=data, content_type=content_type)

    def test_disease_validation_and_unknown_model_stats(self):
        for disease in (None, '', 'unknown', 1, True, [], {}):
            with self.subTest(disease=disease):
                payload = self.payload()
                payload['disease'] = disease
                self.assert_invalid('disease', payload=payload)
        payload = self.payload()
        del payload['disease']
        self.assert_invalid('disease', payload=payload)
        response = self.client.get('/api/model_stats/unknown')
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.is_json)
        self.assertTrue(response.get_json()['errors']['disease'])
        self.assertEqual(self.count_history(), 0)

    def test_required_inputs_and_input_object_type(self):
        for disease, config in DISEASES.items():
            for field in config['fields']:
                with self.subTest(disease=disease, field=field['key']):
                    payload = self.payload(disease)
                    del payload['inputs'][field['key']]
                    self.assert_invalid('inputs.' + field['key'], payload=payload)
        for value in (None, [], 'bad', 1, True):
            with self.subTest(inputs=value):
                payload = self.payload()
                payload['inputs'] = value
                self.assert_invalid('inputs', payload=payload)
        payload = self.payload()
        del payload['inputs']
        self.assert_invalid('inputs', payload=payload)

    def test_rejects_invalid_values_and_out_of_range_for_each_field(self):
        for disease, config in DISEASES.items():
            for field in config['fields']:
                key = field['key']
                values = [True, False, None, [], {}, '', 'not a number',
                          'NaN', 'Infinity', '-Infinity', float('nan'),
                          float('inf'), float('-inf'), field['min'] - 0.1,
                          field['max'] + 0.1]
                if key == 'age':
                    values += [50.5, '50.5']
                for value in values:
                    with self.subTest(disease=disease, field=key, value=value):
                        payload = self.payload(disease)
                        payload['inputs'][key] = value
                        self.assert_invalid('inputs.' + key, payload=payload)

    def test_range_endpoints_are_accepted(self):
        for disease, config in DISEASES.items():
            for field in config['fields']:
                for endpoint in ('min', 'max'):
                    with self.subTest(disease=disease, field=field['key'], endpoint=endpoint):
                        payload = self.payload(disease)
                        payload['inputs'][field['key']] = field[endpoint]
                        before = self.count_history()
                        response = self.client.post('/api/diagnose', json=payload)
                        self.assertEqual(response.status_code, 200)
                        self.assertEqual(self.count_history(), before + 1)

    def test_unknown_keys_and_extra_facts_are_rejected(self):
        payload = self.payload()
        payload['unknown'] = 'x'
        self.assert_invalid('body.unknown', payload=payload)
        payload = self.payload()
        payload['inputs']['unknown'] = 1
        self.assert_invalid('inputs.unknown', payload=payload)
        for value in (None, [], 'bad', 1, True):
            with self.subTest(extra_facts=value):
                payload = self.payload()
                payload['extra_facts'] = value
                self.assert_invalid('extra_facts', payload=payload)
        for fact in ('high_bp', 'old_age', 'unknown'):
            with self.subTest(fact=fact):
                payload = self.payload()
                payload['extra_facts'] = {fact: True}
                self.assert_invalid('extra_facts.' + fact, payload=payload)
        for disease in ('diabetes', 'liver', 'kidney'):
            for fact in ('chest_pain', 'short_breath'):
                with self.subTest(disease=disease, fact=fact):
                    payload = self.payload(disease)
                    payload['extra_facts'] = {fact: True}
                    self.assert_invalid('extra_facts.' + fact, payload=payload)
        for fact in ('chest_pain', 'short_breath'):
            for value in (1, 0, 'true', None, [], {}):
                with self.subTest(fact=fact, value=value):
                    payload = self.payload()
                    payload['extra_facts'] = {fact: value}
                    self.assert_invalid('extra_facts.' + fact, payload=payload)
