import unittest
import os
from rapid_elastic import config

class TestElasticConfig(unittest.TestCase):
    def test(self):
        for key in os.environ:
            if 'SCP_' in key or 'ELASTIC' in key:
                print(f'{key}={os.environ[key]}')

    def test_elastic(self):
        self.assertIsNotNone(config.ELASTIC_HOST)
        self.assertIsNotNone(config.ELASTIC_USER)
        self.assertIsNotNone(config.ELASTIC_PASS)
