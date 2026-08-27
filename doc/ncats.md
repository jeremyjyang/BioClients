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

### Inxight Drugs - Stitcher API

* <https://drugs.ncats.io/>
* <https://stitcher.ncats.io/api/>
* <https://github.com/ncats/stitcher>
* <https://academic.oup.com/nar/article/50/D1/D1307/6396888>

```
python3 -m BioClients.ncats.stitcher.Client -h
usage: Client.py [-h] [--i IFILE] [--o OFILE] [--ids IDS] [--query QUERY]
                 [--api_host API_HOST] [--api_base_path API_BASE_PATH] [-v]
                 {get_drug,get_drug_targets,search}

NCATS Inxight Drugs API client

positional arguments:
  {get_drug,get_drug_targets,search}
                        OPERATION

options:
  -h, --help            show this help message and exit
  --i IFILE             Input IDs
  --o OFILE             Output (TSV)
  --ids IDS             Input UNII IDs (comma-separated)
  --query QUERY         Search query.
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

Example UNIIs: 8R78F6L9VO EM8BM710ZC WI4X0X7BPJ 884KT10YB7 2679MF687A
```
