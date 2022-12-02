# `BioClients.ncats`

## NIH NCATS

Tools for obtaining and processing data from NIH NCATS resources.

* <https://ncats.nih.gov/>

### Global Substance Registration System (GSRS)

* <https://ncats.nih.gov/expertise/preclinical/gsrs>
* <https://gsrs.ncats.nih.gov/>
* <https://gsrs.ncats.nih.gov/#/api>

Examples:

```
$ python -m BioClients.ncats.gsrs.Client -h
usage: Client.py [-h] [--i IFILE] [--o OFILE] [--ids IDS] [--query QUERY]
                 [--api_host API_HOST] [--api_base_path API_BASE_PATH] [-v]
                 {list_vocabularies,list_substances,search,get_substance,get_substance_names}

NCATS Global Substance Registration System (GSRS) client

positional arguments:
  {list_vocabularies,list_substances,search,get_substance,get_substance_names}
                        OPERATION

options:
  -h, --help            show this help message and exit
  --i IFILE             Input IDs
  --o OFILE             Output (TSV)
  --ids IDS             Input IDs (comma-separated)
  --query QUERY         Search query.
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

Example search queries: IBUPRO ASPIRIN OXYTOCIN OXYTO* ASPIRIN AND ESTER COCN
C=1CC=CC=C1C(=O)O
```

