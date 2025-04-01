# `BioClients.ubkg`

## UBKG - Unified Biomedical Knowledge Graph

Client to the UBKG REST API. Note that an UMLS API Key is required for access
to UBKG.

* [Smart-API:UBKG-API](https://smart-api.info/ui/96e5b5c0b0efeef5b93ea98ac2794837)
* [NIH-NLM UMLS Terminology Services](https://uts.nlm.nih.gov/uts/)

The Unified Biomedical Knowledge Graph (UBKG) was developed by the University of
Pittsburgh, Children's Hospital of Philadelphia, and others, built upon the NIH-NLM
Unified Medical Language System (UMLS) metathesaurus, composed of numerous leading,
community standard controlled vocabularies.

The Data Distillery Knowledge Graph (DDKG) is a context and extension of UBKG, developed
by the Common Fund Data Ecosystem (CFDE) Data Distillery Partnership Project team,
including the IDG DCC team at UNM.

```
python -m BioClients.ubkg.Client -h
usage: Client.py [-h] [--o OFILE] [--i IFILE] [--ids IDS] [--term TERM] [--sab SAB]
                 [--relationship RELATIONSHIP]
                 [--context {base_context,data_distillery_context,hubmap_sennet_context}]
                 [--mindepth MINDEPTH] [--maxdepth MAXDEPTH] [--nmax NMAX] [--skip SKIP]
                 [--api_host API_HOST] [--api_base_path API_BASE_PATH]
                 [--api_key API_KEY] [--param_file PARAM_FILE] [-v]
                 {search,info,list_relationship_types,list_node_types,list_node_type_counts,list_property_types,list_sabs,list_sources,list_semantic_types,get_concept2codes,get_concept2concepts,get_concept2definitions,get_concept2paths,get_concept2trees,get_term2concepts}

UBKG REST API client

positional arguments:
  {search,info,list_relationship_types,list_node_types,list_node_type_counts,list_property_types,list_sabs,list_sources,list_semantic_types,get_concept2codes,get_concept2concepts,get_concept2definitions,get_concept2paths,get_concept2trees,get_term2concepts}
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
  --context {base_context,data_distillery_context,hubmap_sennet_context}
  --mindepth MINDEPTH   min path depth
  --maxdepth MAXDEPTH   max path depth
  --nmax NMAX           max records
  --skip SKIP           skip 1st SKIP queries
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  --api_key API_KEY     UMLS API Key
  --param_file PARAM_FILE
  -v, --verbose

```
