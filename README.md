# BioClients

Python package for access to online biomedical resources,
usually via REST APIs. Modules generally include
`Client.py` for command-line use and `Utils.py` for
integration into other code. With the advent of HTTP web services,
first SOAP/XML and then mostly REST/JSON, many online APIs
require very similar methods for data search, requests
and transforms into usable formats, often CSV/TSV.

## Availability and installation

Source at <https://github.com/jeremyjyang/BioClients>;
releases available via `pypi.org`:
<https://pypi.org/project/BioClients/>
(`pip3 install BioClients`).

However, current development snapshot recommended.

___(First download or clone.)___
```
$ cd BioClients
$ python3 setup.py install
```

## Dependencies

* Python 3.6+
* Python packages: `pandas`, `requests`, `urllib`, `json`, `xml`, etc.

## Modules

| | | | | |
|:--:|:--:|:--:|:--:|:--:|
| [BioGrid](doc/biogrid.md) | [BRENDA](doc/brenda.md) | [ChEMBL](doc/chembl.md) |[Disease Ontology](doc/diseaseontology.md) | [DisGeNet](doc/disgenet.md)
| [DNorm](doc/dnorm.md) | [DrugCentral](doc/drugcentral.md) | [EnsEMBL](doc/ensembl.md) | [FDA](doc/fda.md) | [Gene Ontology](doc/geneontology.md)
| [GWAS Catalog](doc/gwascatalog.md) | [HUGO](doc/hugo.md) | [HumanBase](doc/humanbase.md) | [iCite](doc/icite.md) | [IDG](doc/idg.md)
| [LINCS](doc/lincs.md) | [MeSH](doc/mesh.md) | [OMIM](doc/omim.md) | [Open Targets](doc/opentargets.md) | [Panther](doc/panther.md)
| [PDB](doc/pdb.md) | [PubChem](doc/pubchem.md) | [PubMed](doc/pubmed.md) | [PubTator](doc/pubtator.md) | [Reactome](doc/reactome.md)
| [RXNorm](doc/rxnorm.md) | [STRINGDB](doc/stringdb.md) | [TIN-X](doc/tinx.md) | [UMLS](doc/umls.md) | [UniProt](doc/uniprot.md)

## Usage

```
$ python3 -m BioClients.pubchem.Client -h
```

## Data structures and formats, XML, JSON, and CSV/TSV

BioClients is designed to be simple and practical, and XML, JSON
and CSV/TSV are likewise simple in many respects, yet a great deal
of conceptual and technological progress is reflected. XML and JSON
can represent arbitrarily complex data objects, comprised of nested lists,
dictionaries, and trees of primary types. CSV/TSV represents tables of
rows and columns, the relational db view, flattened as needed for many
applications (e.g. ML) but related by common keys. Transforming REST JSON
results to CSV/TSV, as these clients generally do, projects data structures
to tables useful for many applications.
