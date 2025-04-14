import unittest
from rapid_elastic import config

class TestElasticConfig(unittest.TestCase):
    def test_not_null(self):
        self.assertTrue(config.ELASTIC_HOST)
        self.assertTrue(config.ELASTIC_USER)
        self.assertTrue(config.ELASTIC_PASS)
