create table rapid__icd10_str as
WITH distinct_codes AS (
    SELECT DISTINCT disease_alias, icd10_code, length(icd10_code) as digits
    FROM rapid__codeset
    order by disease_alias, digits
),
less_specific as
(
    select  A.disease_alias, A.icd10_code, A.digits
    from    distinct_codes A, distinct_codes B
    where   A.disease_alias = B.disease_alias
    and     A.icd10_code !=  B.icd10_code
    and     A.digits < B.digits
    order by A.disease_alias, A.digits
),
more_specific as
(
    select * from distinct_codes where disease_alias not in (select disease_alias from less_specific)
),
less_and_more as
(
    select disease_alias, icd10_code || '*' as icd10_code from less_specific
    union
    select disease_alias, icd10_code || '*' as icd10_code from more_specific
),
aggregated as
(
    SELECT disease_alias,
           array_join(array_sort(array_agg(icd10_code)), ', ') AS icd10_list
    FROM less_and_more
    GROUP BY disease_alias
)
select * from aggregated
order by disease_alias;