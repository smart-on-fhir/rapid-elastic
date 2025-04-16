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


## SQL Tables

SQL files are loaded in order 1-6 to produce the result table **rapid__match_compare** 

### ICD10 diagnosis
1. **rapid__codeset**.sql
  * `disease_name`  (human label)
  * `disease_alias` (machine label)
  * `orpha_code`    (Orphanet code) 
  * `icd10_code`    (ICD10 code)

2. **rapid__match_icd10**.sql
  * `disease_name`  (human label)
  * `disease_alias` (machine label)
  * `orpha_code`    (Orphanet code) 
  * `icd10_code`    (ICD10 code)
  * `subject_ref`           (FHIR Patient.id)
  * `encounter_ref`         (FHIR Encounter.id)
  * FHIR condition (optional metadata) 

### NOTES search results
3. **rapid__match_notes**.sql
  * `disease_alias` (machine label)
  * `subject_ref`   (FHIR Patient.id)
  * `document_ref`  (FHIR DocumentReference.id)
  * `encounter_ref` (FHIR Encounter.id)
  * `document_title` (optional)
  * `group_name` (optional)
 
#### SAMPLE tables
Select up to 100 patients per disease into these tables. 

4. **rapid__match_notes_sample_patients**.sql
  * `disease_alias` 
  * `subject_ref`   

5. **rapid__match_notes_sample_notes**.sql
  * `disease_alias` 
  * `subject_ref`   
  * `document_ref`  
  * `encounter_ref` 
  * `document_title` (optional)
  * `group_name` (optional)

#### COMPARE results tables 

6. **rapid__match_compare**.sql
  * `disease_alias`
  * `hit_icd10` (matched ICD10-10)
  * `hit_notes` (matched note search)
  * `hit_sample_patients` (in sample of selected patients)
  * `hit_sample_notes` (in sample of selected patient notes)
  * `icd10_code` (match result if hit_icd10=True)
  * `document_ref`
  * `subject_ref`