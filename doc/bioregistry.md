# `BioClients.bioregistry`

## Bioregistry

* <https://bioregistry.io/>
* <https://bioregistry.io/apidocs/>

```
$ python3 -m BioClients.bioregistry.Client -h
usage: Client.py [-h] [--i IFILE] [--ids IDS] [--o OFILE] [--etype ETYPE]
                 [--prefix PREFIX] [--nchunk NCHUNK] [--nmax NMAX] [--skip SKIP]
                 [--api_host API_HOST] [--api_base_path API_BASE_PATH] [-v]
                 {list_collections,list_contexts,list_registry,list_metaregistry,list_contributors,get_reference}

Bioregistry REST API client

positional arguments:
  {list_collections,list_contexts,list_registry,list_metaregistry,list_contributors,get_reference}
                        operation

options:
  -h, --help            show this help message and exit
  --i IFILE             input query IDs
  --ids IDS             input query IDs (comma-separated)
  --o OFILE             output (TSV)
  --etype ETYPE         evidence codes (|-separated)
  --prefix PREFIX       CURIE prefix
  --nchunk NCHUNK
  --nmax NMAX
  --skip SKIP
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose
```
