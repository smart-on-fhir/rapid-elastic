import unittest
from rapid import filetool

class TestFiletool(unittest.TestCase):
    def test_curated_csv_exists(self):
        for curated_csv in filetool.CSV_LIST:
            self.assertTrue(filetool.resource(curated_csv).exists())

    @unittest.skip('Create output folder with date like "output/2025-04-10')
    def test_output_folder(self):
        output_csv = filetool.output('test.csv')
        print(output_csv)
