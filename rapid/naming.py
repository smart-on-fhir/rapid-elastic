import re

###############################################################################
# Athena table names
###############################################################################
def name_table(table: list | str) -> list | str:
    table = name_file(table).lower()
    if isinstance(table, list):
        return [f'cohorts__rare_{table}' for table in list(set(table))]
    else:
        return f'cohorts__rare_{table}'

###############################################################################
# Disease Names
###############################################################################
def name_unique(disease: str | list[str]) -> str | list[str]:
    if isinstance(disease, list):
        return [name_unique(entry) for entry in disease]
    unique = list()
    for token in strip_paren(disease).split():
        if token == token.upper():
            unique.append(token)
        else:
            unique.append(token.title())
    return ' '.join(unique)

def name_file(disease: str, extension=None):
    """
    :param disease: disease name see "name_unique()"
    :param extension: optional file extension
    :return: str filename prepared
    """
    disease = name_unique(disease).strip()
    for sep in [' ', '/', '-', '.']:
        disease = disease.replace(sep, '_')
    if extension:
        return f'{disease}.{extension}'
    return disease

def strip_spaces(disease: str):
    return disease.replace(' ', '_').strip()

def strip_paren(disease: str) -> str:
    # Replace anything in parentheses (non-greedy match)
    # Autosomal Recessive Polycystic Kidney Disease (ARPKD) -->
    # Autosomal Recessive Polycystic Kidney Disease
    return re.sub(r"\s*\([^)]*\)", "", disease).strip()
