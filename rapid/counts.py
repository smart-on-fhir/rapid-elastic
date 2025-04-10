from typing import List
import re
import disease_names
import naming
import filetool

PREFIX = 'cohorts__rare'

# def get_table_name(disease: str) -> str:
#     cleaned = disease.replace('(', '').replace(')', '').replace(' ', '_').lower()
#     return f'{PREFIX}_{cleaned}'

# def list_table_names(filename_json='disease_names_expanded.json') -> List[str]:
#     curated = filetool.disease_names_json(filename_json)
#     table_list = list()
#     for disease in curated.keys():
#         table_list.append(get_table_name(disease))
#     print(table_list)
#     return table_list
#
# def select_table(table_name: str) -> str:
#     if PREFIX not in table_name:
#         table_name = get_table_name(table_name)
#     return f'select * from {table_name}'

# def select_union() -> str:
#     out = list()
#     for table in list_table_names():
#         sql = select_table() + " UNION "

###############################################################################
#
# ICD10
#
###############################################################################
