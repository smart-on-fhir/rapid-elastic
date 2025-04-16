import unittest
from rapid_elastic import filetool

class TestFiletool(unittest.TestCase):

    @unittest.skip('Create output folder with date like "output/2025-04-10')
    def test_output_folder(self):
        output_csv = filetool.output_dir() / 'test.csv'
        print(output_csv)
