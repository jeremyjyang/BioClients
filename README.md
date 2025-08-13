# `BioClients` <img align="right" src="doc/images/BioClients_logo.png" height="120" alt="BioClients logo">

Python package for access to online biomedical resources,
usually via REST APIs. Modules generally include
`Client.py` for command-line use and `Utils.py` for
integration into other code. With the advent of HTTP web services,
first SOAP/XML and then mostly REST/JSON, many online APIs
require very similar methods for data search, requests
and transforms into usable formats, often TSV.

## Availability and installation

### Installing from PyPI

Releases at <https://pypi.org/project/BioClients/>.

```
pip3 install BioClients
```
However, current development snapshot may included additional functionality.

### Installing from source

Source at <https://github.com/jeremyjyang/BioClients>

___(First download or clone.)___


Install `build` package.

```
python3 -m pip install --upgrade build
```

Install using `build`.  This supercedes the deprecated `setup.py install` and `easy_install` methods.

```
cd BioClients
python3 -m build
```

## Dependencies

* Python 3.10+
* Python packages: `pandas`, `requests`, `yaml`, `psycopg2`, `tqdm`, etc. (See [conda/environment.yml](conda/environment.yml)).

## Modules

 [__Allen__](doc/allen.md) &#8226; [__AMP-T2D__](doc/amp__t2d.md) &#8226; [__Badapple__](doc/badapple.md) &#8226; [__BindingDb__](doc/bindingdb.md) &#8226; [__BioGrid__](doc/biogrid.md) &#8226; [__BiomarkerKB__](doc/biomarkerkb.md) &#8226; [__Bioregistry__](doc/bioregistry.md) &#8226; [__BRENDA__](doc/brenda.md) &#8226; [__CAS__](doc/cas.md) &#8226; [__CDC__](doc/cdc.md) &#8226; [__CFDE__](doc/cfde.md) &#8226; [__Chem2Bio2RDF__](doc/chem2bio2rdf.md) &#8226; [__ChEBI__](doc/chebi.md) &#8226; [__ChEMBL__](doc/chembl.md) &#8226; [__ChemIdPlus__](doc/chemidplus.md) &#8226; [__ClinicalTrials.gov__](doc/clinicaltrials.md) &#8226; [__Disease Ontology__](doc/diseaseontology.md) &#8226; [__DisGeNet__](doc/disgenet.md) &#8226; [__DNorm__](doc/dnorm.md) &#8226; [__DrugCentral__](doc/drugcentral.md) &#8226; [__EMBL-EBI__](doc/emblebi.md) &#8226; [__EnsEMBL__](doc/ensembl.md) &#8226; [__Entrez__](doc/entrez.md) &#8226; [__FDA__](doc/fda.md) &#8226; [__Gene Ontology__](doc/geneontology.md) &#8226; [__GTEx__](doc/gtex.md) &#8226; [__GWAS Catalog__](doc/gwascatalog.md) &#8226; [__HUGO__](doc/hugo.md) &#8226; [__HumanBase__](doc/humanbase.md) &#8226; [__iCite__](doc/icite.md) &#8226; [__IDG__](doc/idg.md) &#8226; [__JensenLab__](doc/jensenlab.md) &#8226; [__LINCS__](doc/lincs.md) &#8226; [__MaayanLab__](doc/maayanlab.md) &#8226; [__Medline__](doc/medline.md) &#8226; [__MeSH__](doc/mesh.md) &#8226; [__MONARCH__](doc/monarch.md) &#8226; [__MyGene__](doc/mygene.md) &#8226; [__NCBO__](doc/ncbo.md) &#8226; [__NCATS__](doc/ncats.md) &#8226; [__OMIM__](doc/omim.md) &#8226; [__OncoTree__](doc/oncotree.md) &#8226; [__Open Targets__](doc/opentargets.md) &#8226; [__Panther__](doc/panther.md) &#8226; [__PDB__](doc/pdb.md) &#8226; [__PubChem__](doc/pubchem.md) &#8226; [__PubMed__](doc/pubmed.md) &#8226; [__PubTator__](doc/pubtator.md) &#8226; [__Reactome__](doc/reactome.md) &#8226; [__RXNorm__](doc/rxnorm.md) &#8226; [__STRINGDB__](doc/stringdb.md) &#8226; [__TCGA__](doc/tcga.md) &#8226; [__UBKG__](doc/ubkg.md) &#8226; [__UMLS__](doc/umls.md) &#8226; [__UniProt__](doc/uniprot.md) &#8226; [__Wikidata__](doc/wikidata.md) &#8226; [__WikiPathways__](doc/wikipathways.md) 

Miscellaneous utilities: [__UTIL__](doc/util.md) 

## Usage Example

```
python3 -m BioClients.pubchem.Client -h
```

## Design pattern

Generally each module includes command-line app `Client.py` which calls 
functions in a corresponding `Utils.py`, providing all capabilities
by import of the module. Command-line apps not API clients are generally 
named `App.py`. Functions can write to an output file
or return a Pandas dataframe (if output file unspecified).

## Data structures and formats, XML, JSON, and TSV

BioClients is designed to be simple and practical, and XML, JSON
and TSV are likewise simple in many respects, yet a great deal
of conceptual and technological progress is reflected. XML and JSON
can represent arbitrarily complex data objects, comprised of nested lists,
dictionaries, and trees of primary types. TSV represents tables of
rows and columns, related by common keys, reflecting the development
of SQL and relational databases. Transforming JSON to TSV, as these
clients generally do, projects data objects to tables useful for many
applications (e.g. machine learning).

## Conda environment

BioClients depends on numerous Python packages.  (See [conda/environment.yml](conda/environment.yml)).
The following commands create and activate a Conda environment `bioclients`:

```
$ conda env create -f conda/environment.yml
```
If that fails, try:
```
$ conda create -n bioclients -c conda-forge pandas readline requests pyyaml tqdm psycopg2 numpy scipy scikit-learn matplotlib
```
then:
```
$ conda activate bioclients
(bioclients) $ pip install BioClients
```
and install additional packages as needed via `pip`, e.g.:
```
(bioclients) $ pip install sqlalchemy
(bioclients) $ pip install pyquery
(bioclients) $ pip install mygene
(bioclients) $ pip install click
(bioclients) $ pip install PyMuPDF
(bioclients) $ pip install py2neo
```

## Venv, etc.

It may not be necessary or advantageous to configure an environment for all of BioClients functionality. Specific modules may be supported with `venv` environments with required dependencies. Module documentation should indicate needed package dependencies.
