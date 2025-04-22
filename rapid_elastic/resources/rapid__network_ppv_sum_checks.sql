create table rapid__network_ppv_sum_checks as
WITH
disease_icd10 as
(
    SELECT disease_alias,
            array_join(array_sort(array_distinct(array_agg(icd10_code))), ', ') AS icd10_list
    FROM rapid__match_icd10
    group by disease_alias
),
ppv_percent as
(
    select  ppv,
            cast(round(ppv*100, 1) as varchar) as ppv_string,
            hit_icd10_notes,
            hit_notes_only,
            disease_alias
    from    rapid__ppv
),
check_list as
(
    select      cnt_total_ppv > (15*1000) as warn_15k,
                cnt_total_ppv > (7500)    as warn_7500,
                round(cnt_total_ppv / large_prev, 2) as ratio_large_prev,
                round(cnt_notes_only_ppv / cnt_icd10_notes_ppv, 2) as ratio_icd10_notes,
                rapid__network_ppv_sum.*,
                disease_icd10.icd10_list
    from        disease_icd10,
                rapid__network_ppv_sum
    where       rapid__network_ppv_sum.disease_alias =
                disease_icd10.disease_alias
    order by    disease_icd10.disease_alias
),
check_bool as
(
    select      warn_15k or (ratio_large_prev > 10) or (ratio_icd10_notes > 100) as failed,
                check_list.*
    from        check_list
),
n_case_icd_nlp as
(
    select  distinct
            check_list.disease_alias,
            cnt_icd10_notes_ppv,
            concat('n_case_icd_nlp: ',
                    'Patients with both ICD code ',
                    check_list.icd10_list,
                    ' and note mentions (PPV_icd_nlp=',
                    ppv_percent.ppv_string,
                    '% confirmed out of ',
                    cast(cnt_icd10_notes as varchar),
                    ' potential cases).') as report_text
    from        check_list,
                ppv_percent
    where       check_list.disease_alias = ppv_percent.disease_alias
    and         ppv_percent.hit_icd10_notes
),
n_case_notes_only as
(
    select  distinct
            check_list.disease_alias,
            cnt_icd10_notes_ppv,
            concat('n_case_nlp_only:    ',
                    'Patients with notes mentions only ',
                    '(PPV_icd_nlp=',
                    ppv_percent.ppv_string,
                    '% confirmed out of ',
                    cast(cnt_notes_only as varchar),
                    ' potential cases).') as report_text
    from        check_list,
                ppv_percent
    where       check_list.disease_alias = ppv_percent.disease_alias
    and         ppv_percent.hit_notes_only
)
select  check_bool.disease_alias,
        case
        when    not check_bool.failed
        then    check_bool.cnt_total_ppv
        else    check_bool.cnt_icd10_notes_ppv end as column_J,
        case
        when    not check_bool.failed
        then    concat('n_total= (n_case_icd_nlp + n_case_nlp_only).    ',
                        n_case_icd_nlp.report_text,
                        '   ',
                        n_case_notes_only.report_text)
        else    concat('n_total= ',
                        n_case_icd_nlp.report_text)
        end     as report_text
from check_bool
left join   n_case_icd_nlp      on check_bool.disease_alias = n_case_icd_nlp.disease_alias
left join   n_case_notes_only   on check_bool.disease_alias = n_case_notes_only.disease_alias
order by disease_alias


