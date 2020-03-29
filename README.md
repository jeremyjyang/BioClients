# BioClients

Python package for access to online biomedical resources,
usually via REST APIs. Modules generally include
`Client.py` for command-line use and `Utils.py` for
integration into other code.

## Dependencies

* Python3

## Modules

`biogrid`, `brenda`, `chembl`, `diseaseontology`, `disgenet`, `dnorm`, `ensembl`, `fda`, `geneontology`, `gwascatalog`, `hugo`, `humanbase`, `icite`, `mesh`, `omim`, `opentargets`, `pdb`, `pubchem`, `pubmed`, `pubtator`, `reactome`, `rxnorm`, `stringdb`, `umls`, `uniprot`

## Usage

```
$ python3 -m BioClients.stringdb.Client -h

usage: Client.py [-h] [--id ID] [--ids IDS] [--idfile IDFILE] [--o OFILE]
                 [--species SPECIES] [--minscore MINSCORE]
                 [--netflavor {evidence,confidence,actions}]
                 [--imgfmt {image,highres_image,svg}] [--api_host API_HOST]
                 [--api_base_path API_BASE_PATH] [-v]
                 {getIds,getInteractionPartners,getNetwork,getNetworkImage,getEnrichment,getPPIEnrichment,getInteractors,getActions,getAbstracts}

STRING-DB REST API client utility

positional arguments:
  {getIds,getInteractionPartners,getNetwork,getNetworkImage,getEnrichment,getPPIEnrichment,getInteractors,getActions,getAbstracts}
                        operation

optional arguments:
  -h, --help            show this help message and exit
  --id ID               protein ID (ex:DRD1_HUMAN)
  --ids IDS             protein IDs, comma-separated
  --idfile IDFILE       input file, protein IDs
  --o OFILE             output file
  --species SPECIES     taxon code, ex: 9606 (human)
  --minscore MINSCORE   signifcance threshold 0-1000
  --netflavor {evidence,confidence,actions}
                        network flavor
  --imgfmt {image,highres_image,svg}
                        image format
  --api_host API_HOST
  --api_base_path API_BASE_PATH
  -v, --verbose

Example protein IDs: DRD1 DRD1_HUMAN DRD2 DRD2_HUMAN ; Example species: 9606 (human, via taxon identifiers, http://www.uniprot.org/taxonomy) ; Image formats: PNG PNG_highres SVG ; MAY BE DEPRECATED: getInteractors, getActions, getAbstracts
```

##  UMLS

From the NIH National Library of Medicine (NLM).

* Registration is required for both browser and API access.  See
<https://www.nlm.nih.gov/research/umls/>. To use
[BioClients.umls.Client](BioClients/umls/Client.py), create `~/.umls.yaml` with
format:

```
API_KEY: "===REPLACE-WITH-KEY-HERE==="
```

##  RxNorm

From the NIH National Library of Medicine (NLM).

* <https://www.nlm.nih.gov/research/umls/rxnorm/>

##  MeSH

From the NIH National Library of Medicine (NLM).
Currently XML processing tools only.

* <https://meshb.nlm.nih.gov/>

## PubChem

Tools for obtaining and processing PubChem data (REST, SOAP, FTP).

## ChEMBL

Tools for obtaining and processing ChEMBL data.

* https://www.ebi.ac.uk/chembl/
* https://chembl.gitbook.io/chembl-interface-documentation/web-services
* https://chembl.gitbook.io/chembl-interface-documentation/downloads
