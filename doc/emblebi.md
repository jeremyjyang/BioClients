# `BioClients.emblebi`

## EMBL-EBI

Tools for obtaining and processing data from EMBL-EBI resources.
Some EMBL-EBI resources have separate BioClients modules.

* <https://www.ebi.ac.uk/>

### Identifiers

* <https://identifiers.org>
* <https://docs.identifiers.org/articles/api.html>

Examples:

```
$ python3 -m BioClients.emblebi.identifiers.Client -h
usage: Client.py [-h] [--i IFILE] [--o OFILE] [--ids IDS] [--query QUERY]
                 [--resolver_api_host RESOLVER_API_HOST]
                 [--resolver_api_base_path RESOLVER_API_BASE_PATH]
                 [--registry_api_host REGISTRY_API_HOST]
                 [--registry_api_base_path REGISTRY_API_BASE_PATH]
                 [--search_logic {containing,exact}] [-v]
                 {resolve,list_namespaces,list_resources,list_institutions,search_namespaces,search_institutions,search_resources}

EMBL-EBI Identifiers.org client

positional arguments:
  {resolve,list_namespaces,list_resources,list_institutions,search_namespaces,search_institutions,search_resources}
                        OPERATION

optional arguments:
  -h, --help            show this help message and exit
  --i IFILE             Input IDs
  --o OFILE             Output (TSV)
  --ids IDS             Input IDs (comma-separated)
  --query QUERY         Search query.
  --resolver_api_host RESOLVER_API_HOST
  --resolver_api_base_path RESOLVER_API_BASE_PATH
  --registry_api_host REGISTRY_API_HOST
  --registry_api_base_path REGISTRY_API_BASE_PATH
  --search_logic {containing,exact}
  -v, --verbose

Example IDs: taxonomy:9606
```
