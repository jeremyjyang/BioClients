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

Operations available include:

* list_products - List all drug products.
* list_structures - List all drug structures.
* list_structures2smiles - List all drug structures as SMILES file.
* list_structures2molfile - List all drug structures as MDL molfile.
* list_active_ingredients - List all active ingredients.
* list_indications - List all indications.
* list_ddis - List all drug-drug interactions.
* get_structure - Get structure by struct_id.
* get_structure_by_synonym - Get structure by synonym.
* get_structure_ids - Get all IDs for structures.
* get_structure_products - Get all products for structures.
* get_structure_atcs - Get all ATC classes for structures.
* get_product - Get product by product_id.
* get_product_structures - Get structures for product.
* get_indication_structures - Get all structures for indication.
* search_indications - Search indications by regular expression.
* search_products - Search products by regular expression.

All results are TSV format except as noted.


### Usage

```
$ python3 -m BioClients.drugcentral.Client -h
usage: Client.py [-h] [--i IFILE] [--ids IDS] [--o OFILE] [--dbhost DBHOST]
                 [--dbport DBPORT] [--dbname DBNAME] [--dbusr DBUSR]
                 [--dbpw DBPW] [--param_file PARAM_FILE] [--dbschema DBSCHEMA]
                 [-v]
                 {describe, counts, version, get_structure, get_structure_by_synonym, get_structure_ids, get_structure_products, get_structure_atcs, get_product, get_product_structures, get_indication_structures, list_products, list_structures, list_structures2smiles, list_structures2molfile, list_active_ingredients, list_indications, list_ddis, search_indications, search_products, meta_listdbs}

DrugCentral PostgreSql client utility

positional arguments:
  {describe, counts, version, get_structure, get_structure_by_synonym, get_structure_ids, get_structure_products, get_structure_atcs, get_product, get_product_structures, get_indication_structures, list_products, list_structures, list_structures2smiles, list_structures2molfile, list_active_ingredients, list_indications, list_ddis, search_indications, search_products, meta_listdbs}
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

