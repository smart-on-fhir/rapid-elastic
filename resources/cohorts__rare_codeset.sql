create TABLE cohorts__rare_codeset AS 
select distinct 'codeset_unique_lt10_per_100k' as source_csv, * from cohorts__rare_codeset_unique_lt10_per_100k
 UNION 
select distinct 'codeset_unique_lt50_per_100k' as source_csv, * from cohorts__rare_codeset_unique_lt50_per_100k
 UNION 
select distinct 'codeset_broad_lt10_per_100k' as source_csv, * from cohorts__rare_codeset_broad_lt10_per_100k
 UNION 
select distinct 'codeset_broad_lt50_per_100k' as source_csv, * from cohorts__rare_codeset_broad_lt50_per_100k