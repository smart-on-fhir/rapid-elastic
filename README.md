# rapid-elastic

### Disease Synonyms Curation
* Disease names and synonyms were **HUMAN expert curated** and assisted via ChatGPT with additional checks within NLM GeneReviews, OrphaNet, and Google searches.
* [disease_names_expanded.json](rapid_elastic/resources/disease_names_expanded.json) is pre-built and recommended for use without modification.
* [disease_names.py](rapid_elastic/disease_names.py) assists curation if changes need to be made: read spreadsheet CSV, write disease names JSON, recommend GPT4 prompts, find duplicates, and merges curated JSON.

### Quickstart

1. configure ENV variables query your Elasticsearch server (within your **VPN/firewall**) 
   1. `ELASTIC_HOST` : default http://localhost:9200
   2. `ELASTIC_USER` : basic auth
   3. `ELASTIC_PASS` : basic auth

2. pipx install rapid-elastic

3. rapid-elastic

### Elasticsearch server 
Read the [server setup docs](docs/server-setup.md).

### KQL (Kibana Query Language) 
* By default, synonyms used to match any "exact phrase" in the note. 
* see `kql_syntax.py` for alternate methods of building Elasticsearch queries.

### Each Elasticsearch hit is saved to "output" folder 
 * `subject_ref`           (FHIR Patient.id)
 * `encounter_ref`         (FHIR Encounter.id)
 * `document_ref`          (FHIR DocumentReference.id) 
 * `group_name`            (optional)
 * `document_title`        (optional)


### SQL Athena
#### SQL tables are generated from spreadsheet CSV files
  * `disease_name`
  * `orpha_code` 
  * `icd10_code`

#### FHIR resources are referenced using 
 * `subject_ref`           (FHIR Patient.id)
 * `encounter_ref`         (FHIR Encounter.id)
 * `documentreference_ref` (FHIR DocumentReference.id) 
  
#### FHIR Condition.code is selected using 
* `icd10_code` 
 

