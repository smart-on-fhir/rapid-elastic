import unittest
from rapid_elastic import config

class TestElasticConfig(unittest.TestCase):
    def test_elastic(self):
        self.assertIsNotNone(config.ELASTIC_HOST)
        self.assertIsNotNone(config.ELASTIC_USER)
        self.assertIsNotNone(config.ELASTIC_PASS)