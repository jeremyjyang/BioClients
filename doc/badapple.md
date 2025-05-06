# `Badapple`

__Badapple__ : BioAssay Data Associative Promiscuity Prediction Learning Engine

## `Badapple2-API`

Client for the Badapple REST API.

* [Badapple2-API](https://github.com/unmtransinfo/Badapple2-API)
* [Badapple2 API-Docs](https://chiltepin.health.unm.edu/badapple2/apidocs/)

```
python -m BioClients.badapple.Client -h
usage: Client.py [-h] [--smi SMI] [--ids IDS] [--i IFILE]
                 [--db {badapple2,badapple_classic}] [--o OFILE] [--max_rings MAX_RINGS]
                 [--api_host API_HOST] [--api_base_path API_BASE_PATH] [-v]
                 {get_compound2scaffolds,get_scaffold_info,get_scaffold2compounds,get_scaffold2drugs}

Badapple REST API client utility

positional arguments:
  {get_compound2scaffolds,get_scaffold_info,get_scaffold2compounds,get_scaffold2drugs}
                        OPERATION

options:
  -h, --help            show this help message and exit
  --smi SMI             input SMILES
  --ids IDS             input IDs, comma-separated
  --i IFILE             input SMILES file (with optional appended <space>NAME), or input
                        IDs file
  --db {badapple2,badapple_classic}
                        default=badapple2
  --o OFILE             output file (TSV)
  --max_rings MAX_RINGS
                        max rings
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

Example SMILES: OC(=O)C1=C2CCCC(C=C3C=CC(=O)C=C3)=C2NC2=CC=CC=C12 Example scaffold IDs:
46,50
```
