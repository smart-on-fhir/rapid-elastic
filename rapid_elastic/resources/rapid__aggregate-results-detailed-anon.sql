CREATE EXTERNAL TABLE rapid__aggregate_results_detailed_anon (
    subject_ref     string,
    document_ref    string,
    disease_alias   string,
    asserted        string,
    span            boolean,
    human           string
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://cumulus-analytics/andy/rapid__aggregate_results_detailed_april22_anon/'
TBLPROPERTIES ("skip.header.line.count"="1")
;