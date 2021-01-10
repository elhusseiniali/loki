import unittest
import requests
import json
import base64

from flask_testing import TestCase
from loki import create_app, db
from loki.config import TestConfig

class BaseTestCase(TestCase):
    """A base test case.
    
    Nota Bene : If you don’t define create_app a NotImplementedError will be raised.
    """
    def create_app(self):
        return create_app(TestConfig)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class AttackApiTestCase(BaseTestCase):
    """A test case for all actions by the Attack API"""

    # Ensure attacks/all behaves correctly
    def test_attack_all_api(self):
        response = self.client.get("/api/1/attacks/all")
        content = json.loads(response.data)[0]
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', content.keys())
        self.assertIn('paper', content.keys())

    # Ensure attacks/run behaves correctly
    def test_attack_id_api(self):
        response_200 = self.client.get("/api/1/attacks/1")
        content = json.loads(response_200.data)
        attack = {
            "name": "FastGradientSignMethod",
            "paper": "https://arxiv.org/abs/1412.6572"
        }
        self.assertEqual(response_200.status_code, 200)
        self.assertEqual(attack, content)
        
        response_404 = self.client.get("/api/1/attacks/10")
        response_422 = self.client.get("/api/1/attacks/donneleC")
        self.assertEqual(response_404.status_code, 404)
        self.assertEqual(response_422.status_code, 422)

    # Ensure attacks/{attack_id} behaves correctly
    def test_attack_put(self):
        image = open("loki/static/data/Yellow-Labrador-Retriever.jpg", "rb")
        im = image.read()
        im_b64 = base64.b64encode(im)
        files_200 = {'image_data': im_b64,
                 'attack_id': 1,
                 'classifier_id': 1}
        response_200 = self.client.put("/api/1/attacks/run", data=files_200)
        images_dict = json.loads(response_200.data)
        self.assertEqual(response_200.status_code, 200)
        self.assertIn('original_image', images_dict.keys())
        self.assertIn('difference_image', images_dict.keys())
        self.assertIn('result_image', images_dict.keys())

        files_404 = {'image_data': im_b64,
                 'attack_id': 10,
                 'classifier_id': 1}
        response_404 = self.client.put("/api/1/attacks/run", data=files_404)
        self.assertEqual(response_404.status_code, 404)

        bad_data = "notanimage"
        files_422 = {'image_data': bad_data,
                 'attack_id': 1,
                 'classifier_id': 1}
        response_422 = self.client.put("/api/1/attacks/run", data=files_422)
        self.assertEqual(response_422.status_code, 422)

class ClassifyApiTestCase(BaseTestCase):
    """A test case for all actions by the Classifiers API"""

    # Ensure classifiers/all behaves correctly
    def test_classify_all_api(self):
        response = self.client.get("/api/1/classifiers/all")
        content = json.loads(response.data)[0]
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', content.keys())
        self.assertIn('paper', content.keys())

    # Ensure classifiers/classify behaves correctly
    def test_classifier_id_api(self):
        response_200 = self.client.get("/api/1/classifiers/1")
        content = json.loads(response_200.data)
        classifier = {
            "name": "Inception v3",
            "paper": "https://arxiv.org/abs/1512.00567"
        }
        self.assertEqual(response_200.status_code, 200)
        self.assertEqual(classifier, content)
        
        response_404 = self.client.get("/api/1/classifiers/10")
        response_422 = self.client.get("/api/1/classifiers/donneleC")
        self.assertEqual(response_404.status_code, 404)
        self.assertEqual(response_422.status_code, 422)

    # Ensure classifiers/{classifier_id} behaves correctly
    def test_classifier_put(self):
        image = open("loki/static/data/Yellow-Labrador-Retriever.jpg", "rb")
        im = image.read()
        im_b64 = base64.b64encode(im)
        files_200 = {'image_data': im_b64,
                 'classifier_id': 1}
        response_200 = self.client.put("/api/1/classifiers/classify", data=files_200)
        results_dict = json.loads(response_200.data)[0]
        self.assertEqual(response_200.status_code, 200)
        self.assertIn('index', results_dict.keys())
        self.assertIn('label', results_dict.keys())
        self.assertIn('percentage', results_dict.keys())

        files_404 = {'image_data': im_b64,
                 'classifier_id': 10}
        response_404 = self.client.put("/api/1/classifiers/classify", data=files_404)
        self.assertEqual(response_404.status_code, 404)

        bad_data = "notanimage"
        files_422 = {'image_data': bad_data,
                 'classifier_id': 1}
        response_422 = self.client.put("/api/1/classifiers/classify", data=files_422)
        self.assertEqual(response_422.status_code, 422)


class DatasetApiTestCase(BaseTestCase):
    """A test case for all actions by the Datasets API"""

    # Ensure datasets/all behaves correctly
    def test_dataset_all_api(self):
        response = self.client.get("/api/1/datasets/all")
        content = json.loads(response.data)[0]
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', content.keys())
        self.assertIn('paper', content.keys())

    # Ensure GET /datasets/labels/{dataset_id} behaves correctly
    def test_dataset_id_api(self):
        response_200 = self.client.get("/api/1/datasets/labels/0")
        content = json.loads(response_200.data)
        self.assertEqual(response_200.status_code, 200)
        self.assertIn("goldfish", content)
        
        response_404 = self.client.get("/api/1/datasets/labels/10")
        response_422 = self.client.get("/api/1/datasets/labels/donneleC")
        self.assertEqual(response_404.status_code, 404)
        self.assertEqual(response_422.status_code, 422)

    # Ensure PUT /datasets/labels/{dataset_id} behaves correctly
    def test_dataset_put_label(self):
        files_200 = {'dataset_id': 0,
                 'class_id': 1}
        response_200 = self.client.put("/api/1/datasets/labels/0", data=files_200)
        results_dict = json.loads(response_200.data)
        self.assertEqual(response_200.status_code, 200)
        self.assertEqual('goldfish', results_dict)

        files_404 = {'dataset_id': 0,
                 'class_id': 1000000}
        response_404 = self.client.put("/api/1/datasets/labels/0", data=files_404)
        self.assertEqual(response_404.status_code, 404)

        files_422 = {'dataset_id': 0,
                 'class_id': "notaninteger"}
        response_422 = self.client.put("/api/1/datasets/labels/0", data=files_422)
        self.assertEqual(response_422.status_code, 422)

    # Ensure /datasets/{dataset_id} behaves correctly
    def test_dataset_put_dataset(self):
        files_200 = {'dataset_id': 0}
        response_200 = self.client.put("/api/1/datasets/0", data=files_200)
        results_dict = json.loads(response_200.data)
        dataset_truth = {'name': 'ImageNet', 'paper': 'https://arxiv.org/abs/1409.0575'}
        self.assertEqual(response_200.status_code, 200)
        self.assertEqual(dataset_truth, results_dict)

        files_404 = {'dataset_id': 10}
        response_404 = self.client.put("/api/1/datasets/datasets/10", data=files_404)
        self.assertEqual(response_404.status_code, 404)


class ReportApiTestCase(BaseTestCase):
    """A test case for all actions by the Report API"""

    # Ensure /reports/all behaves correctly
    def test_report_all_api(self):
        response = self.client.get("/api/1/reports/all")
        content = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('reports', content.keys())

if __name__ == '__main__':
    unittest.main()