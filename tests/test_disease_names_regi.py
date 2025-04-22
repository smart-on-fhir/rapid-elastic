import unittest
from collections import Counter
from rapid_elastic import filetool
from rapid_elastic import naming
from rapid_elastic import disease_names

class TestDiseaseNamesREGI(unittest.TestCase):

    def test_extract_regi(self):
        file_raw = filetool.resource('rapid__site_count_regi.rrf')
        for line in filetool.read_text(file_raw).splitlines():
            print(line)

    def ignore_test(self):
        known = disease_names.list_disease_alias()
        site_raw = DISEASE_NAMES.splitlines()
        site_raw = [d for d in site_raw if (d is not None and len(d) > 1)]
        site_alias = [naming.name_table_alias(d) for d in site_raw]

        # for d in site_alias:
        #     print(d)

        duplicates = [item for item, count in Counter(site_alias).items() if count > 1]
        print(duplicates)

        # {'glutaric_aciduria_type_1', 'sanfilippo_syndrome', 'neuronal_ceroid_lipofuscinosis', 'hurler_syndrome'}
        self.assertEqual(set(), set(known).difference(set(site_alias)))
        self.assertEqual(set(), set(site_alias).difference(set(known)))



###############################################################################

DISEASE_NAMES = """
Beta thalassemia major (Cooley's anemia)
Fanconi anemia
Shwachman-Diamond syndrome
Diamond-Blackfan anemia
Hemophilia A 
Chronic granulomatous disease (CGD)
Familial hemophagocytic lymphohistiocytosis (HLH)
X-linked agammaglobulinemia (Bruton)
Severe combined immunodeficiency (SCID)
Wiskott-Aldrich syndrome
22q11.2 deletion syndrome (DiGeorge)
Pseudohypoparathyroidism type 1A (albright hereditary osteodystrophy)
Isolated growth hormone deficiency (IGHD)
Barth syndrome (3-methylglutaconic acidurea type 2)
Medium-chain acyl-CoA dehydrogenase deficiency (MCADD)
X-linked adrenoleukodystrophy (X-ALD)
Cystinuria
Cystinosis (nephropathic)
Carbamoyl phosphate synthetase I deficiency (CPS1)
Glutaric aciduria type 1 (GA1)
Pompe disease (Glycogen storage type1)
Transaldolase deficiency
Neuronal ceroid lipofuscinosis (Batten disease) 
Hurler syndrome (Mucopolysaccharidosis type1)
Sanfilippo syndrome (Mucopolysaccharidosis type III )
Salla disease (free sialic acid storage)
COG8-Congenital Disorders of Glycosylation
Wilson disease
Menkes disease
Cystic fibrosis (CF)
Alpha-1 antitrypsin deficiency
Rett syndrome
Friedreich ataxia (FRDA)
Ataxia-telangiectasia (AT)
Spinal muscular atrophy (SMA)
Opsoclonus-myoclonus syndrome
Leigh syndrome (subacute necrotizing encephalopathy)
Lennox-Gastaut syndrome (LGS)
Dravet syndrome
Juvenile myoclonic epilepsy (JME)
Hereditary neuropathy with liability to pressure palsies (HNPP)
Duchenne muscular dystrophy (DMD)
Steinert myotonic dystrophy
Ullrich congenital muscular dystrophy
Neurodegeneration-spasticity-cerebellar atrophy-cortical visual impairment syndrome (NESCAV syndrome)
Usher syndrome
Leber congenital amaurosis (LCA)
Stargardt disease (juvenile macular dystrophy)
Achromatopsia (complete congenital color blindness)
Pediatric pulmonary hypertension (PAH)
Hereditary hemorrhagic telangiectasia
Pediatric bronchiectasis (non-CF)
Childhood interstitial lung disease (chILD)
Surfactant Protein Deficiencies
Chronic intestinal pseudo-obstruction (CIPO)
Systemic-onset juvenile idiopathic arthritis (Still's disease)
Gitelman syndrome
Congenital hyperinsulinism
Aicardi syndrome
Joubert syndrome
FLNA-related X-linked myxomatous valvular dysplasia
Primary ciliary dyskinesia (PCD)
Hirschsprung disease
Biliary atresia
Alagille Syndrome
Autosomal recessive polycystic kidney disease (ARPKD)
Nephronophthisis (juvenile)
Cleidocranial dysplasia
Treacher Collins syndrome
Pseudoachondroplasia
Melnick-Needles osteodysplasty
Osteogenesis imperfecta (OI)
McCune Albright syndrome (fibrous dysplasia)
Ehlers-Danlos syndrome (Classical type)
Epidermolysis bullosa (EB)
Neurofibromatosis type 1 (NF1)
Tuberous sclerosis complex (TSC)
Sturge-Weber syndrome
Cowden syndrome/multiple hamartoma syndrome
Moebius syndrome
Stickler syndrome
Pitt-Hopkins syndrome
Otopalataldigital syndrome type 1
Otopalataldigital syndrome type 2
Noonan syndrome
Smith-Lemli-Opitz syndrome (SLOS)
Prader-Willi syndrome
Russell-Silver syndrome
VACTERL/VATER association
Rubinstein-Taybi syndrome
Beckwith-Wiedemann syndrome
Marfan syndrome
Loeys-Dietz syndrome
Sensenbrenner syndrome (cranioectodermal dysplasia)
Arterial Tortuosity Syndrome
CHARGE syndrome
Bannayan-Riley-Ruvalcaba syndrome
Alport syndrome
Bardet-Biedl syndrome (BBS)
Heterotaxy syndrome (situs ambiguus)
Kabuki syndrome
1p36 deletion syndrome
16p11.2 microdeletion syndrome (? distal or proximal)
Smith-Magenis syndrome (17p11.2 microdeletion syndrome)
Angelman syndrome
Williams syndrome
Fragile X syndrome
"""