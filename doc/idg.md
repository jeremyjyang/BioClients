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

* <https://www.newdrugtargets.org>
* <https://api.newdrugtargets.org/docs>

```
$ python3 -m BioClients.idg.tinx.Client -h
usage: Client.py [-h] [--i IFILE] [--ids IDS] [--disease_ids DISEASE_IDS] [--o OFILE]
                 [--query QUERY] [--api_host API_HOST] [--api_base_path API_BASE_PATH]
                 [-v]
                 {list_diseases,list_targets,list_articles,list_dto,get_disease,get_disease_by_doid,get_disease_targets,get_disease_target_articles,get_target,get_target_by_uniprot,get_target_diseases,get_dto,search_diseases,search_targets,search_articles,search_dtos}

TIN-X (Target Importance and Novelty Explorer) REST API client)

positional arguments:
  {list_diseases,list_targets,list_articles,list_dto,get_disease,get_disease_by_doid,get_disease_targets,get_disease_target_articles,get_target,get_target_by_uniprot,get_target_diseases,get_dto,search_diseases,search_targets,search_articles,search_dtos}
                        operation

optional arguments:
  -h, --help            show this help message and exit
  --i IFILE             input IDs or search terms
  --ids IDS             IDs (comma-separated)
  --disease_ids DISEASE_IDS
                        disease IDs (comma-separated), needed ONLY if BOTH target and
                        disease IDs specified
  --o OFILE             output (TSV)
  --query QUERY         search query
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

Example IDs: 5391 (disease); DOID:9297 (DOID); 12203 (target); Q9H4B4 (UniProt);
--disease_ids needed ONLY if BOTH target and disease IDs specified, such as for
get_disease_target_articles.
```

# `BioClients.idg.tiga`

TIGA (Target Illumination GWAS Analytics)

* <https://unmtid-shinyapps.net/shiny/tiga/>

```
$ python3 -m BioClients.idg.tiga.Client -h
usage: Client.py [-h] [--o OFILE] [--igene IFILEGENE] [--itrait IFILETRAIT]
                 [--geneIds GENEIDS] [--traitIds TRAITIDS] [--param_file PARAM_FILE]
                 [--dbhost DBHOST] [--dbport DBPORT] [--dbusr DBUSR] [--dbpw DBPW]
                 [--dbname DBNAME] [-v] [-q]
                 {info,listGenes,listTraits,getTraitAssociations,getGeneAssociations,getGeneTraitAssociations,getGeneTraitProvenance}

TIGA/TCRD MySql client utility

positional arguments:
  {info,listGenes,listTraits,getTraitAssociations,getGeneAssociations,getGeneTraitAssociations,getGeneTraitProvenance}
                        OPERATION

optional arguments:
  -h, --help            show this help message and exit
  --o OFILE             output (TSV)
  --igene IFILEGENE     input gene ID file
  --itrait IFILETRAIT   input trait ID file
  --geneIds GENEIDS     input IDs, genes (ENSG)
  --traitIds TRAITIDS   input IDs, traits (EFO)
  --param_file PARAM_FILE
                        default param_file: /home/jjyang/.tcrd.yaml
  --dbhost DBHOST
  --dbport DBPORT
  --dbusr DBUSR
  --dbpw DBPW
  --dbname DBNAME
  -v, --verbose
  -q, --quiet           Suppress progress notification.

Example IDs: EFO_0004541, ENSG00000160785, ENSG00000215021
```
