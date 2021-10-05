# `BioClients.drugcentral`

## DrugCentral (`drugcentral.org`)

[DrugCentral](https://drugcentral.org) is a widely used research database of
approved drugs, active pharmaceutical ingredients and clinical products,
with indications, side effects, molecular mechanism of action targets,
and much more.  Developed, curated, and maintained by Tudor Oprea, Oleg Ursu,
Jayme Holmes and coworkers as a key resource for the NIH Illuminating the
Druggable Genome (IDG) project.

DrugCentral employs a backend PostgreSql db, freely available at
<https://drugcentral.org/download>. The BioClients API provides
programmatic access to an available db instance, which may be deployed
locally, or may be available publicly with configuration details
at <https://drugcentral.org> (this service in beta at time of writing, 
available at: dbhost=unmtid-dbs.net, dbport=5433, dbname=drugcentral,
dbuser=drugman, dbpw=dosage).

Operations include:

* __list_products__ - List all drug products.
* __list_structures__ - List all drug structures.  
* __list_structures2smiles__ - List all drug structures as SMILES file.
* __list_structures2molfile__ - List all drug structures as MDL molfile.
* __list_active_ingredients__ - List all active ingredients.
* __list_indications__ - List all indications.
* __list_xref_types__ - List all xref types.
* __list_ddis__ - List all drug-drug interactions.
* __get_structure__ - Get structure by struct_id.
* __get_structure_by_synonym__ - Get structure by synonym.
* __get_structure_by_xref__ - Get structure by xref ID.
* __get_structure_xrefs__ - Get all xref IDs for structures.
* __get_structure_products__ - Get all products for structures.
* __get_structure_atcs__ - Get all ATC classes for structures.
* __get_product__ - Get product by product_id.
* __get_product_structures__ - Get structures for product.
* __get_indication_structures__ - Get all structures for indication (OMOP ID).
* __get_drugpage__ - Get drug (structure), with products, xrefs, etc. as JSON.
* __search_indications__ - Search indications by regular expression.
* __search_products__ - Search products by regular expression.

All results are TSV format except as noted.


### Usage

```
$ python3 -m BioClients.drugcentral.Client -h
usage: Client.py [-h] [--i IFILE] [--ids IDS] [--xref_type XREF_TYPE] [--o OFILE]
                 [--dbhost DBHOST] [--dbport DBPORT] [--dbname DBNAME] [--dbusr DBUSR]
                 [--dbpw DBPW] [--param_file PARAM_FILE] [--dbschema DBSCHEMA] [-v]
                 {list_tables,list_columns,list_tables_rowCounts,version,get_structure,get_structure_by_synonym,get_structure_by_xref,get_structure_xrefs,get_structure_products,get_structure_orangebook_products,get_structure_atcs,get_structure_synonyms,get_product,get_product_structures,get_indication_structures,get_drugpage,list_products,list_structures,list_structures2smiles,list_structures2molfile,list_active_ingredients,list_indications,list_indication_targets,list_ddis,list_atcs,list_xrefs,list_xref_types,search_indications,search_products,meta_listdbs}

DrugCentral PostgreSql client utility

positional arguments:
  {list_tables,list_columns,list_tables_rowCounts,version,get_structure,get_structure_by_synonym,get_structure_by_xref,get_structure_xrefs,get_structure_products,get_structure_orangebook_products,get_structure_atcs,get_structure_synonyms,get_product,get_product_structures,get_indication_structures,get_drugpage,list_products,list_structures,list_structures2smiles,list_structures2molfile,list_active_ingredients,list_indications,list_indication_targets,list_ddis,list_atcs,list_xrefs,list_xref_types,search_indications,search_products,meta_listdbs}
                        OPERATION (select one)

optional arguments:
  -h, --help            show this help message and exit
  --i IFILE             input ID file
  --ids IDS             input IDs (comma-separated)
  --xref_type XREF_TYPE
                        xref ID type
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
`$HOME/.drugcentral.yaml`, formatted thus:

```
DBHOST: "====Replace_with_HOST===="
DBPORT: "====Replace_with_PORT===="
DBNAME: "====Replace_with_NAME===="
DBUSR:  "====Replace_with_USERNAME===="
DBPW:   "====Replace_with_PASSWORD===="
```

