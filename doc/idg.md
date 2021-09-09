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
                 [--qtype {TID,GENEID,UNIPROT,GENESYMB,NCBI_GI,ENSP}]
                 [--tdl {Tdark,Tbio,Tchem,Tclin}] [--fam FAM] [--param_file PARAM_FILE]
                 [--dbhost DBHOST] [--dbport DBPORT] [--dbusr DBUSR] [--dbpw DBPW]
                 [--dbname DBNAME] [-v]
                 {info,listTables,describeTables,tableRowCounts,tdlCounts,listTargets,listXreftypes,listXrefs,getTargets,getTargetpathways}

TCRD MySql client utility

positional arguments:
  {info,listTables,describeTables,tableRowCounts,tdlCounts,listTargets,listXreftypes,listXrefs,getTargets,getTargetpathways}
                        OPERATION

optional arguments:
  -h, --help            show this help message and exit
  --o OFILE             output (TSV)
  --i IFILE             input ID or query file
  --ids IDS             IDs or queries
  --qtype {TID,GENEID,UNIPROT,GENESYMB,NCBI_GI,ENSP}
                        ID or query type
  --tdl {Tdark,Tbio,Tchem,Tclin}
                        Target Development Level (TDL) Tdark|Tbio|Tchem|Tclin
  --fam FAM             target family GPCR|Kinase|IC|NR|...|Unknown
  --param_file PARAM_FILE
  --dbhost DBHOST
  --dbport DBPORT
  --dbusr DBUSR
  --dbpw DBPW
  --dbname DBNAME
  -v, --verbose
```

# `BioClients.idg.tinx`

TIN-X (Target Importance and Novelty Explorer)

* <http://www.newdrugtargets.org>
* <http://api.newdrugtargets.org/docs>

