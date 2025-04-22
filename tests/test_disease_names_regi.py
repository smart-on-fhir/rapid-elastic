import unittest
from collections import Counter
from rapid_elastic import filetool
from rapid_elastic import naming
from rapid_elastic import disease_names

class TestDiseaseNamesREGI(unittest.TestCase):

        # cnt_icd10           int,
        # cnt_icd10_notes	    int,
        # cnt_notes_only	    int,
        # disease_alias       string

    def old_____test_extract_regi_wrong_column(self):
        pass
        # file_raw = filetool.resource('rapid__site_count_regi_wrong_column.csv')
        # out = list()
        # for line in filetool.read_text(file_raw).splitlines():
        #     disease_name, icd10_code, patient_count = line.split(',')
        #     disease_alias = naming.name_table_alias(disease_name)
        #     out.append(f'{patient_count},0,0,{disease_alias}')
        # out = '\n'.join(out)
        # filetool.write_text(out, filetool.resource('rapid__site_count_regi_wrong_column.csv'))

    def test_runonce_extract_regi_etl(self):
        file_raw = filetool.resource('rapid__site_count_regi_etl.rrf')
        out = list()
        for line in filetool.read_text(file_raw).splitlines():
            if not line.startswith('disease_name'):
                disease_name, cnt_icd10_notes, cnt_icd10, cnt_notes_only, _ignore5, _ignore6, _ignore7 = line.split('|')
                if cnt_icd10_notes == 'less than 10':
                    cnt_icd10_notes = 5     # pick a point in the middle as an estimator
                if not cnt_icd10_notes:
                    cnt_icd10_notes = 0
                if not cnt_icd10:
                    cnt_icd10 = 0
                if not cnt_notes_only:
                    cnt_notes_only = 0

                cnt_icd10 = int(cnt_icd10) + int(cnt_icd10_notes)
                disease_alias = naming.name_table_alias(disease_name)
                out.append(f'{cnt_icd10},{cnt_icd10_notes},{cnt_notes_only},{disease_alias}')
        out = '\n'.join(out)
        filetool.write_text(out, filetool.resource('rapid__site_count_regi.csv'))

    def test_names(self):
        known = disease_names.list_disease_alias()
        site_raw = DISEASE_NAMES.splitlines()
        site_raw = [d for d in site_raw if (d is not None and len(d) > 1)]
        site_alias = [naming.name_table_alias(d) for d in site_raw]

        # for d in site_alias:
        #     print(d)

        duplicates = [item for item, count in Counter(site_alias).items() if count > 1]
        print(duplicates)

        print(len(site_alias), ' len(site_alias)')
        diff1 = set(known).difference(set(site_alias))
        diff2 = set(site_alias).difference(set(known))

        print(len(diff1))
        print(diff1)
        print(diff2)

        # {'glutaric_aciduria_type_1', 'sanfilippo_syndrome', 'neuronal_ceroid_lipofuscinosis', 'hurler_syndrome'}
        self.assertEqual(set(), diff1)
        self.assertEqual(set(), diff2)



###############################################################################

DISEASE_NAMES = """
16p11_2_microdeletion_syndrome
1p36_deletion_syndrome
achromatopsia
aicardi_syndrome
alagille_syndrome
angelman_syndrome
ataxia_telangiectasia
barth_syndrome
beta_thalassemia_major
biliary_atresia
carbamoyl_phosphate_synthetase_i_deficiency
childhood_interstitial_lung_disease
chronic_granulomatous_disease
chronic_intestinal_pseudo_obstruction
cleidocranial_dysplasia
cog8_congenital_disorders_of_glycosylation
congenital_hyperinsulinism
cowden_syndrome_multiple_hamartoma_syndrome
cystic_fibrosis
cystinosis
cystinuria
diamond_blackfan_anemia
dravet_syndrome
duchenne_muscular_dystrophy
epidermolysis_bullosa
familial_hemophagocytic_lymphohistiocytosis
fanconi_anemia
flna_related_x_linked_myxomatous_valvular_dysplasia
friedreich_ataxia
gitelman_syndrome
glutaric_aciduria_type_1
hereditary_hemorrhagic_telangiectasia
hereditary_neuropathy_with_liability_to_pressure_palsies
heterotaxy_syndrome
isolated_growth_hormone_deficiency
joubert_syndrome
juvenile_myoclonic_epilepsy
kabuki_syndrome
leigh_syndrome
lennox_gastaut_syndrome
mccune_albright_syndrome
melnick_needles_osteodysplasty
menkes_disease
hurler_syndrome
nephronophthisis
neuronal_ceroid_lipofuscinosis
opsoclonus_myoclonus_syndrome
osteogenesis_imperfecta
pediatric_bronchiectasis
pediatric_pulmonary_hypertension
pompe_disease
primary_ciliary_dyskinesia
pseudoachondroplasia
pseudohypoparathyroidism_type_1a
rubinstein_taybi_syndrome
salla_disease
sensenbrenner_syndrome
severe_combined_immunodeficiency
shwachman_diamond_syndrome
smith_magenis_syndrome
spinal_muscular_atrophy
steinert_myotonic_dystrophy
sturge_weber_syndrome
surfactant_protein_deficiencies
systemic_onset_juvenile_idiopathic_arthritis
transaldolase_deficiency
treacher_collins_syndrome
ullrich_congenital_muscular_dystrophy
vacterl_vater_association
wilson_disease
wiskott_aldrich_syndrome
x_linked_agammaglobulinemia
"""