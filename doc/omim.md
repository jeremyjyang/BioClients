# `BioClients.omim`

## OMIM

Online Mendelian Inheritance in Man,
"An Online Catalog of Human Genes and Genetic Disorders"

See: <https://omim.org/help/api>

The OMIM API URLs are organized in a very simple fashion:
   /api/[handler]?[parameters]
   /api/[handler]/[component]?[parameters]
   /api/[handler]/[action]?[parameters]
The handler refers to the data object, such as an entry or a clinical synopsis.

Handlers: entry, clinicalSynopsis, geneMap, search, html, dump
