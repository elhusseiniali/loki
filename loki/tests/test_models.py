import unittest
from loki.models import User, Classifier, Report

from datetime import datetime


class TestObjectCreation(unittest.TestCase):
    def test_basic_creation(self):
        frege = User(username="frege",
                     email="frege@gmail.com",
                     password="weakpassword123")
        assert frege

        resnet = Classifier(
            name="ResNet",
            file_path="dummy_path",
            user=frege
        )
        assert resnet

        some_report = Report(date=datetime.now(),
                             model=resnet)
        assert some_report
