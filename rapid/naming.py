import re

###############################################################################
# Athena table names
###############################################################################
TABLE_PREFIX = "cohorts__rare"

def name_table(table: list | str) -> list | str:
    if isinstance(table, list):
        return [f'{TABLE_PREFIX}__{table}' for table in list(set(table))]
    else:
        return f'{TABLE_PREFIX}__{table}'

###############################################################################
# Disease Names
###############################################################################
def strip_spaces(disease: str):
    return disease.replace(' ', '_')

def strip_paren(disease: str) -> str:
    # Replace anything in parentheses (non-greedy match)
    # Autosomal Recessive Polycystic Kidney Disease (ARPKD) -->
    # Autosomal Recessive Polycystic Kidney Disease
    return re.sub(r"\s*\([^)]*\)", "", disease)
