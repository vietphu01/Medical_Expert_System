import importlib.util
import os
import sqlite3
import unittest
from contextlib import chdir, closing
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]


class HistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = Path(cls.enterClassContext(TemporaryDirectory()))
        cls.startup_db = cls.directory / 'startup.db'

        # Cô lập import và cả đường dẫn tương đối nếu app dùng DB mặc định.
        spec = importlib.util.spec_from_file_location('history_test_app', ROOT / 'medical_expert/web/app.py')
        cls.module = importlib.util.module_from_spec(spec)
        with chdir(cls.directory), patch.dict(os.environ, MEDICAL_HISTORY_DB=str(cls.startup_db)):
            spec.loader.exec_module(cls.module)

    def setUp(self):
        self.enterContext(chdir(self.directory))

    def test_missing_and_malformed_runs_start_unavailable(self):
        for content in (None, '{bad json'):
            with self.subTest(content=content):
                run_dir = self.directory / ('missing-run' if content is None else 'bad-run')
                if content is not None:
                    run_dir.mkdir(exist_ok=True)
                    (run_dir / 'models.json').write_text(content, encoding='utf-8')
                spec = importlib.util.spec_from_file_location('unavailable_test_app', ROOT / 'medical_expert/web/app.py')
                module = importlib.util.module_from_spec(spec)
                with patch.dict(os.environ, MEDICAL_HISTORY_DB=str(self.directory / 'unavailable.db'),
                                MEDICAL_MODEL_RUN=str(run_dir)):
                    spec.loader.exec_module(module)
                module.app.template_folder = str(ROOT / 'medical_expert/web/templates')
                client = module.app.test_client()
                page = client.get('/')
                self.assertEqual(page.status_code, 200)
                self.assertIn('modelStatus', page.get_data(as_text=True))
                response = client.get('/api/model_stats/heart')
                self.assertEqual(response.status_code, 503)
                self.assertIn('model', response.get_json()['errors'])

    def test_startup_creates_full_history_schema(self):
        self.assertTrue(self.startup_db.is_file())
        with closing(sqlite3.connect(self.startup_db)) as conn:
            columns = conn.execute('PRAGMA table_info(history)').fetchall()

        self.assertEqual(
            [(name, data_type) for _, name, data_type, _, _, _ in columns],
            [('id', 'INTEGER'), ('disease', 'TEXT'), ('features', 'TEXT'),
             ('ml_prob', 'REAL'), ('risk_level', 'TEXT'), ('advice', 'TEXT'),
             ('timestamp', 'DATETIME')],
        )
        self.assertEqual(columns[0][5], 1)
        self.assertEqual(columns[-1][4], 'CURRENT_TIMESTAMP')

    def test_two_initializations_preserve_existing_history(self):
        db_path = self.directory / 'existing.db'
        self.enterContext(patch.dict(self.module.app.config, DATABASE=str(db_path)))
        self.module.init_db()

        record = (7, 'heart', '{}', 0.25, 'LOW', 'Ca mẫu', '2026-01-01 00:00:00')
        with closing(sqlite3.connect(db_path)) as conn, conn:
            conn.execute('INSERT INTO history VALUES (?, ?, ?, ?, ?, ?, ?)', record)

        for iteration in (1, 2):
            with self.subTest(initialization=iteration):
                self.module.init_db()
                with closing(sqlite3.connect(db_path)) as conn:
                    self.assertEqual(conn.execute('SELECT * FROM history').fetchall(), [record])

    def test_latest_ten_include_newest_id_when_times_match(self):
        db_path = self.directory / 'same-second.db'
        self.enterContext(patch.dict(self.module.app.config, DATABASE=str(db_path)))
        self.module.init_db()
        with closing(sqlite3.connect(db_path)) as conn, conn:
            conn.executemany('INSERT INTO history (id, timestamp) VALUES (?, ?)',
                             [(i, '2026-01-01 00:00:00') for i in range(1, 12)])
        rows = self.module.app.test_client().get('/api/history').get_json()
        self.assertEqual([row[0] for row in rows], list(range(11, 1, -1)))

    def test_diagnose_and_history_share_configured_database(self):
        db_path = self.directory / 'routes.db'
        self.enterContext(patch.dict(self.module.app.config, DATABASE=str(db_path)))
        self.module.init_db()
        model = Mock(variant='fixture', score=Mock(return_value=0.45))
        self.enterContext(patch.dict(self.module.MODELS, {'cleveland': model}, clear=True))
        client = self.module.app.test_client()
        diagnosis = client.post('/api/diagnose', json={
            'disease': 'heart',
            'inputs': {'age': 50, 'bp': 130, 'chol': 240},
        })
        self.assertEqual(diagnosis.status_code, 200)

        with closing(sqlite3.connect(db_path)) as conn:
            rows = conn.execute('SELECT * FROM history').fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], 'heart')
        self.assertEqual(round(rows[0][3] * 100, 2), diagnosis.get_json()['ml_probability'])

        history = client.get('/api/history')
        self.assertEqual(history.status_code, 200)
        self.assertEqual(history.get_json(), [list(rows[0])])
