CREATE EXTERNAL TABLE rapid__site_count_uthsc (
    cnt_icd10           int,
    cnt_icd10_notes	    int,
    cnt_notes_only	    int,
    disease_alias       string
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://cumulus-analytics/andy/'
TBLPROPERTIES ("skip.header.line.count"="1")
;