# `BioClients.pubmed`

## PubMed

* (PubMed)[https://pubmed.ncbi.nlm.nih.gov/]
* <https://www.ncbi.nlm.nih.gov/pmc/tools/developers/>
* <https://www.ncbi.nlm.nih.gov/pmc/tools/get-metadata/>

### PubMed Web Services Client

`get_record` returns selected fields: title, abstract, firstAuthorLastName, journal, and year.

```
$ python3 -m BioClients.pubmed.Client -h
usage: Client.py [-h] [--i IFILE] [--ids IDS] [--o OFILE] [--api_host API_HOST]
                 [--api_base_path API_BASE_PATH] [--skip SKIP] [--nmax NMAX] [-q] [-v]
                 {get_esummary,get_record}

PubMed webservices client

positional arguments:
  {get_esummary,get_record}
                        OPERATION

options:
  -h, --help            show this help message and exit
  --i IFILE             input IDs file (PMIDs)
  --ids IDS             input IDs (PMIDs) (comma-separated)
  --o OFILE             output (usually TSV)
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  --skip SKIP
  --nmax NMAX
  -q, --quiet           Suppress progress notification.
  -v, --verbose
```

### PubMed XML Processing App

Parse, process Entrez PubMed XML (summaries or full), normally obtained via
Entrez eUtils, eDirect CLI or Perl API.

Note that other Entrez XML (e.g. PubChem) very similar.

```
$ python3 -m BioClients.pubmed.App_XML -h
usage: App_XML.py [-h] --i IFILE [--ids IDS] [--idfile IDFILE] [--nmax NMAX] [--o OFILE]
                  [--odir ODIR] [-v]
                  {summary2tsv,summary2abstract,full2tsv,full2abstract,full2authorlist}

process PubMed XML (summaries or full), typically obtained via Entrez eUtils.

positional arguments:
  {summary2tsv,summary2abstract,full2tsv,full2abstract,full2authorlist}
                        operation

options:
  -h, --help            show this help message and exit
  --i IFILE             input file, XML
  --ids IDS             PubMed IDs, comma-separated (ex:25533513)
  --idfile IDFILE       input file, PubMed IDs
  --nmax NMAX           max to return
  --o OFILE             output (TSV)
  --odir ODIR           output directory
  -v, --verbose
```
