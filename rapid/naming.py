from typing import List
import re

###############################################################################
# Athena table names
###############################################################################
TABLE_PREFIX = "cohorts__rare"

def name_table(table: list | str) -> list | str:
    table = name_unique(table)
    if isinstance(table, list):
        return [f'{TABLE_PREFIX}__{table}' for table in list(set(table))]
    else:
        return f'{TABLE_PREFIX}__{table}'

###############################################################################
# Disease Names
###############################################################################
def name_unique(disease: str | List[str]) -> str | List[str]:
    if isinstance(disease, list):
        return [name_unique(entry) for entry in disease]
    unique = list()
    for token in strip_paren(disease).strip().split():
        if token == token.upper():
            unique.append(token)
        else:
            unique.append(token.title())
    return ' '.join(unique)

def name_file(disease: str, extension=None):
    disease = name_unique(disease).replace(' ', '_')
    if extension:
        return f'{disease}.{extension}'
    return disease

def strip_spaces(disease: str):
    return disease.replace(' ', '_').replace('/', '-').strip()

def strip_paren(disease: str) -> str:
    # Replace anything in parentheses (non-greedy match)
    # Autosomal Recessive Polycystic Kidney Disease (ARPKD) -->
    # Autosomal Recessive Polycystic Kidney Disease
    return re.sub(r"\s*\([^)]*\)", "", disease).strip()
