import unittest
from rapid import filetool
from rapid import naming
from rapid import disease_names
from rapid import sql_compare

class TestSQLCompare(unittest.TestCase):

    @unittest.skip('cohorts__rare_match_notes.sql')
    def test_union_views_compare_notes(self):
        print(sql_compare.union_views_file(
            create='cohorts__rare_match_notes',
            table_list=disease_names.list_tables(),
            create_table=True, alias_col='disease_alias'))

    @unittest.skip('cohorts__rare_match_codeset.sql')
    def test_union_views_codeset_icd10(self):
        tables_list = [t.replace('.csv', '') for t in filetool.DEPRECATED_CSV_LIST]
        tables_list = [naming.name_table(f'codeset_{t}') for t in tables_list]
        print(sql_compare.union_views_file(
            create='cohorts__rare_codeset',
            table_list=tables_list,
            create_table=True,
            alias_col='source_csv'))

    def test_table_names(self):
        expected = filetool.read_text(filetool.resource('tables.list')).splitlines()
        actual = disease_names.list_tables()
        _diff1 = set(actual).difference(set(expected))

        self.assertTrue(len(_diff1) == 0, f'{_diff1} expected, was missing')
