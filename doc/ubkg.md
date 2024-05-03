# `BioClients.ubkg`

## UBKG - Unified Biomedical Knowledge Graph

Client to the DDKG-UBKG REST API.

* [Smart-API:UBKG-API](https://smart-api.info/ui/55be2831c69b17f6bc975ddb58cabb5e)

The Data Distillery Knowledge Graph (DDKG) is an extension and instance of the
Unified Biomedical Knowledge Graph (UBKG), developed by the University of
Pittsburgh, Children's Hospital of Philadelphia, and the Common Fund Data
Ecosystem (CFDE) Data Distillery Partnership Project.


```
python3 -m BioClients.ubkg.Client -h
usage: Client.py [-h] [--o OFILE] [--i IFILE] [--ids IDS] [--term TERM]
                 [--sab SAB] [--relationship RELATIONSHIP]
                 [--mindepth MINDEPTH] [--maxdepth MAXDEPTH] [--nmax NMAX]
                 [--skip SKIP] [--api_host API_HOST]
                 [--api_base_path API_BASE_PATH] [--api_key API_KEY] [-v]
                 {search,info,list_relationship_types,list_node_types,list_node_type_counts,list_property_types,list_sabs,list_semantic_types,get_concept2codes,get_concept2concepts,get_concept2definitions,get_concept2paths,get_concept2trees,get_term2concepts}

UBKG REST API client

positional arguments:
  {search,info,list_relationship_types,list_node_types,list_node_type_counts,list_property_types,list_sabs,list_semantic_types,get_concept2codes,get_concept2concepts,get_concept2definitions,get_concept2paths,get_concept2trees,get_term2concepts}
                        OPERATION

options:
  -h, --help            show this help message and exit
  --o OFILE             output (TSV)
  --i IFILE             UMLS CUI ID file
  --ids IDS             UMLS CUI IDs, comma-separated
  --term TERM           UMLS term, e.g. 'Asthma'
  --sab SAB             Standard abbreviation type
  --relationship RELATIONSHIP
                        Relationship type
  --mindepth MINDEPTH   min path depth
  --maxdepth MAXDEPTH   max path depth
  --nmax NMAX           max records
  --skip SKIP           skip 1st SKIP queries
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  --api_key API_KEY
  -v, --verbose

The Data Distillery Knowledge Graph (DDKG) is an extension and instance of the
Unified Biomedical Knowledge Graph (UBKG), developed by the University of
Pittsburgh, Children's Hospital of Philadelphia, and the Common Fund Data
Ecosystem (CFDE) Data Distillery Partnership Project.
```
