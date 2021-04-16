# `BioClients.medline`

## Medline Plus

* [Medline Plus](https://medlineplus.gov/) | [Medline Plus Web Services](https://medlineplus.gov/about/developers/webservices/)
* [Medline Plus Genetics](https://medlineplus.gov/genetics) | [Medline Plus Genetics API](https://medlineplus.gov/about/developers/geneticsdatafilesapi/)
* [Medline Plus Connect](https://medlineplus.gov/connect/overview.html) | [Medline Plus Connect Web Service](https://medlineplus.gov/connect/service.html)

## Dependencies

* Python package `xmltodict`

## Example commands

```
$ python3 -m BioClients.medline.genetics.Client -h
usage: Client.py [-h] [--i IFILE] [--o OFILE] [--ids IDS] [--api_host API_HOST]
                 [--api_base_path API_BASE_PATH]
                 [--download_host DOWNLOAD_HOST]
                 [--download_base_path DOWNLOAD_BASE_PATH]
                 [--summary_url SUMMARY_URL] [-v]
                 {search,list_conditions,list_genes,get_condition_genes}

MedlinePlus Genetics REST API client

positional arguments:
  {search,list_conditions,list_genes,get_condition_genes}
                        OPERATION (select one)

optional arguments:
  -h, --help            show this help message and exit
  --i IFILE             input term file (one per line)
  --o OFILE             output (TSV)
  --ids IDS             term list (comma-separated)
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  --download_host DOWNLOAD_HOST
  --download_base_path DOWNLOAD_BASE_PATH
  --summary_url SUMMARY_URL
  -v, --verbose

Example conditions: allergic-asthma, alzheimer-disease, parkinson-disease,
rapid-onset-dystonia-parkinsonism, type-1-diabetes, type-2-diabetes
```

```
python3 -m BioClients.medline.genetics.Client list_conditions
python3 -m BioClients.medline.genetics.Client search --ids "Asthma"
python3 -m BioClients.medline.genetics.Client search --ids "Alzheimer"
python3 -m BioClients.medline.genetics.Client get_condition_genes --ids "parkinson-disease"
```
