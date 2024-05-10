# `BioClients.clinicaltrials`

##  ClinicalTrials.gov

NIH NLM ClinicalTrials.gov REST API v2 client

  * <https://clinicaltrials.gov/>
  * <https://clinicaltrials.gov/data-api/about-api>
  * <https://clinicaltrials.gov/data-api/api>
  * <https://clinicaltrials.gov/find-studies/constructing-complex-search-queries>

```
$ python3 -m BioClients.clinicaltrials.Client -h
usage: Client.py [-h] [--i IFILE] [--o OFILE] [--ids IDS]
                 [--query_cond QUERY_COND] [--query_term QUERY_TERM]
                 [--api_host API_HOST] [--api_base_path API_BASE_PATH] [-v]
                 {version,list_study_fields,list_search_areas,search_studies,get_studies}

ClinicalTrials.gov API client

positional arguments:
  {version,list_study_fields,list_search_areas,search_studies,get_studies}
                        OPERATION

options:
  -h, --help            show this help message and exit
  --i IFILE             Input NCT_IDs
  --o OFILE             Output (TSV)
  --ids IDS             Input NCT_IDs (comma-separated)
  --query_cond QUERY_COND
                        Search query condition
  --query_term QUERY_TERM
                        Search query term
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

See: https://clinicaltrials.gov/data-api/about-api,
https://clinicaltrials.gov/data-api/api, https://clinicaltrials.gov/find-
studies/constructing-complex-search-queries
```
