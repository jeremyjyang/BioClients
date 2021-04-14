# `BioClients.gwascatalog`

## GWAS Catalog

GWAS Catalog REST API client.

* <https://www.ebi.ac.uk/gwas/docs/api>
* <https://www.ebi.ac.uk/gwas/rest/api>
* <https://www.ebi.ac.uk/gwas/rest/docs/api>
* <https://www.ebi.ac.uk/gwas/rest/docs/sample-scripts>


## Example commands

```
python3 -m BioClients.gwascatalog.Client list_studies --o gwascatalog_studies.tsv
```

```
python3 -m BioClients.gwascatalog.Client search_studies --searchtype efotrait --ids "Worry measurement"
```

```
python3 -m BioClients.gwascatalog.Client get_studyAssociations --ids "GCST004364,GCST000227"
```

```
python3 -m BioClients.gwascatalog.Client get_snps --ids "rs6085920,rs2273833,rs6684514,rs144991356"
```
