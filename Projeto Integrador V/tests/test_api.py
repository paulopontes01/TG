import unittest
import joblib
import pandas as pd
from fastapi.testclient import TestClient
from api.app import app, MODEL_PATH


class APITest(unittest.TestCase):
    def test_http_matches_original(self):
        original = joblib.load(MODEL_PATH)
        with TestClient(app) as client:
            for case in [dict(valor_anuncio=2200, dormitorios=2, banheiros=1, garagens=1, tipo='Apartamento', bairro='Jardim Vera Cruz'), dict(valor_anuncio=5500, dormitorios=3, banheiros=2, garagens=0, tipo='Casa', bairro='Centro'), dict(valor_anuncio=1000, dormitorios=0, banheiros=1, garagens=0, tipo='Tipo sintético', bairro='Bairro sintético')]:
                expected = original.predict_proba(pd.DataFrame([case]))[0, list(original.classes_).index(1)]
                response = client.post('/api/predict', json=case)
                self.assertEqual(response.status_code, 200, response.text)
                self.assertAlmostEqual(response.json()['probabilidade_sucesso'], expected, places=4)

    def test_validation(self):
        valid = dict(valor_anuncio=2200, tipo='Apartamento', bairro='Centro')
        with TestClient(app) as client:
            for change in [dict(valor_anuncio=-1), dict(bairro=' '), dict(dormitorios=-1), dict(disponibilidade='Vendido')]:
                self.assertEqual(client.post('/api/predict', json=valid | change).status_code, 422)
            self.assertEqual(client.post('/api/predict', json={}).status_code, 422)

    def test_front_health_metadata(self):
        with TestClient(app) as client:
            for path in ('/', '/health', '/api/model', '/docs'):
                self.assertEqual(client.get(path).status_code, 200)
            self.assertIn('/api/predict', client.get('/').text)
            self.assertNotIn('http://127.0.0.1:8001', client.get('/').text)
            self.assertTrue(client.get('/health').json()['ready'])
            self.assertNotIn('/predict', client.get('/openapi.json').json()['paths'])
            self.assertEqual(client.post('/predict', json={}).status_code, 404)
