import unittest
from rapid_elastic import filetool
from rapid_elastic import naming
from rapid_elastic import disease_names
from rapid_elastic import sql_compare

class TestSQLCompare(unittest.TestCase):
    def test_table_names(self):
        expected = filetool.read_text(filetool.resource('tables.list')).splitlines()
        actual = disease_names.list_cohorts()
        _diff1 = set(actual).difference(set(expected))
        self.assertTrue(len(_diff1) == 0, f'{_diff1} expected, was missing')

    @unittest.skip('rapid__match_notes.sql')
    def test_union_views_match_notes(self):
        print(sql_compare.union_views_file(
            create='rapid__match_notes',
            table_list=disease_names.list_cohorts(),
            create_table=True, alias_col='disease_alias'))

    @unittest.skip('rapid__match_notes_sample_patients.sql')
    def test_union_views_match_notes_sample(self):
        print(sql_compare.union_views_file(
            create='rapid__match_notes_sample_patients',
            table_list=disease_names.list_cohorts(),
            create_table=True, alias_col='disease_alias', sample_size=100))
