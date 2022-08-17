# `BioClients.wikidata`

## Wikidata

Wikidata is a collaboratively edited RDF/Sparql knowledge graph
used ___by___ Wikipedia. The structured infobox data in Wikipedia
is from Wikidata. Not to be confused with
[DBPedia](https://en.wikipedia.org/wiki/DBpedia) which is 
built ___from___ Wikipedia.

  * <https://en.wikipedia.org/wiki/Wikidata>

This module provides access to Wikidata Sparql endpoint. Focus on
biomedical entities and particularly GeneWiki.

  * <https://www.wikidata.org>
  * <https://www.wikidata.org/wiki/User:ProteinBoxBot/SPARQL_Examples>

### GeneWiki

  * <https://www.wikidata.org/wiki/Wikidata:WikiProject_Gene_Wiki>
  * <https://github.com/SuLab/genewikiworld>

### Dependencies

  * [WikidataIntegrator](https://github.com/SuLab/WikidataIntegrator)

### Usage

```
$ python3 -m BioClients.wikidata.Client -h
usage: Client.py [-h] [--o OFILE] [--rqfile RQFILE] [--rq RQ] [-v]
                 {query,list_drugTargetPairs,list_geneDiseasePairs}

Wikidata utilities

positional arguments:
  {list_drugTargetPairs,list_geneDiseasePairs,query,test}
                        OPERATION

options:
  -h, --help            show this help message and exit
  --o OFILE             output (TSV)
  --rqfile RQFILE       input Sparql file
  --rq RQ               input Sparql string
  -v, --verbose
```

```
$ python3 -m BioClients.wikidata.Client list_geneDiseasePairs
```
