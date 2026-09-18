import unittest
from rapid_elastic import config, filetool

class TestElasticConfig(unittest.TestCase):
    def test_elastic_host(self):
        self.assertIsNotNone(config.ELASTIC_HOST)

    def test_default_output(self):
        """
        filetool.date_str() returns today’s date string, probably something like 2026-07-08.
        """
        actual = filetool.path_output()
        expected = filetool.date_str()
        self.assertTrue(str(actual).endswith(expected))
