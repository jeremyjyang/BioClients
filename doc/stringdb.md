# `BioClients.stringdb`

## STRINGDB

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

