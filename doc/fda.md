# `BioClients.fda`

## FDA

OpenFDA Adverse Event Reports (FAERS) REST API client.

* <https://www.fda.gov/drugs/drug-approvals-and-databases/fda-adverse-event-reporting-system-faers-database>
* <https://open.fda.gov/apis/>
* <https://open.fda.gov/apis/drug/event/how-to-use-the-endpoint/>
* <https://api.fda.gov/drug/event.json?search=patient.drug.openfda.pharm_class_epc:"nonsteroidal+anti-inflammatory+drug"&count=patient.reaction.reactionmeddrapt.exact>

```
$ python -m BioClients.fda.aer.Client -h
usage: Client.py [-h] [--o OFILE] [--drug_class DRUG_CLASS]
                 [--drug_ind DRUG_IND] [--drug_unii DRUG_UNII]
                 [--drug_ndc DRUG_NDC] [--drug_spl DRUG_SPL]
                 [--serious SERIOUS] [--fatal FATAL] [--tfrom TFROM]
                 [--tto TTO] [--rawquery RAWQUERY] [--nmax NMAX]
                 [--api_host API_HOST] [--api_base_path API_BASE_PATH]
                 [--param_file PARAM_FILE] [--api_key API_KEY] [-v]
                 {search,get_counts,info,list_fields}

OpenFDA Adverse Event Reports client

positional arguments:
  {search,get_counts,info,list_fields}
                        operation

options:
  -h, --help            show this help message and exit
  --o OFILE             output (TSV)
  --drug_class DRUG_CLASS
                        search: EPC pharmacologic class
  --drug_ind DRUG_IND   search: drug indication
  --drug_unii DRUG_UNII
                        search: drug ID UNII
  --drug_ndc DRUG_NDC   search: drug ID NDC
  --drug_spl DRUG_SPL   search: drug ID SPL
  --serious SERIOUS     search: serious adverse events
  --fatal FATAL         search: fatal adverse events (seriousnessdeath)
  --tfrom TFROM         time-from (received by FDA) (YYYYMMDD)
  --tto TTO             time-to (received by FDA) (YYYYMMDD)
  --rawquery RAWQUERY
  --nmax NMAX           max returned records
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  --param_file PARAM_FILE
  --api_key API_KEY
  -v, --verbose

Example UNII: 786Z46389E
```
