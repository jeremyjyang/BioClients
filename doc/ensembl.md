# `BioClients.ensembl`

## EnsEMBL

Access to Ensembl REST API.

 * <http://rest.ensembl.org/documentation/info/lookup>

Including Variant Effect Predictor (VEP):

 * <https://useast.ensembl.org/info/docs/tools/vep/index.html>
 * <https://rest.ensembl.org/#VEP>

## `BioClients.ensembl.biomart`

Also, the BIOMART ID mapping service.

 * <https://m.ensembl.org/info/data/biomart/biomart_restful.html>

```
$ python3 -m BioClients.ensembl.Client -h
usage: Client.py [-h] [--ids IDS]
       [--i IFILE]
       [--api_host API_HOST]
       [--api_base_path API_BASE_PATH]
       [--o OFILE]
       [--skip SKIP]
       [--nmax NMAX] [-v] [-q]
       {list_species,get_xrefs,get_info,get_vep,show_version}

Ensembl REST API client

positional arguments:
  {list_species,get_xrefs,get_info,get_vep,show_version}
                        operation

options:
  -h, --help            show this help message and exit
  --ids IDS             Ensembl_IDs, comma-separated (ex:ENSG00000000003), or SNP IDs,
                        comma-separated (ex:rs56116432)
  --i IFILE             input file, Ensembl IDs or SNP IDs
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  --o OFILE             output (TSV)
  --skip SKIP
  --nmax NMAX
  -v, --verbose
  -q, --quiet

Example IDs: ENSG00000157764, ENSG00000160785
```
