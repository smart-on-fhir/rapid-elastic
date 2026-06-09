import unittest
from collections import Counter
from rapid_elastic import filetool
from rapid_elastic import naming
from rapid_elastic import disease_names

class TestDiseaseNamesSUM(unittest.TestCase):

    def test(self):
        known = disease_names.list_disease_alias()
        site_raw = DISEASE_NAMES.splitlines()
        site_raw = [d for d in site_raw if (d is not None and len(d) > 1)]
        site_alias = [naming.name_table_alias(d) for d in site_raw]

        for d in site_alias:
            print(d)

        duplicates = [item for item, count in Counter(site_alias).items() if count > 1]
        print(duplicates)

        # {'glutaric_aciduria_type_1', 'sanfilippo_syndrome', 'neuronal_ceroid_lipofuscinosis', 'hurler_syndrome'}
        self.assertEqual(set(), set(known).difference(set(site_alias)))
        self.assertEqual(set(), set(site_alias).difference(set(known)))

###############################################################################

DISEASE_NAMES = """
Noonan syndrome
Williams syndrome
22q11.2 deletion syndrome (DiGeorge)
Heterotaxy syndrome (situs ambiguus)
Marfan syndrome
Arterial Tortuosity Syndrome
Alagille Syndrome
Treacher Collins syndrome
Moebius syndrome
Epidermolysis bullosa (EB)
Medium-chain acyl-CoA dehydrogenase deficiency (MCADD)
Carbamoyl phosphate synthetase I deficiency (CPS1)
Glutaric aciduria type 1 (GA1)
Salla disease (free sialic acid storage)
Wilson disease
Menkes disease
X-linked adrenoleukodystrophy (X-ALD)
Leigh syndrome (subacute necrotizing encephalopathy)
Pompe disease (Glycogen storage type1)
Hurler syndrome (Mucopolysaccharidosis type1)
Sanfilippo syndrome (Mucopolysaccharidosis type III)
Smith-Lemli-Opitz syndrome (SLOS)
Cystinosis (nephropathic)
Isolated growth hormone deficiency (IGHD)
Beckwith-Wiedemann syndrome
Prader-Willi syndrome
Russell-Silver syndrome
Congenital hyperinsulinism
Hirschsprung disease
Biliary atresia
Shwachman-Diamond syndrome
Alpha-1 antitrypsin deficiency
Chronic intestinal pseudo-obstruction (CIPO)
Fanconi anemia
Diamond-Blackfan anemia
Hemophilia A 
Beta thalassemia major (Cooley's anemia)
Chronic granulomatous disease (CGD)
Wiskott-Aldrich syndrome
X-linked agammaglobulinemia (Bruton)
Familial hemophagocytic lymphohistiocytosis (HLH)
Severe combined immunodeficiency (SCID)
CHARGE syndrome
VACTERL/VATER association
Bardet-Biedl syndrome (BBS)
Stickler syndrome
Sensenbrenner syndrome (cranioectodermal dysplasia)
Pseudoachondroplasia
Osteogenesis imperfecta (OI)
Ehlers-Danlos syndrome (Classical type)
Ullrich congenital muscular dystrophy
Cleidocranial dysplasia
Pitt-Hopkins syndrome
Rett syndrome
Angelman syndrome
Dravet syndrome
Lennox-Gastaut syndrome (LGS)
Juvenile myoclonic epilepsy (JME)
1p36 deletion syndrome
16p11.2 microdeletion syndrome (? distal or proximal)
Kabuki syndrome
Tuberous sclerosis complex (TSC)
Neurofibromatosis type 1 (NF1)
Friedreich ataxia (FRDA)
Ataxia-telangiectasia (AT)
Spinal muscular atrophy (SMA)
Duchenne muscular dystrophy (DMD)
Sturge-Weber syndrome
Hereditary neuropathy with liability to pressure palsies (HNPP)
Aicardi syndrome
Neuronal ceroid lipofuscinosis (Batten disease)
Fragile X syndrome
Joubert syndrome
COG8-Congenital Disorders of Glycosylation
Transaldolase deficiency
Stargardt disease (juvenile macular dystrophy)
Usher syndrome
Leber congenital amaurosis (LCA)
Achromatopsia (complete congenital color blindness)
Primary ciliary dyskinesia (PCD)
Cystic fibrosis (CF)
Pediatric bronchiectasis (non-CF)
Childhood interstitial lung disease (chILD)
Pediatric pulmonary hypertension (PAH)
Surfactant Protein Deficiencies
Alport syndrome
Autosomal recessive polycystic kidney disease (ARPKD)
Nephronophthisis (juvenile)
Gitelman syndrome
Cystinuria
Systemic-onset juvenile idiopathic arthritis (Still's disease)
Opsoclonus-myoclonus syndrome
Neurodegeneration-spasticity-cerebellar atrophy-cortical visual impairment syndrome (NESCAV syndrome)
Hereditary hemorrhagic telangiectasia
Loeys-Dietz syndrome
Pseudohypoparathyroidism type 1A (albright hereditary osteodystrophy)
McCune Albright syndrome (fibrous dysplasia)
FLNA-related X-linked myxomatous valvular dysplasia
Melnick-Needles osteodysplasty
Otopalataldigital syndrome type 1
Otopalataldigital syndrome type 2
Bannayan-Riley-Ruvalcaba syndrome
Cowden syndrome/multiple hamartoma syndrome
Steinert myotonic dystrophy
Smith-Magenis syndrome (17p11.2 microdeletion syndrome)
Barth syndrome (3-methylglutaconic acidurea type 2)
Rubinstein-Taybi syndrome
"""