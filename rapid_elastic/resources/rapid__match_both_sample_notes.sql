create TABLE rapid__match_both_sample_notes AS
select  distinct rapid__match_notes.*
from    rapid__match_notes,
        rapid__match_notes_sample_patients,
        rapid__match_icd10_sample_patients
where   rapid__match_notes.disease_alias = rapid__match_notes_sample_patients.disease_alias
and     rapid__match_notes.subject_ref   = rapid__match_notes_sample_patients.subject_ref
and     rapid__match_notes.disease_alias = rapid__match_icd10_sample_patients.disease_alias
and     rapid__match_notes.subject_ref   = rapid__match_icd10_sample_patients.subject_ref
;