from typing import List
from pathlib import Path
from rapid import filetool

def union_views(create: str, table_list: List[str], create_table=False, alias_col='alias', sample_size=0) -> str:
    if create_table:
        create = f"create TABLE {create} AS \n"
    else:
        create = f"create or replace VIEW {create} AS \n"

    select = list()
    for table in table_list:
        alias = table.replace('cohorts__rare_', '')
        if sample_size > 0:
            select.append(f"(select distinct '{alias}' as {alias_col}, subject_ref from {table} limit {sample_size})")
        else:
            select.append(f"select distinct '{alias}' as {alias_col}, * from {table}")
    out = create + '\n UNION '.join(select)
    return out

def union_views_file(create: str, table_list: List[str], create_table=False, alias_col='alias', sample_size=0) -> Path:
    return filetool.write_text(
        contents=union_views(create, table_list, create_table, alias_col, sample_size),
        file_path=filetool.resource(f'{create}.sql'))
