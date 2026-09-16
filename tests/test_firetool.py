import unittest
from rapid_elastic import filetool
from pathlib import Path

class FiretoolTest(unittest.TestCase):
    
    def setUp(self):
        self.resources_path = Path(__file__).parent.parent / "rapid_elastic" / "resources"
    
    def test_query_topics_txt(self):
        REFERENCE_NAME = "dx_citrullinemia"
        txt = filetool.read_query_topics_txt(self.resources_path / ("query_topics/" + REFERENCE_NAME + ".txt"))
        from_json = filetool.read_query_topics_json(self.resources_path / "query_topics.json")
        self.assertEqual(txt[REFERENCE_NAME], from_json[REFERENCE_NAME])