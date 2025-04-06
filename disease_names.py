import re
import csv
from pathlib import Path

import filetool

RARE_LT10_PER_100K = "RARE_LT10_PER_100K.csv"
RARE_LT50_PER_100K = "RARE_LT50_PER_100K.csv"

def strip_paren(disease: str) -> str:
    # Replace anything in parentheses (non-greedy match)
    # Autosomal Recessive Polycystic Kidney Disease (ARPKD) -->
    # Autosomal Recessive Polycystic Kidney Disease
    return re.sub(r"\s*\([^)]*\)", "", disease)

def dict_disease_names(disease_csv: Path | str) -> dict:
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

def disease_names(filename_csv) -> Path:
    print(f'reading .... {filename_csv}')
    out = dict_disease_names(filename_csv)
    print(f"{len(out.keys())} disease names")
    return filetool.write_json(out, filetool.resource(f'disease_names_{filename_csv}.json'))


if __name__ == '__main__':
    disease_names(RARE_LT10_PER_100K)
    disease_names(RARE_LT50_PER_100K)
