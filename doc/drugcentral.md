# BioClients

## DrugCentral (`drugcentral.org`)

[DrugCentral](http://drugcentral.org) is a widely used research database of
approved drugs, active pharmaceutical ingredients and clinical products,
with indications, side effects, molecular mechanism of action targets,
and much more.  Developed, curated, and maintained by Tudor Oprea, Oleg Ursu,
Jayme Holmes and coworkers as a key resource for the NIH Illuminating the
Druggable Genome (IDG) project.

DrugCentral employs a backend PostgreSql db, freely available at
<http://drugcentral.org/download>. The BioClients API provides
programmatic access to an available db instance, which may be deployed
locally, or may be available publicly with configuration details
at <http://drugcentral.org> (this service in beta at time of writing).

### Usage

```
$ python3 -m BioClients.drugcentral.Client -h
usage: Client.py [-h] [--i IFILE] [--ids IDS] [--o OFILE] [--dbhost DBHOST]
                 [--dbport DBPORT] [--dbname DBNAME] [--dbusr DBUSR]
                 [--dbpw DBPW] [--param_file PARAM_FILE] [--dbschema DBSCHEMA]
                 [-v]
                 {describe,counts,version,get_structure,get_structure_by_synonym,get_structure_by_indication,get_structure_ids,get_structure_products,get_product,get_product_structures,get_indication_structures,list_products,list_structures,list_structures2smiles,list_structures2molfile,list_active_ingredients,list_indications,search_indications,search_products}

DrugCentral PostgreSql client utility

positional arguments:
  {describe,counts,version,get_structure,get_structure_by_synonym,get_structure_by_indication,get_structure_ids,get_structure_products,get_product,get_product_structures,get_indication_structures,list_products,list_structures,list_active_ingredients,list_indications,search_indications,search_products}
                        operation

optional arguments:
  -h, --help            show this help message and exit
  --i IFILE             input ID file
  --ids IDS             input IDs (comma-separated)
  --o OFILE             output (TSV)
  --dbhost DBHOST
  --dbport DBPORT
  --dbname DBNAME
  --dbusr DBUSR
  --dbpw DBPW
  --param_file PARAM_FILE
  --dbschema DBSCHEMA
  -v, --verbose

Search via --ids as regular expressions, e.g. "^Alzheimer"
```

### Database credentials

Db credentials are normally stored in a configuration file at
`$HOME/.drugcentral.yaml`.

