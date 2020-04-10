# BioClients

Python package for access to online biomedical resources,
usually via REST APIs. Modules generally include
`Client.py` for command-line use and `Utils.py` for
integration into other code. With the advent of HTTP web services,
first SOAP/XML and then mostly REST/JSON, many online APIs
require very similar methods for data search, requests
and transforms into usable formats, often CSV/TSV.

## Availability and installation

Source at <https://github.com/jeremyjyang/BioClients>.
Latest numbered release available via `pypi.org`:
<https://pypi.org/project/BioClients/>.
However, currently development snapshot recommended.

```
$ pip3 install BioClients
```

## Dependencies

* Python 3.6+
* Python packages: `pandas`, `requests`, `json`, `xml`, etc.

## Modules

| [BioGrid](doc/biogrid.md) | [BRENDA](doc/brenda.md) | [ChEMBL](doc/chembl.md) |[Disease Ontology](doc/diseaseontology.md) | [DisGeNet](doc/disgenet.md)
|:--:|:--:|:--:|:--:|:--:|
| [DNorm](doc/dnorm.md) | [EnsEMBL](doc/ensembl.md) | [FDA](doc/fda.md) | [Gene Ontology](doc/geneontology.md) | [GWAS Catalog](doc/gwascatalog.md)
| [HUGO](doc/hugo.md) | [HumanBase](doc/humanbase.md) | [iCite](doc/icite.md) | [LINCS](doc/lincs.md) | [MeSH](doc/mesh.md)
| [OMIM](doc/omim.md) | [Open Targets](doc/opentargets.md) | [PDB](doc/pdb.md) | [PubChem](doc/pubchem.md) | [PubMed](doc/pubmed.md)
| [PubTator](doc/pubtator.md) | [Reactome](doc/reactome.md) | [RXNorm](doc/rxnorm.md) | [STRINGDB](doc/stringdb.md) | [UMLS](doc/umls.md)
| [UniProt](doc/uniprot.md)

## Usage

```
$ python3 -m BioClients.pubchem.Client -h
```
