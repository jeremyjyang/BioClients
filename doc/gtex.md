# `BioClients.gtex`

## GTEx

GTEx REST API client.

* <https://gtexportal.org>
* <https://www.gtexportal.org/home/api-docs>


## Example commands

```
$ python3 -m BioClients.gtex.Client -h
usage: Client.py [-h] [--ids IDS] [--i IFILE] [--o OFILE] [--dataset DATASET]
                 [--subject SUBJECT] [--skip SKIP] [--nmax NMAX] [--api_host API_HOST]
                 [--api_base_path API_BASE_PATH] [-v]
                 {list_datasets,list_subjects,list_samples,get_gene_expression}

GTEx REST API client

positional arguments:
  {list_datasets,list_subjects,list_samples,get_gene_expression}
                        OPERATION (select one)

options:
  -h, --help            show this help message and exit
  --ids IDS             input IDs
  --i IFILE             input file, IDs
  --o OFILE             output (TSV)
  --dataset DATASET     GTEx datasetId
  --subject SUBJECT     GTEx subjectId
  --skip SKIP
  --nmax NMAX
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose
```
