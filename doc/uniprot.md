# `BioClients.uniprot`

## UniProt

Access to Uniprot REST API.

UniprotKB = Uniprot Knowledge Base

* <https://www.uniprot.org>
* <https://www.uniprot.org/help/api>
* <https://www.uniprot.org/api-documentation/uniprotkb>

```
$ python -m BioClients.uniprot.Client -h
usage: Client.py [-h] [--ids IDS] [--i IFILE] [--o OFILE] [--api_host API_HOST] [--api_base_path API_BASE_PATH] [-v] {getData,getNames,getFunctions,listData}

Uniprot query client; get data for specified IDs

positional arguments:
  {getData,getNames,getFunctions,listData}
                        operation

options:
  -h, --help            show this help message and exit
  --ids IDS             UniProt IDs, comma-separated (ex: Q14790)
  --i IFILE             input file, UniProt IDs
  --o OFILE             output (TSV)
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

Example IDs: Q14790,P01116,P01118,A8K8Z5,B0LPF9,Q96D10

```

```
python3 -m BioClients.uniprot.Client getNames --ids Q14790,P01116
```

```
python3 -m BioClients.uniprot.Client getFunctions --ids Q14790,P01116
```
