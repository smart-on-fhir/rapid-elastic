create TABLE rapid__match_notes_sample_notes AS
select  distinct notes.*
from    rapid__match_notes as notes,
        rapid__match_notes_sample_patients as patients
where   notes.disease_alias = patients.disease_alias
and     notes.subject_ref = patients.subject_ref
;