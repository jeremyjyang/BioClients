# `BioClients.gwascatalog`

## GWAS Catalog

GWAS Catalog REST API client.

__Version 1:__
* <https://www.ebi.ac.uk/gwas/docs/api>
* <https://www.ebi.ac.uk/gwas/rest/api>
* <https://www.ebi.ac.uk/gwas/rest/docs/api>
* <https://www.ebi.ac.uk/gwas/rest/docs/sample-scripts>

__Version 2:__
 - <https://www.ebi.ac.uk/gwas/rest/api/v2/docs>
 - _"GWAS RESTful API V2 has been released with various enhancements & improvements over GWAS RESTful API V1. V1 is deprecated and will be retired no later than May 2026."_
 - <https://www.ebi.ac.uk/gwas/rest/api/v2/docs/reference>


## Example commands

```
python3 -m BioClients.gwascatalog.Client list_studies_v2 --o gwascatalog_studies.tsv
```

```
python3 -m BioClients.gwascatalog.Client get_studyAssociations_v2 --ids "GCST004364,GCST000227"
```

```
python3 -m BioClients.gwascatalog.Client get_snps_v2 --ids "rs6085920,rs2273833,rs6684514,rs144991356"
```

```
python -m BioClients.gwascatalog.Client -h
usage: Client.py [-h] [--ids IDS]
                 [--searchtype {pubmedmid,gcst,efotrait,efouri,accessionid,rs}]
                 [--i IFILE] [--o OFILE] [--skip SKIP] [--nmax NMAX] [--api_host API_HOST]
                 [--api_base_path API_BASE_PATH] [--api_base_path_v2 API_BASE_PATH_V2]
                 [-v] [-q]
                 {get_metadata_v2,list_studies,list_studies_v2,get_studyAssociations,get_studyAssociations_v2,get_snps,get_snps_v2,search_studies,search_studies_v2}

GWAS Catalog REST API (V1|V2) client

positional arguments:
  {get_metadata_v2,list_studies,list_studies_v2,get_studyAssociations,get_studyAssociations_v2,get_snps,get_snps_v2,search_studies,search_studies_v2}
                        operation

options:
  -h, --help            show this help message and exit
  --ids IDS             IDs, comma-separated
  --searchtype {pubmedmid,gcst,efotrait,efouri,accessionid,rs}
                        ID type
  --i IFILE             input file, IDs
  --o OFILE             output (TSV)
  --skip SKIP
  --nmax NMAX
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  --api_base_path_v2 API_BASE_PATH_V2
  -v, --verbose
  -q, --quiet

Example PMIDs: 28530673; Example GCSTs: GCST004364, GCST000227; Example EFOIDs:
EFO_0004232; Example SNPIDs: rs6085920, rs2273833, rs6684514, rs144991356
```
