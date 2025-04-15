create table rapid__labelstudio_init as
with high_confidence as
(
    select distinct *
    from rapid__match_compare
    where   hit_icd10
    and     hit_notes
    and     hit_sample_patients
    and     hit_sample_notes
    and     disease_alias IN (
            'noonan_syndrome',
            'carbamoyl_phosphate_synthetase_i_deficiency',
            'beckwith_wiedemann_syndrome',
            'pompe_disease',
            'angelman_syndrome')
)
select
    high_confidence.disease_alias,
    high_confidence.subject_ref,
    high_confidence.document_ref,
    sample_notes.group_name,
    sample_notes.encounter_ref,
    sample_notes.document_title
from
    high_confidence,
    rapid__match_notes_sample_notes as sample_notes
where
    high_confidence.document_ref = sample_notes.document_ref
order by subject_ref, encounter_ref, document_ref
;