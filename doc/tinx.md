# `BioClients.tinx`

## TINX

TINX = Target Importance and Novelty Explorer

Developed by and for the Illuminating the Druggable Genome (IDG) 
Knowledge Management Center (KMC).

 * [TIN-X version 3: update with expanded dataset and modernized architecture for enhanced illumination of understudied targets](https://peerj.com/articles/17470/), VT Metzger, et al., PeerJ, 2024. 


### Usage

```
python3 -m BioClients.tinx.Client -h
usage: Client.py [-h] [--ids IDS] [--i IFILE] [--o OFILE]
                 [--query SEARCH_QUERY] [--api_host API_HOST]
                 [--api_base_path API_BASE_PATH] [-v]
                 {get_disease_targets,get_disease_publications,get_target_diseases,get_target_publications,search_diseases,search_targets}

TINX REST API query client

positional arguments:
  {get_disease_targets,get_disease_publications,get_target_diseases,get_target_publications,search_diseases,search_targets}
                        operation

options:
  -h, --help            show this help message and exit
  --ids IDS             UniProt IDs, comma-separated (ex: Q14790)
  --i IFILE             input file, UniProt IDs
  --o OFILE             output (TSV)
  --query SEARCH_QUERY  search query
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

Example IDs: Diseases: DOID:0014667 Targets: 488
```
