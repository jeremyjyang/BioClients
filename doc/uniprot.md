# `BioClients.uniprot`

## UniProt

Access to Uniprot REST API.

UniprotKB = Uniprot Knowledge Base

* <https://www.uniprot.org>
* <https://www.uniprot.org/help/api>
* <https://www.uniprot.org/uniprot>

```
$ python3 -m BioClients.uniprot.Client -h
usage: Client.py [-h] [--ids IDS] [--i IFILE] [--o OFILE]
                 [--api_host API_HOST] [--api_base_path API_BASE_PATH] [-v]
                 {getData,listData}

Uniprot query client; get data for specified IDs

positional arguments:
  {getData,listData}    operation

options:
  -h, --help            show this help message and exit
  --ids IDS             UniProt IDs, comma-separated (ex: Q14790)
  --i IFILE             input file, UniProt IDs
  --o OFILE             output (TSV)
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose
```

```
python3 -m BioClients.uniprot.Client getData --ids Q14790
```
