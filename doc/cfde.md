# `BioClients.cfde`

##  CFDE

API access for resources of the Common Fund Data Ecosystem (CFDE).

  * <https://nih-cfde.org/>

```
$ python3 -m BioClients.cfde.cfchemdb.Client -h
usage: Client.py [-h] [--i IFILE] [--ids IDS] [--xref_type XREF_TYPE] [--o OFILE]
                 [--dbhost DBHOST] [--dbport DBPORT] [--dbname DBNAME] [--dbusr DBUSR]
                 [--dbpw DBPW] [--param_file PARAM_FILE] [--dbschema DBSCHEMA] [-v] [-q]
                 {list_tables,list_columns,list_tables_rowCounts,version,get_structure,list_structures,list_structures2smiles,meta_listdbs}

CFChemDb PostgreSql client utility

positional arguments:
  {list_tables,list_columns,list_tables_rowCounts,version,get_structure,list_structures,list_structures2smiles,meta_listdbs}
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
  -q, --quiet           Suppress progress notification.
```
