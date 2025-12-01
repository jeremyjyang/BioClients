# `BioClients.chebi`

## ChEBI

ChEBI REST API client

Tools for obtaining and processing ChEBI data.
Chemical Entities of Biological Interest (ChEBI) is a freely available dictionary of molecular entities focused on ‘small’ chemical compounds.

* <https://www.ebi.ac.uk/chebi/>
* <https://www.ebi.ac.uk/chebi/backend/api/docs/>

```
 python -m BioClients.chebi.Client -h
usage: Client.py [-h] [--ids IDS] [--i IFILE] [--o OFILE] [--query QUERY]
                 [--skip SKIP] [--nmax NMAX] [--api_host API_HOST]
                 [--api_base_path API_BASE_PATH] [-v]
                 {list_sources,get_entity,get_entity_names,get_entity_chemical_data,get_entity_secondary_ids,get_entity_children,get_entity_parents,get_entity_origins,search}

ChEBI REST API client

positional arguments:
  {list_sources,get_entity,get_entity_names,get_entity_chemical_data,get_entity_secondary_ids,get_entity_children,get_entity_parents,get_entity_origins,search}
                        OPERATION (select one)

options:
  -h, --help            show this help message and exit
  --ids IDS             input IDs
  --i IFILE             input file, IDs
  --o OFILE             output (TSV)
  --query QUERY         search query (SMILES)
  --skip SKIP
  --nmax NMAX
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

Example entity IDs: 16737, 30273,33246,24433
```
