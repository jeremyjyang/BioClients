# `BioClients.idg`

## IDG - Illuminating the Druggable Genome

* <https://pharos.nih.gov/api>
* <https://druggablegenome.net/>

# `BioClients.idg.pharos`

Access the Pharos GraphQL API.

## Dependencies

  * Python package `python-graphql-client`

```
python3 -m BioClients.idg.pharos.Client -h
usage: Client.py [-h] [--i IFILE] [--ids IDS] [--o OFILE]
                 [--idtype_target {tcrdid,uniprot,sym}]
                 [--idtype_disease {cui,doid,name}] [--nmax NMAX]
                 [--api_endpoint API_ENDPOINT] [-v]
                 {get_targets,get_diseases,test}

Pharos GraphQL API client

positional arguments:
  {get_targets,get_diseases,test}
                        operation

optional arguments:
  -h, --help            show this help message and exit
  --i IFILE             input file, target IDs
  --ids IDS             IDs, target, comma-separated
  --o OFILE             output (TSV)
  --idtype_target {tcrdid,uniprot,sym}
                        target ID type
  --idtype_disease {cui,doid,name}
                        disease ID type
  --nmax NMAX           max to return
  --api_endpoint API_ENDPOINT
  -v, --verbose
```

# `BioClients.idg.tcrd`

Provides access to the TCRD MySql db.

## Dependencies

  * Python package `mysqlclient`

TCRD credentials normally stored in `$HOME/.tcrd.yaml` formatted thus:

```
DBHOST: "tcrd.kmc.io"
DBPORT: 3306
DBNAME: "tcrd660"
DBUSR: "tcrd"
DBPW: ""
```

```
python3 -m BioClients.idg.tcrd.Client -h
usage: Client.py [-h] [--o OFILE] [--i IFILE] [--ids IDS]
                 [--idtype {TID,GENEID,UNIPROT,GENESYMB,ENSP}] [--xreftypes XREFTYPES]
                 [--tdls TDLS] [--tfams TFAMS] [--param_file PARAM_FILE]
                 [--dbhost DBHOST] [--dbport DBPORT] [--dbusr DBUSR] [--dbpw DBPW]
                 [--dbname DBNAME] [-v] [-q]
                 {info,listTables,listColumns,tableRowCounts,tdlCounts,listTargets,listXrefTypes,listXrefs,listDatasets,listTargetsByDTO,listTargetFamilies,listPhenotypes,listPhenotypeTypes,listPublications,getTargets,getTargetsByXref,getTargetPage,listDiseases,listDiseaseTypes,getDiseaseAssociations,getDiseaseAssociationsPage,getTargetpathways}

TCRD MySql client utility

positional arguments:
  {info,listTables,listColumns,tableRowCounts,tdlCounts,listTargets,listXrefTypes,listXrefs,listDatasets,listTargetsByDTO,listTargetFamilies,listPhenotypes,listPhenotypeTypes,listPublications,getTargets,getTargetsByXref,getTargetPage,listDiseases,listDiseaseTypes,getDiseaseAssociations,getDiseaseAssociationsPage,getTargetpathways}
                        OPERATION

optional arguments:
  -h, --help            show this help message and exit
  --o OFILE             output (TSV)
  --i IFILE             input target ID file
  --ids IDS             input IDs
  --idtype {TID,GENEID,UNIPROT,GENESYMB,ENSP}
                        target ID type
  --xreftypes XREFTYPES
                        Xref types, comma-separated
  --tdls TDLS           TDLs, comma-separated (Tdark|Tbio|Tchem|Tclin)
  --tfams TFAMS         target families, comma-separated
  --param_file PARAM_FILE
  --dbhost DBHOST
  --dbport DBPORT
  --dbusr DBUSR
  --dbpw DBPW
  --dbname DBNAME
  -v, --verbose
  -q, --quiet           Suppress progress notification.
```

# `BioClients.idg.tinx`

TIN-X (Target Importance and Novelty Explorer)

* <http://www.newdrugtargets.org>
* <http://api.newdrugtargets.org/docs>

