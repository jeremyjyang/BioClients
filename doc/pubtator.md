# `BioClients.pubtator`

# PubTator

PubMed and related NIH literature resources.

* (PubMed)[https://pubmed.ncbi.nlm.nih.gov/]
* (PubTator)[https://www.ncbi.nlm.nih.gov/research/pubtator/]

Pubtator REST API client
<https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/tmTools/RESTfulAPIs.html>
Formats: JSON, PubTator, BioC.

Nomenclatures:
  Gene : NCBI Gene
e.g. <https://www.ncbi.nlm.nih.gov/sites/entrez?db=gene&term=145226>
  Disease : MEDIC (CTD, CTD\_diseases.csv)
e.g. <http://ctdbase.org/basicQuery.go?bqCat=disease&bq=C537775>
  Chemical : MESH
e.g.  <http://www.nlm.nih.gov/cgi/mesh/2014/MB_cgi?field=uid&term=D000596>
  Species : NCBI Taxonomy
e.g.  <https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?name=10090>
  Mutation : tmVar <https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/tutorial/tmVar.html>

NOTE that the API does NOT provide keyword search capability like
webapp <https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/index.cgi>
