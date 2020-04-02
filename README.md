# BioClients

Python package for access to online biomedical resources,
usually via REST APIs. Modules generally include
`Client.py` for command-line use and `Utils.py` for
integration into other code.

## Dependencies

* Python3

## Modules

`biogrid`, `brenda`, `chembl`, `diseaseontology`, `disgenet`, `dnorm`, `ensembl`, `fda`, `geneontology`, `gwascatalog`, `hugo`, `humanbase`, `icite`, `lincs`, `mesh`, `omim`, `opentargets`, `pdb`, `pubchem`, `pubmed`, `pubtator`, `reactome`, `rxnorm`, `stringdb`, `umls`, `uniprot`

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

### Usage examples

```
python3 -m BioClients.rxnorm.Client -h
python3 -m BioClients.rxnorm.Client list_sourcetypes
python3 -m BioClients.rxnorm.Client list_relationtypes
python3 -m BioClients.rxnorm.Client list_termtypes
python3 -m BioClients.rxnorm.Client list_propnames
python3 -m BioClients.rxnorm.Client list_propcategories
python3 -m BioClients.rxnorm.Client list_idtypes
python3 -m BioClients.rxnorm.Client list_class_types
python3 -m BioClients.rxnorm.Client list_classes
python3 -m BioClients.rxnorm.Client list_classes --class_types 'MESHPA,ATC1-4'
```

Requiring names:

```
python3 -m BioClients.rxnorm.Client get_name --ids "prozac,tamiflu"
python3 -m BioClients.rxnorm.Client get_name2rxcui --ids "prozac,tamiflu"
```

Requiring external IDs:
```
python3 -m BioClients.rxnorm.Client get_id2rxcui --ids "C2709711" --idtype UMLSCUI
```

Requiring RxCUI IDs:
```
python3 -m BioClients.rxnorm.Client get_rxcui_status --ids "131725,213269"
python3 -m BioClients.rxnorm.Client get_rxcui_properties --ids "131725,213269"
python3 -m BioClients.rxnorm.Client get_rxcui_ndcs --ids "131725,213269"
python3 -m BioClients.rxnorm.Client get_rxcui_allrelated --ids "131725,213269"
```

##  MeSH

From the NIH National Library of Medicine (NLM).
Currently XML processing tools only.

* <https://meshb.nlm.nih.gov/>

## PubChem

Tools for obtaining and processing PubChem data (REST, SOAP, FTP).

```
python3 -m BioClients.pubchem.Client --name remdesivir name2sid
python3 -m BioClients.pubchem.Client --name remdesivir name2cid
```

## ChEMBL

Tools for obtaining and processing ChEMBL data.

* https://www.ebi.ac.uk/chembl/
* https://chembl.gitbook.io/chembl-interface-documentation/web-services
* https://chembl.gitbook.io/chembl-interface-documentation/downloads

# PubMed, PubTator, iCite

PubMed and related NIH literature resources.

* (PubMed)[https://pubmed.ncbi.nlm.nih.gov/]
* (iCite)[https://icite.od.nih.gov/]
* (PubTator)[https://www.ncbi.nlm.nih.gov/research/pubtator/]
