import kql_syntax
import pipeline

DISEASE_SEARCH = {
    "Phenylketonuria (PKU)": [
        "phenylketonuria",
        "phenylalanine hydroxylase deficiency",
        "hyperphenylalaninemia"],
    "Primary Congenital Hypothyroidism": [
        "Congenital Hypothyroidism",
        "Neonatal Hypothyroidism",
        "Thyroid Dysgenesis",
        "Congenital Primary Hypothyroidism",
        "Congenital Thyroid Hormone Deficiency"],
    "Maple Syrup Urine Disease (MSUD)": [
        "Maple Syrup Urine Disease",
        "Maple Syrup Urine Syndrome",
        "Branched-Chain Ketoaciduria",
        "Branched Chain Ketoaciduria"],
    "Classic Galactosemia (Type I)": [
        "Classic Galactosemia",
        "Galactosemia Type I",
        "GALT Deficiency",
        "Galactose-1-Phosphate Uridyltransferase Deficiency",
        "Galactose 1-Phosphate Uridyltransferase Deficiency"],
    "Alpha-1 Antitrypsin Deficiency (AATD)" : [
        "Alpha-1 Antitrypsin Deficiency",
        "Alpha 1 Antitrypsin Deficiency",
        "AAT Deficiency",
        "A1AT Deficiency",
        "Alpha-1 Protease Inhibitor Deficiency",
        "Alpha-1 PI Deficiency"],
    "Medium-Chain Acyl-CoA Dehydrogenase Deficiency": [
        "Medium-Chain Acyl-CoA Dehydrogenase Deficiency",
        "Medium Chain Acyl CoA Dehydrogenase Deficiency",
        "Medium-Chain Acyl-Coenzyme A Dehydrogenase Deficiency",
        "ACADM Deficiency",
        "MCAD Deficiency",
        "MCADD"],
    "Congenital Adrenal Hyperplasia (21-hydroxylase)": [
        "Congenital Adrenal Hyperplasia due to 21-Hydroxylase Deficiency",
        "CAH due to 21-Hydroxylase Deficiency",
        "21-Hydroxylase Deficiency",
        "Classic Congenital Adrenal Hyperplasia",
        "Congenital Adrenal Hyperplasia"],
    "cystic fibrosis (CF)": ["cystic fibrosis"]
}