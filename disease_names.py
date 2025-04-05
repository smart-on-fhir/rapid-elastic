import re
import csv
from pathlib import Path

import filetool

RARE_LT10_PER_100K = "RARE_LT10_PER_100K.csv"
RARE_LT50_PER_100K = "RARE_LT50_PER_100K.csv"

def read_disease_names(disease_csv: Path | str) -> dict:
    with open(filetool.resource(disease_csv), newline='') as csvfile:
        reader = csv.reader(csvfile)
        out = {}

        # Optional: skip header if presentf
        headers = next(reader)
        print(headers)

        # Loop through rows
        for row in reader:
            # Each row is a list of column values
            print(row)          # Full row as list
            disease_name = row[0]
            disease_name = strip_paren(disease_name)

            # initialize search keywords only with self
            out[disease_name] = [disease_name]
        return out

def strip_paren(disease: str) -> str:
    # Replace anything in parentheses (non-greedy match)
    # Autosomal Recessive Polycystic Kidney Disease (ARPKD) -->
    # Autosomal Recessive Polycystic Kidney Disease
    return re.sub(r"\s*\([^)]*\)", "", disease)

def disease_names() -> Path:
    out = read_disease_names(RARE_LT10_PER_100K) | read_disease_names(RARE_LT50_PER_100K)
    print(f"{len(out.keys())} disease names")
    return filetool.write_json(out, filetool.resource('disease_names.json'))


if __name__ == '__main__':
    # print(disease_names())
    pass
