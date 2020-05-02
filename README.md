# `BioClients` <img align="right" src="/doc/images/BioClients_logo.png" height="120" alt="BioClients logo">

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

 [__AMP-T2D__](doc/amp__t2d.md) &#8226;  [__BioGrid__](doc/biogrid.md) &#8226;  [__BRENDA__](doc/brenda.md) &#8226;  [__Chem2Bio2RDF__](doc/chem2bio2rdf.md) &#8226;  [__ChEMBL__](doc/chembl.md) &#8226; [__Disease Ontology__](doc/diseaseontology.md) &#8226;  [__DisGeNet__](doc/disgenet.md) &#8226;  [__DNorm__](doc/dnorm.md) &#8226;  [__DrugCentral__](doc/drugcentral.md) &#8226;  [__EnsEMBL__](doc/ensembl.md) &#8226;  [__FDA__](doc/fda.md) &#8226;  [__Gene Ontology__](doc/geneontology.md) &#8226;  [__GWAS Catalog__](doc/gwascatalog.md) &#8226;  [__HUGO__](doc/hugo.md) &#8226;  [__HumanBase__](doc/humanbase.md) &#8226;  [__iCite__](doc/icite.md) &#8226;  [__IDG__](doc/idg.md) &#8226; [__JensenLab__](doc/jensenlab.md) &#8226; [__LINCS__](doc/lincs.md) &#8226; [__MaayanLab__](doc/maayanlab.md) 
&#8226; [__MeSH__](doc/mesh.md) &#8226;  [__MONARCH__](doc/monarch.md) &#8226;  [__OMIM__](doc/omim.md) &#8226;  [__Open Targets__](doc/opentargets.md) &#8226;  [__Panther__](doc/panther.md) &#8226;  [__PDB__](doc/pdb.md) &#8226;  [__PubChem__](doc/pubchem.md) &#8226;  [__PubMed__](doc/pubmed.md) &#8226;  [__PubTator__](doc/pubtator.md) &#8226;  [__Reactome__](doc/reactome.md) &#8226;  [__RXNorm__](doc/rxnorm.md) &#8226;  [__STRINGDB__](doc/stringdb.md) &#8226; [__TCGA__](doc/tcga.md) &#8226; [__TIN-X__](doc/tinx.md) &#8226; [__UMLS__](doc/umls.md) &#8226;  [__UniProt__](doc/uniprot.md) 

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
